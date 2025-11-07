from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Medidor
from usuarios.models import Usuario
from .forms import MedidorForm

# Decorador para verificar roles permitidos
def verificar_permiso(roles_permitidos):
    """
    Decorador para verificar permisos basados en roles.
    """
    def decorador(vista):
        def _verificar_permiso(request, *args, **kwargs):
            if request.user.rol not in roles_permitidos:
                messages.error(request, "No tienes permiso para acceder a esta función.")
                return redirect('roles:redireccion_dashboard')
            return vista(request, *args, **kwargs)
        return _verificar_permiso
    return decorador

@login_required
@verificar_permiso(['admin', 'operario'])
def buscar_usuario_para_medidor(request):
    """
    Vista para buscar usuarios y mostrar el estado de sus medidores.
    """
    query = request.GET.get('q', '')
    usuarios = Usuario.objects.filter(nombre__icontains=query) if query else Usuario.objects.all()
    return render(request, 'medidores/buscar_usuario_para_medidor.html', {
        'usuarios': usuarios,
        'query': query
    })

@login_required
@verificar_permiso(['admin', 'operario'])
def asignar_medidor_usuario(request, usuario_id):
    """
    Vista para asignar un medidor a un usuario específico.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if usuario.medidores.filter(estado='activo').exists():
        messages.warning(request, f"El usuario {usuario.nombre} ya tiene un medidor activo asignado.")
        return redirect('medidores:buscar_usuario_para_medidor')

    if request.method == 'POST':
        form = MedidorForm(request.POST, usuario=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Medidor asignado exitosamente a {usuario.nombre}.")
            return redirect('medidores:buscar_usuario_para_medidor')
        else:
            messages.error(request, "Error al asignar el medidor. Revisa los datos ingresados.")
    else:
        form = MedidorForm(usuario=usuario)

    return render(request, 'medidores/asignar_medidor_usuario.html', {
        'form': form,
        'usuario': usuario
    })

@login_required
@verificar_permiso(['admin', 'operario'])
def historial_medidores(request):
    """
    Vista para mostrar el historial de medidores.
    """
    medidores = Medidor.objects.select_related('usuario').order_by('-fecha_registro')
    return render(request, 'medidores/historial_medidores.html', {
        'medidores': medidores
    })

@login_required
@verificar_permiso(['admin'])
def eliminar_medidor(request, medidor_id):
    """
    Vista para eliminar un medidor.
    """
    medidor = get_object_or_404(Medidor, id=medidor_id)

    if request.method == 'POST':
        medidor.delete()
        messages.success(request, f"Medidor {medidor.codigo_serial} eliminado exitosamente.")
        return redirect('medidores:historial_medidores')

    return render(request, 'medidores/eliminar_medidor.html', {
        'medidor': medidor
    })

@login_required
@verificar_permiso(['admin', 'operario'])
def confirmar_cambio_estado(request, medidor_id):
    """
    Vista para confirmar el cambio de estado de un medidor.
    """
    medidor = get_object_or_404(Medidor, id=medidor_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in dict(Medidor.ESTADOS).keys():
            medidor.estado = nuevo_estado
            medidor.save()
            messages.success(request, f"Estado del medidor {medidor.codigo_serial} actualizado a {medidor.get_estado_display()}.")
            return redirect('medidores:historial_medidores')
        else:
            messages.error(request, "Estado inválido seleccionado.")

    return render(request, 'medidores/confirmar_cambio_estado.html', {
        'medidor': medidor,
        'estados': Medidor.ESTADOS
    })
