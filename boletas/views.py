from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from .models import Boleta
from usuarios.models import Usuario
from consumos.models import Consumo
import json
from xhtml2pdf import pisa
from django.shortcuts import render
from django.http import HttpResponse

@login_required
def imprimir_boleta(request, boleta_id):
    """
    Muestra una vista imprimible de la boleta en el navegador con un gráfico de consumo histórico.
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)
    usuario = boleta.usuario

    # Obtener consumos históricos del usuario
    consumos_historicos = Consumo.objects.filter(usuario=usuario).order_by('fecha_consumo')
    labels = [c.fecha_consumo.strftime('%Y-%m') for c in consumos_historicos]
    valores = [float(c.cantidad_consumida) for c in consumos_historicos]

    # Datos del gráfico
    grafico_consumo_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Consumo Mensual (m³)',
            'data': valores,
            'borderColor': 'rgba(75, 192, 192, 1)',
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'tension': 0.4
        }]
    }

    contexto = {
        'boleta': boleta,
        'usuario': usuario,
        'grafico_consumo_data': grafico_consumo_data,
    }
    return render(request, 'boletas/imprimir_boleta.html', contexto)

# 1. Historial de Boletas Recientes
@login_required
def historial_recientes(request):
    """
    Muestra el historial de las boletas más recientes.
    """
    boletas = Boleta.objects.select_related('usuario').order_by('-fecha_emision')[:50]
    return render(request, 'boletas/historial_recientes.html', {'boletas': boletas})

# 2. Buscar Usuarios para ver Boletas
@login_required
def buscar_usuario(request):
    """
    Muestra un formulario para buscar usuarios y listar sus boletas.
    """
    query = request.GET.get('search', '')  # Obtén el valor de búsqueda
    if query:
        usuarios = Usuario.objects.filter(nombre__icontains=query).order_by('nombre')  # Filtra por nombre
    else:
        usuarios = Usuario.objects.all().order_by('nombre')  # Lista todos los usuarios si no hay búsqueda

    return render(request, 'boletas/buscar_usuario.html', {'usuarios': usuarios, 'query': query})


# 3. Historial de Boletas por Usuario
@login_required
def historial_usuario(request, usuario_id):
    """
    Muestra el historial de boletas de un usuario específico.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    boletas = Boleta.objects.filter(usuario=usuario).order_by('-fecha_emision')
    return render(request, 'boletas/historial_usuario.html', {'usuario': usuario, 'boletas': boletas})

# 4. Seleccionar Usuario para Generar Boleta
@login_required
def seleccionar_usuario(request):
    """
    Muestra una lista de usuarios con consumos registrados para seleccionar quién recibirá una boleta.
    """
    query = request.GET.get('search', '')
    usuarios = Usuario.objects.filter(consumo__isnull=False).distinct()

    if query:
        usuarios = usuarios.filter(nombre__icontains=query)

    return render(request, 'boletas/seleccionar_usuario.html', {'usuarios': usuarios})

# 5. Seleccionar Consumos para Generar Boleta
from django.contrib.messages import get_messages

@login_required
def seleccionar_consumos(request, usuario_id):
    """
    Permite seleccionar los consumos inicial y final para generar una boleta.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    consumos = Consumo.objects.filter(usuario=usuario).order_by('fecha_consumo')

    if request.method == 'POST':
        consumo_inicio_id = request.POST.get('consumo_inicio')
        consumo_fin_id = request.POST.get('consumo_fin')

        if consumo_inicio_id and consumo_fin_id:
            consumo_inicio = get_object_or_404(Consumo, id=consumo_inicio_id)
            consumo_fin = get_object_or_404(Consumo, id=consumo_fin_id)

            if consumo_fin.fecha_consumo < consumo_inicio.fecha_consumo:
                messages.error(request, "La fecha de consumo final no puede ser anterior a la inicial.", extra_tags='seleccionar_consumos')
            elif consumo_fin.id == consumo_inicio.id:
                messages.error(request, "El consumo inicial y final no pueden ser iguales.", extra_tags='seleccionar_consumos')
            else:
                return redirect(
                    'boletas:generar_boleta',
                    usuario_id=usuario.id,
                    consumo_inicio_id=consumo_inicio.id,
                    consumo_fin_id=consumo_fin.id
                )

    # Filtrar solo mensajes de esta vista
    relevant_messages = [
        message for message in get_messages(request)
        if 'seleccionar_consumos' in message.extra_tags
    ]

    return render(request, 'boletas/seleccionar_consumos.html', {
        'usuario': usuario,
        'consumos': consumos,
        'messages': relevant_messages
    })

# 6. Generar Boleta
@login_required
def generar_boleta(request, usuario_id, consumo_inicio_id, consumo_fin_id):
    """
    Genera una nueva boleta basada en los consumos seleccionados.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    consumo_inicio = get_object_or_404(Consumo, id=consumo_inicio_id)
    consumo_fin = get_object_or_404(Consumo, id=consumo_fin_id)

    # Validaciones adicionales
    if consumo_inicio.id == consumo_fin.id:
        messages.error(request, "El consumo inicial y final no pueden ser iguales.")
        return redirect('boletas:seleccionar_consumos', usuario_id=usuario.id)

    if consumo_fin.fecha_consumo < consumo_inicio.fecha_consumo:
        messages.error(request, "La fecha del consumo final no puede ser anterior a la del consumo inicial.")
        return redirect('boletas:seleccionar_consumos', usuario_id=usuario.id)

    # Creación de la boleta
    boleta, created = Boleta.objects.get_or_create(
        usuario=usuario,
        consumo_inicio=consumo_inicio,
        consumo_fin=consumo_fin
    )

    if created:
        consumo_total = consumo_fin.cantidad_consumida - consumo_inicio.cantidad_consumida
        tarifa_base = consumo_inicio.tarifa_aplicada.valor

        if consumo_total <= 10:
            total_a_pagar = tarifa_base
        elif consumo_total <= 15:
            total_a_pagar = tarifa_base + 1000
        else:
            total_a_pagar = tarifa_base + 1000 + (1000 * (consumo_total - 15))

        boleta.consumo_total = consumo_total
        boleta.tarifa_base = tarifa_base
        boleta.total_a_pagar = total_a_pagar
        boleta.save()

    return redirect('boletas:historial_usuario', usuario_id=usuario.id)


# 7. Descargar PDF
def descargar_pdf(request, boleta_id):
    """
    Genera un PDF de la boleta.
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)
    usuario = boleta.usuario

    consumos_historicos = Consumo.objects.filter(usuario=usuario).order_by('fecha_consumo')
    labels = [c.fecha_consumo.strftime('%Y-%m') for c in consumos_historicos]
    valores = [float(c.cantidad_consumida) for c in consumos_historicos]

    grafico_consumo_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Consumo Mensual (m³)',
            'data': valores,
            'borderColor': 'rgba(75, 192, 192, 1)',
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
        }]
    }

    html_content = render_to_string('boletas/boleta_pdf.html', {
        'usuario': usuario,
        'boleta': boleta,
        'grafico_consumo_data': grafico_consumo_data,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boleta_{boleta.id}.pdf"'

    pisa.CreatePDF(html_content, dest=response)
    return response

# 8. Confirmar y Cambiar Estado de Boleta
@login_required
def actualizar_estado_boleta(request, boleta_id):
    """
    Cambia el estado de una boleta (Pendiente -> Pagado o viceversa).
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)

    if request.method == 'POST':
        boleta.pagado = not boleta.pagado
        boleta.save()
        messages.success(request, f"El estado de la boleta #{boleta.id} se actualizó correctamente.")
        return redirect('boletas:historial_recientes')

    return render(request, 'boletas/confirmar_estado.html', {'boleta': boleta})

# 9. Confirmar y Eliminar Boleta
@login_required
def confirmar_eliminar_boleta(request, boleta_id):
    """
    Muestra una página de confirmación antes de eliminar una boleta.
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)

    if request.method == 'POST':
        boleta.delete()
        messages.success(request, f"Boleta {boleta_id} eliminada exitosamente.")
        return redirect('boletas:historial_recientes')

    return render(request, 'boletas/confirmar_eliminar.html', {'boleta': boleta})

@login_required
def eliminar_boleta(request, boleta_id):
    """
    Elimina una boleta después de confirmar la acción.
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)

    if request.method == 'POST':
        boleta.delete()
        messages.success(request, f"La boleta #{boleta_id} ha sido eliminada exitosamente.")
        return redirect('boletas:historial_recientes')

    return render(request, 'boletas/confirmar_eliminar.html', {'boleta': boleta})
