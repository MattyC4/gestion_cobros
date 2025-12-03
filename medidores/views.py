from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

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
    Vista para buscar usuarios y mostrar el estado de sus medidores, con paginación.
    """
    query = request.GET.get('q', '').strip()

    if query:
        usuarios_qs = Usuario.objects.filter(nombre__icontains=query)
    else:
        usuarios_qs = Usuario.objects.all()

    # Paginación: 10 usuarios por página
    paginator = Paginator(usuarios_qs.order_by('nombre'), 10)
    page_number = request.GET.get('page')
    usuarios_page = paginator.get_page(page_number)

    context = {
        'usuarios': usuarios_page,
        'query': query,
        'is_paginated': usuarios_page.has_other_pages(),
    }

    return render(request, 'medidores/buscar_usuario_para_medidor.html', context)


@login_required
@verificar_permiso(['admin', 'operario'])
def asignar_medidor_usuario(request, usuario_id):
    """
    Vista para asignar un medidor a un usuario específico.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Validación: solo un medidor activo por usuario
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
        'usuario': usuario,
    })


@login_required
@verificar_permiso(['admin', 'operario'])
def historial_medidores(request):
    """
    Vista para mostrar el historial de medidores con paginación y métricas.
    """
    query = request.GET.get('q', '').strip()

    medidores_qs = Medidor.objects.select_related('usuario').order_by('-fecha_registro')

    if query:
        medidores_qs = medidores_qs.filter(
            Q(codigo_serial__icontains=query) |
            Q(usuario__nombre__icontains=query) |
            Q(usuario__rut__icontains=query)
        )

    paginator = Paginator(medidores_qs, 10)  # 10 medidores por página
    page_number = request.GET.get('page')
    medidores_page = paginator.get_page(page_number)

    # Métricas para tarjetas
    total_medidores = Medidor.objects.count()
    medidores_activos = Medidor.objects.filter(estado='activo').count()
    medidores_inactivos = Medidor.objects.filter(estado='inactivo').count()
    medidores_mantencion = Medidor.objects.filter(estado='mantenimiento').count()
    medidores_danados = Medidor.objects.filter(estado='danado').count()

    medidores_asignados = Medidor.objects.filter(usuario__isnull=False).count()
    medidores_sin_asignar = total_medidores - medidores_asignados

    context = {
        'medidores': medidores_page,
        'query': query,
        'is_paginated': medidores_page.has_other_pages(),
        'total_medidores': total_medidores,
        'medidores_activos': medidores_activos,
        'medidores_inactivos': medidores_inactivos,
        'medidores_mantencion': medidores_mantencion,
        'medidores_danados': medidores_danados,
        'medidores_asignados': medidores_asignados,
        'medidores_sin_asignar': medidores_sin_asignar,
    }

    return render(request, 'medidores/historial_medidores.html', context)


@login_required
@verificar_permiso(['admin'])
def eliminar_medidor(request, medidor_id):
    """
    Vista para eliminar un medidor.
    """
    medidor = get_object_or_404(Medidor, id=medidor_id)

    if request.method == 'POST':
        codigo = medidor.codigo_serial
        medidor.delete()
        messages.success(request, f"Medidor {codigo} eliminado exitosamente.")
        return redirect('medidores:historial_medidores')

    return render(request, 'medidores/eliminar_medidor.html', {
        'medidor': medidor,
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
            messages.success(
                request,
                f"Estado del medidor {medidor.codigo_serial} actualizado a {medidor.get_estado_display()}."
            )
            return redirect('medidores:historial_medidores')
        else:
            messages.error(request, "Estado inválido seleccionado.")

    return render(request, 'medidores/confirmar_cambio_estado.html', {
        'medidor': medidor,
        'estados': Medidor.ESTADOS,
    })
