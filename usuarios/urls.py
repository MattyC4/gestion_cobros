# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('lista/', views.lista_usuarios, name='lista_usuarios'),
    path('agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
]
