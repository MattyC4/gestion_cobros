from django.urls import path
from . import views

app_name = 'consumos'  # Importante para los nombres de URL en templates

urlpatterns = [
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('registrar/<int:usuario_id>/', views.registrar_consumo, name='registrar_consumo'),
    path('usuarios-consumos/', views.lista_usuarios_consumos, name='usuarios-consumos'),
    path('historial/<int:usuario_id>/', views.historial_consumos, name='historial_consumos'),
]
