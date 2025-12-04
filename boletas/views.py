from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages

from usuarios.models import Usuario



from .models import Boleta
from usuarios.models import Usuario
from consumos.models import Consumo

from xhtml2pdf import pisa


# ================================
#  Helper de permisos por rol
# ================================
def verificar_permiso(roles_permitidos):
    """
    Decorador para verificar que el usuario tenga uno de los roles permitidos.
    """
    def decorador(vista):
        def _wrapped(request, *args, **kwargs):
            if not hasattr(request.user, "rol") or request.user.rol not in roles_permitidos:
                messages.error(request, "No tienes permiso para acceder a esta sección de boletas.")
                return redirect("roles:redireccion_dashboard")
            return vista(request, *args, **kwargs)
        return _wrapped
    return decorador


# ================================
# 1. Vista imprimible en HTML
# ================================
@login_required
@verificar_permiso(["admin", "secretaria"])
def imprimir_boleta(request, boleta_id):
    """
    Muestra una vista imprimible de la boleta en el navegador con un gráfico de consumo histórico.
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)
    usuario = boleta.usuario

    # Obtener consumos históricos del usuario
    consumos_historicos = Consumo.objects.filter(usuario=usuario).order_by("fecha_consumo")
    labels = [c.fecha_consumo.strftime("%Y-%m") for c in consumos_historicos]
    valores = [float(c.cantidad_consumida) for c in consumos_historicos]

    grafico_consumo_data = {
        "labels": labels,
        "datasets": [{
            "label": "Consumo Mensual (m³)",
            "data": valores,
            "borderColor": "rgba(75, 192, 192, 1)",
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "tension": 0.4,
        }],
    }

    contexto = {
        "boleta": boleta,
        "usuario": usuario,
        "grafico_consumo_data": grafico_consumo_data,
    }
    return render(request, "boletas/imprimir_boleta.html", contexto)


# ================================
# 2. Historial de boletas recientes
# ================================
@login_required
@verificar_permiso(["admin", "secretaria"])
def historial_recientes(request):
    """
    Muestra el historial de las boletas más recientes.
    """
    boletas = (
        Boleta.objects
        .select_related("usuario")
        .order_by("-fecha_emision")[:50]
    )
    return render(request, "boletas/historial_recientes.html", {"boletas": boletas})


# ================================
# 3. Buscar usuarios para ver boletas
# ================================
@login_required
@verificar_permiso(["admin", "secretaria"])
def buscar_usuario(request):
    query = request.GET.get('search', '').strip()
    usuarios_qs = Usuario.objects.all().order_by('nombre')

    if query:
        usuarios_qs = usuarios_qs.filter(nombre__icontains=query)

    paginator = Paginator(usuarios_qs, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'usuarios': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_usuarios': paginator.count,
        'query': query,
    }
    return render(request, 'boletas/buscar_usuario.html', context)


# ================================
# 4. Historial de boletas por usuario
# ================================
@login_required
@verificar_permiso(["admin", "secretaria"])
def historial_usuario(request, usuario_id):
    """
    Muestra el historial de boletas de un usuario específico.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    boletas = Boleta.objects.filter(usuario=usuario).order_by("-fecha_emision")

    if not boletas.exists():
        messages.info(request, f"El usuario {usuario.nombre} aún no tiene boletas generadas.")

    return render(
        request,
        "boletas/historial_usuario.html",
        {"usuario": usuario, "boletas": boletas},
    )


# ================================
# 5. Seleccionar usuario para generar boleta
# ================================
@login_required
@verificar_permiso(["admin", "secretaria"])
def seleccionar_usuario(request):
    """
    Lista usuarios que tienen consumos registrados para generar boletas,
    mostrando la fecha del último consumo como información contextual.
    """
    if request.user.rol not in ['admin', 'secretaria']:
        messages.error(request, "No tienes permiso para generar boletas.")
        return redirect('roles:redireccion_dashboard')

    # Texto de búsqueda
    search = request.GET.get('search', '').strip()

    # Usuarios con consumos + fecha del último consumo
    usuarios = (
        Usuario.objects
        .filter(consumo__isnull=False)
        .annotate(
            ultimo_consumo=Max('consumo__fecha_consumo')
        )
        .order_by('nombre')
        .distinct()
    )

    # Filtro por búsqueda
    if search:
        usuarios = usuarios.filter(
            models.Q(nombre__icontains=search) |
            models.Q(rut__icontains=search)
        )

    return render(request, 'boletas/seleccionar_usuario.html', {
        'usuarios': usuarios,
        'search': search,
        'total_usuarios': usuarios.count()
    })



# ================================
# 6. Seleccionar consumos para generar boleta
# ================================
from django.contrib.messages import get_messages  # lo dejamos aquí como ya lo usabas


@login_required
@verificar_permiso(["admin", "secretaria"])
def seleccionar_consumos(request, usuario_id):
    """
    Permite seleccionar los consumos inicial y final para generar una boleta.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    consumos = Consumo.objects.filter(usuario=usuario).order_by("fecha_consumo")

    # Si el usuario tiene menos de 2 consumos, no se puede generar boleta
    if consumos.count() < 2:
        messages.warning(
            request,
            "Este usuario aún no tiene suficientes consumos para generar una boleta "
            "(se requieren al menos 2 lecturas)."
        )
        return redirect("boletas:seleccionar_usuario")

    if request.method == "POST":
        consumo_inicio_id = request.POST.get("consumo_inicio")
        consumo_fin_id = request.POST.get("consumo_fin")

        if not consumo_inicio_id or not consumo_fin_id:
            messages.error(
                request,
                "Debes seleccionar un consumo inicial y uno final.",
                extra_tags="seleccionar_consumos",
            )
        else:
            consumo_inicio = get_object_or_404(Consumo, id=consumo_inicio_id)
            consumo_fin = get_object_or_404(Consumo, id=consumo_fin_id)

            if consumo_fin.fecha_consumo < consumo_inicio.fecha_consumo:
                messages.error(
                    request,
                    "La fecha de consumo final no puede ser anterior a la inicial.",
                    extra_tags="seleccionar_consumos",
                )
            elif consumo_fin.id == consumo_inicio.id:
                messages.error(
                    request,
                    "El consumo inicial y final no pueden ser iguales.",
                    extra_tags="seleccionar_consumos",
                )
            else:
                return redirect(
                    "boletas:generar_boleta",
                    usuario_id=usuario.id,
                    consumo_inicio_id=consumo_inicio.id,
                    consumo_fin_id=consumo_fin.id,
                )

    # Filtrar solo mensajes de esta vista (por extra_tags)
    relevant_messages = [
        message for message in get_messages(request)
        if "seleccionar_consumos" in getattr(message, "extra_tags", "")
    ]

    return render(
        request,
        "boletas/seleccionar_consumos.html",
        {
            "usuario": usuario,
            "consumos": consumos,
            "messages": relevant_messages,
        },
    )


# ================================
# 7. Generar boleta
# ================================
@login_required
@verificar_permiso(["admin", "secretaria"])
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
        return redirect("boletas:seleccionar_consumos", usuario_id=usuario.id)

    if consumo_fin.fecha_consumo < consumo_inicio.fecha_consumo:
        messages.error(
            request,
            "La fecha del consumo final no puede ser anterior a la del consumo inicial."
        )
        return redirect("boletas:seleccionar_consumos", usuario_id=usuario.id)

    # Crear o recuperar boleta
    boleta, created = Boleta.objects.get_or_create(
        usuario=usuario,
        consumo_inicio=consumo_inicio,
        consumo_fin=consumo_fin,
    )

    consumo_total = consumo_fin.cantidad_consumida - consumo_inicio.cantidad_consumida
    tarifa_base = consumo_inicio.tarifa_aplicada.valor

    # Regla de negocio actual (la mantengo tal cual)
    if consumo_total <= 10:
        total_a_pagar = tarifa_base
    elif consumo_total <= 15:
        total_a_pagar = tarifa_base + 1000
    else:
        total_a_pagar = tarifa_base + 1000 + (1000 * (consumo_total - 15))

    # Actualizamos siempre por si cambia la tarifa o se re-calcula
    boleta.consumo_total = consumo_total
    boleta.tarifa_base = tarifa_base
    boleta.total_a_pagar = total_a_pagar
    boleta.save()

    if created:
        messages.success(
            request,
            f"Boleta creada correctamente para {usuario.nombre}."
        )
    else:
        messages.info(
            request,
            f"La boleta ya existía, se recalcularon los montos con la información actual."
        )

    return redirect("boletas:historial_usuario", usuario_id=usuario.id)


# ================================
# 8. Descargar PDF
# ================================
@login_required
@verificar_permiso(["admin", "secretaria"])
def descargar_pdf(request, boleta_id):
    """
    Genera un PDF de la boleta.
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)
    usuario = boleta.usuario

    consumos_historicos = Consumo.objects.filter(usuario=usuario).order_by("fecha_consumo")
    labels = [c.fecha_consumo.strftime("%Y-%m") for c in consumos_historicos]
    valores = [float(c.cantidad_consumida) for c in consumos_historicos]

    grafico_consumo_data = {
        "labels": labels,
        "datasets": [{
            "label": "Consumo Mensual (m³)",
            "data": valores,
            "borderColor": "rgba(75, 192, 192, 1)",
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
        }],
    }

    html_content = render_to_string(
        "boletas/boleta_pdf.html",
        {
            "usuario": usuario,
            "boleta": boleta,
            "grafico_consumo_data": grafico_consumo_data,
        },
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="boleta_{boleta.id}.pdf"'

    pisa.CreatePDF(html_content, dest=response)
    return response


# ================================
# 9. Actualizar estado (pagado / pendiente)
# ================================
@login_required
@verificar_permiso(["admin", "secretaria"])
def actualizar_estado_boleta(request, boleta_id):
    """
    Cambia el estado de una boleta (Pendiente -> Pagado o viceversa).
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)

    if request.method == "POST":
        boleta.pagado = not boleta.pagado
        boleta.save()
        estado = "pagado" if boleta.pagado else "pendiente"
        messages.success(
            request,
            f"El estado de la boleta #{boleta.id} se actualizó a {estado}."
        )
        return redirect("boletas:historial_recientes")

    return render(request, "boletas/confirmar_estado.html", {"boleta": boleta})


# ================================
# 10. Confirmar y eliminar boleta
# ================================
@login_required
@verificar_permiso(["admin", "secretaria"])
def confirmar_eliminar_boleta(request, boleta_id):
    """
    Muestra una página de confirmación antes de eliminar una boleta.
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)

    if request.method == "POST":
        boleta.delete()
        messages.success(request, f"Boleta #{boleta_id} eliminada exitosamente.")
        return redirect("boletas:historial_recientes")

    return render(request, "boletas/confirmar_eliminar.html", {"boleta": boleta})


# Alias opcional si ya tienes una URL antigua apuntando aquí
@login_required
@verificar_permiso(["admin", "secretaria"])
def eliminar_boleta(request, boleta_id):
    """
    Alias de confirmar_eliminar_boleta para compatibilidad con URLs existentes.
    """
    return confirmar_eliminar_boleta(request, boleta_id)
