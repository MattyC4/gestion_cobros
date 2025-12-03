from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Tarifa
from .forms import TarifaForm


@login_required
def agregar_tarifa(request):
    """
    Vista para agregar una nueva tarifa.
    Solo accesible para usuarios autenticados con rol administrador.
    - Usa la fecha de vigencia enviada desde el formulario (si existe).
    - Desactiva tarifas activas anteriores y cierra su fecha de vigencia.
    """
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permiso para agregar tarifas.")
        return redirect('tarifas:historial_tarifas')

    if request.method == 'POST':
        form = TarifaForm(request.POST)
        if form.is_valid():
            try:
                nueva_tarifa = form.save(commit=False)

                # Si el formulario no trae fecha_vigencia, usar la fecha de hoy
                if not nueva_tarifa.fecha_vigencia:
                    nueva_tarifa.fecha_vigencia = timezone.now().date()

                # Desactivar tarifas activas anteriores y cerrar vigencia
                Tarifa.objects.filter(activo=True).update(
                    activo=False,
                    fecha_fin_vigencia=nueva_tarifa.fecha_vigencia
                )

                # Activar la nueva tarifa
                nueva_tarifa.activo = True
                nueva_tarifa.save()

                messages.success(request, "Tarifa agregada y activada exitosamente.")
                return redirect('tarifas:historial_tarifas')

            except ValueError as e:
                form.add_error(None, str(e))
        else:
            messages.error(request, "Revisa los datos ingresados en el formulario.")
    else:
        form = TarifaForm()

    # Si algún día quisieras mostrar el formulario en página aparte,
    # usarías este render. Hoy lo estás usando desde un modal en historial.
    return render(request, 'tarifas/agregar_tarifa.html', {'form': form})


@login_required
def historial_tarifas(request):
    """
    Vista para mostrar el historial de tarifas.
    Accesible para administradores y secretarias.
    """
    if request.user.rol not in ['admin', 'secretaria']:
        messages.error(request, "No tienes permiso para ver el historial de tarifas.")
        return redirect('roles:redireccion_dashboard')

    tarifas = Tarifa.objects.order_by('-fecha_vigencia')  # más reciente primero
    tarifa_activa = Tarifa.objects.filter(activo=True).order_by('-fecha_vigencia').first()

    context = {
        'tarifas': tarifas,
        'tarifa_activa': tarifa_activa,
    }
    return render(request, 'tarifas/historial_tarifas.html', context)


@login_required
def editar_tarifa(request, tarifa_id):
    """
    Vista para editar una tarifa existente.
    Solo accesible para usuarios administradores.
    Ojo: editar tarifas históricas puede afectar cómo se interpretan consumos pasados.
    """
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permiso para editar tarifas.")
        return redirect('tarifas:historial_tarifas')

    tarifa = get_object_or_404(Tarifa, id=tarifa_id)

    if request.method == 'POST':
        form = TarifaForm(request.POST, instance=tarifa)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Tarifa actualizada correctamente.")
                return redirect('tarifas:historial_tarifas')
            except ValueError as e:
                form.add_error(None, str(e))
        else:
            messages.error(request, "Revisa los datos ingresados en el formulario.")
    else:
        form = TarifaForm(instance=tarifa)

    return render(request, 'tarifas/editar_tarifa.html', {'form': form, 'tarifa': tarifa})


@login_required
def confirmar_eliminacion_tarifa(request, tarifa_id):
    """
    Vista para confirmar la eliminación de una tarifa.
    Solo accesible para administradores.
    """
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permiso para eliminar tarifas.")
        return redirect('tarifas:historial_tarifas')

    tarifa = get_object_or_404(Tarifa, id=tarifa_id)

    if request.method == 'POST':
        valor_str = f"${tarifa.valor}"  # guardamos antes por si acaso
        tarifa.delete()
        messages.success(request, f"La tarifa de {valor_str} fue eliminada correctamente.")
        return redirect('tarifas:historial_tarifas')

    return render(request, 'tarifas/confirmar_eliminacion_tarifa.html', {'tarifa': tarifa})
