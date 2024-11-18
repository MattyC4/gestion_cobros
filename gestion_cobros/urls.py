# proyecto_principal/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('medidores/', include('medidores.urls', namespace='medidores')),
    path('tarifas/', include('tarifas.urls', namespace='tarifas')),
    path('consumos/', include('consumos.urls', namespace='consumos')),  # Agregamos consumos
    path('roles/', include('roles.urls', namespace='roles')),  # Para el dashboard del administrador
]
