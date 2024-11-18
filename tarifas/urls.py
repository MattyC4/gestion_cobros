# tarifas/urls.py
from django.urls import path
from . import views

app_name = 'tarifas'

urlpatterns = [
    path('agregar/', views.agregar_tarifa, name='agregar_tarifa'),
    path('historial/', views.historial_tarifas, name='historial_tarifas'),
]
