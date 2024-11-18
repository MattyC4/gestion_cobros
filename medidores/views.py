# medidores/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Medidor
from usuarios.models import Usuario
from .forms import MedidorForm

# Vista para mostrar todos los usuarios con el estado de medidor
def buscar_usuario_para_medidor(request):
    query = request.GET.get('q', '')
    # Filtrar usuarios por el término de búsqueda, mostrando todos
    usuarios = Usuario.objects.filter(nombre__icontains=query)
    return render(request, 'medidores/buscar_usuario_para_medidor.html', {'usuarios': usuarios, 'query': query})

# Vista para asignar un medidor a un usuario específico
def asignar_medidor_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Verificar si el usuario ya tiene un medidor asignado
    if usuario.medidores.exists():
        return redirect('medidores:buscar_usuario_para_medidor')  # Redirigir si ya tiene medidor

    if request.method == 'POST':
        form = MedidorForm(request.POST)
        if form.is_valid():
            medidor = form.save(commit=False)
            medidor.usuario = usuario
            medidor.save()
            return redirect('medidores:historial_medidores')
    else:
        form = MedidorForm()

    return render(request, 'medidores/asignar_medidor_usuario.html', {'form': form, 'usuario': usuario})

# Vista para ver el historial de medidores
def historial_medidores(request):
    medidores = Medidor.objects.all().order_by('-fecha_registro')  # Ordenar por fecha de registro
    return render(request, 'medidores/historial_medidores.html', {'medidores': medidores})

# Vista para eliminar un medidor
def eliminar_medidor(request, medidor_id):
    medidor = get_object_or_404(Medidor, id=medidor_id)
    if request.method == 'POST':
        medidor.delete()
        return redirect('medidores:historial_medidores')
    return render(request, 'medidores/eliminar_medidor.html', {'medidor': medidor})
