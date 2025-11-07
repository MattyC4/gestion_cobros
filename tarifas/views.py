from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Tarifa
from .forms import TarifaForm


@login_required
def agregar_tarifa(request):
    """
    Vista para agregar una nueva tarifa. Solo accesible para usuarios autenticados con permisos de administrador.
    """
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permiso para agregar tarifas.")
        return redirect('tarifas:historial_tarifas')

    if request.method == 'POST':
        form = TarifaForm(request.POST)
        if form.is_valid():
            try:
                nueva_tarifa = form.save(commit=False)
                nueva_tarifa.fecha_vigencia = timezone.now().date()
                nueva_tarifa.activo = True
                nueva_tarifa.save()
                messages.success(request, "Tarifa agregada y activada exitosamente.")
                return redirect('tarifas:historial_tarifas')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = TarifaForm()

    return render(request, 'tarifas/agregar_tarifa.html', {'form': form})


@login_required
def historial_tarifas(request):
    """
    Vista para mostrar el historial de tarifas. Accesible para administradores y secretarias.
    """
    if request.user.rol not in ['admin', 'secretaria']:
        messages.error(request, "No tienes permiso para ver el historial de tarifas.")
        return redirect('roles:redireccion_dashboard')

    tarifas = Tarifa.objects.order_by('-fecha_vigencia')  # Ordenar por fecha de vigencia descendente
    return render(request, 'tarifas/historial_tarifas.html', {'tarifas': tarifas})


@login_required
def editar_tarifa(request, tarifa_id):
    """
    Vista para editar una tarifa existente. Solo accesible para usuarios administradores.
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
        form = TarifaForm(instance=tarifa)

    return render(request, 'tarifas/editar_tarifa.html', {'form': form, 'tarifa': tarifa})


@login_required
def confirmar_eliminacion_tarifa(request, tarifa_id):
    """
    Vista para confirmar la eliminación de una tarifa.
    """
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permiso para eliminar tarifas.")
        return redirect('tarifas:historial_tarifas')

    tarifa = get_object_or_404(Tarifa, id=tarifa_id)

    if request.method == 'POST':
        tarifa.delete()
        messages.success(request, f"La tarifa de {tarifa.valor} fue eliminada correctamente.")
        return redirect('tarifas:historial_tarifas')

    return render(request, 'tarifas/confirmar_eliminacion_tarifa.html', {'tarifa': tarifa})
