from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from usuarios.models import Usuario
from medidores.models import Medidor
from tarifas.models import Tarifa
from .models import Consumo

# Lista de Usuarios con Medidor
def lista_usuarios(request):
    query = request.GET.get('search', '')
    usuarios = Usuario.objects.filter(medidores__isnull=False).distinct()

    if query:
        usuarios = usuarios.filter(nombre__icontains=query)

    return render(request, 'consumos/lista_usuarios.html', {'usuarios': usuarios})

# Formulario para Registrar Consumo
def registrar_consumo(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    medidor = usuario.medidores.first()  # Asume que el usuario tiene un medidor asignado
    tarifa = Tarifa.objects.filter(activo=True).first()

    if request.method == 'POST':
        cantidad_consumida = request.POST.get('cantidad_consumida')
        fecha_consumo = request.POST.get('fecha_consumo')

        # Crear el registro de consumo
        Consumo.objects.create(
            usuario=usuario,
            medidor=medidor,
            tarifa_aplicada=tarifa,
            cantidad_consumida=cantidad_consumida,
            fecha_consumo=fecha_consumo
        )

        # Redirigir a la lista de usuarios con consumos
        return redirect(reverse('consumos:usuarios-consumos'))

    return render(request, 'consumos/registrar_consumo.html', {
        'usuario': usuario,
        'medidor': medidor,
        'tarifa': tarifa
    })

# Lista de Usuarios con Consumos
def lista_usuarios_consumos(request):
    query = request.GET.get('search', '')
    usuarios = Usuario.objects.filter(consumo__isnull=False).distinct()

    if query:
        usuarios = usuarios.filter(nombre__icontains=query)

    return render(request, 'consumos/lista_usuarios_consumos.html', {'usuarios': usuarios})

# Historial de Consumos
def historial_consumos(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    consumos = Consumo.objects.filter(usuario=usuario).select_related('medidor', 'tarifa_aplicada')

    return render(request, 'consumos/historial_consumos.html', {
        'usuario': usuario,
        'consumos': consumos
    })
