from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from usuarios.models import Usuario
from medidores.models import Medidor
from tarifas.models import Tarifa
from .models import Consumo
from django.contrib.auth.decorators import login_required


@login_required
def lista_usuarios(request):
    """
    Vista para listar los usuarios con medidores asignados.
    """
    if request.user.rol not in ['admin', 'operario']:
        messages.error(request, "No tienes permiso para acceder a esta función.")
        return redirect('roles:redireccion_dashboard')

    query = request.GET.get('search', '')
    usuarios = Usuario.objects.filter(medidores__isnull=False).distinct()

    if query:
        usuarios = usuarios.filter(nombre__icontains=query)

    return render(request, 'consumos/lista_usuarios.html', {'usuarios': usuarios})


@login_required
def registrar_consumo(request, usuario_id):
    """
    Vista para registrar consumo de un usuario.
    """
    if request.user.rol not in ['admin', 'operario']:
        messages.error(request, "No tienes permiso para acceder a esta función.")
        return redirect('roles:redireccion_dashboard')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    medidor = usuario.medidores.filter(estado='activo').first()
    tarifa = Tarifa.objects.filter(activo=True).first()

    if not medidor:
        messages.error(request, "El usuario no tiene un medidor activo asignado.")
        return redirect('consumos:lista_usuarios')

    if not tarifa:
        messages.error(request, "No hay tarifas activas disponibles para registrar el consumo.")
        return redirect('consumos:lista_usuarios')

    if request.method == 'POST':
        cantidad_consumida = request.POST.get('cantidad_consumida')
        fecha_consumo = request.POST.get('fecha_consumo')

        consumo = Consumo(
            usuario=usuario,
            medidor=medidor,
            tarifa_aplicada=tarifa,
            cantidad_consumida=cantidad_consumida,
            fecha_consumo=fecha_consumo
        )
        try:
            consumo.full_clean()  # Valida el objeto antes de guardar
            consumo.save()  # Guarda el registro de consumo
            messages.success(request, "Consumo registrado exitosamente.")
            return redirect('consumos:lista_usuarios_consumos')
        except ValidationError as e:
            for error in e.message_dict.values():
                messages.error(request, error)

    return render(request, 'consumos/registrar_consumo.html', {
        'usuario': usuario,
        'medidor': medidor,
        'tarifa': tarifa
    })


@login_required
def lista_usuarios_consumos(request):
    """
    Vista para listar usuarios que tienen consumos registrados.
    """
    if request.user.rol not in ['admin', 'operario']:
        messages.error(request, "No tienes permiso para acceder a esta función.")
        return redirect('roles:redireccion_dashboard')

    query = request.GET.get('search', '')
    usuarios = Usuario.objects.filter(consumo__isnull=False).distinct()

    if query:
        usuarios = usuarios.filter(nombre__icontains=query)

    return render(request, 'consumos/lista_usuarios_consumos.html', {'usuarios': usuarios})


@login_required
def historial_consumos(request, usuario_id):
    """
    Vista para ver el historial de consumos de un usuario específico.
    """
    if request.user.rol not in ['admin', 'operario']:
        messages.error(request, "No tienes permiso para acceder a esta función.")
        return redirect('roles:redireccion_dashboard')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    consumos = Consumo.objects.filter(usuario=usuario).select_related('medidor', 'tarifa_aplicada').order_by('-fecha_consumo')

    return render(request, 'consumos/historial_consumos.html', {
        'usuario': usuario,
        'consumos': consumos
    })


@login_required
def eliminar_consumo(request, consumo_id):
    """
    Vista para eliminar un registro de consumo.
    """
    if request.user.rol not in ['admin', 'operario']:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('roles:redireccion_dashboard')

    consumo = get_object_or_404(Consumo, id=consumo_id)

    if request.method == 'POST':
        usuario_id = consumo.usuario.id
        consumo.delete()
        messages.success(request, "El registro de consumo ha sido eliminado exitosamente.")
        return redirect('consumos:historial_consumos', usuario_id=usuario_id)

    return render(request, 'consumos/eliminar_consumo.html', {'consumo': consumo})
