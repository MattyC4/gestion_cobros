# tarifas/views.py
from django.shortcuts import render, redirect
from .models import Tarifa
from .forms import TarifaForm
from django.utils import timezone

def agregar_tarifa(request):
    if request.method == 'POST':
        form = TarifaForm(request.POST)
        if form.is_valid():
            # Crear nueva tarifa y desactivar la anterior automáticamente en el modelo
            nueva_tarifa = form.save(commit=False)
            nueva_tarifa.fecha_vigencia = timezone.now().date()
            nueva_tarifa.activo = True
            nueva_tarifa.save()
            return redirect('tarifas:historial_tarifas')
    else:
        form = TarifaForm()
    return render(request, 'tarifas/agregar_tarifa.html', {'form': form})

def historial_tarifas(request):
    tarifas = Tarifa.objects.order_by('-fecha_vigencia')
    return render(request, 'tarifas/historial_tarifas.html', {'tarifas': tarifas})
