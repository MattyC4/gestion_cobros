# roles/views.py
from django.shortcuts import render
from django.http import HttpResponse
from .models import Rol

def admin_dashboard(request):
    # Aquí podrías agregar lógica para obtener datos específicos del administrador.
    # De momento, cargamos solo un mensaje de bienvenida.
    context = {
        'titulo': 'Dashboard del Administrador',
        'mensaje_bienvenida': 'Bienvenido al panel de administración. Aquí podrás gestionar el sistema.',
    }
    return render(request, 'roles/admin_dashboard.html', context)
