from django.urls import path
from . import views

app_name = 'medidores'

urlpatterns = [
    path('buscar-usuario/', views.buscar_usuario_para_medidor, name='buscar_usuario_para_medidor'),
    path('asignar/<int:usuario_id>/', views.asignar_medidor_usuario, name='asignar_medidor_usuario'),
    path('historial/', views.historial_medidores, name='historial_medidores'),
    path('eliminar/<int:medidor_id>/', views.eliminar_medidor, name='eliminar_medidor'),
    path('confirmar-cambio-estado/<int:medidor_id>/', views.confirmar_cambio_estado, name='confirmar_cambio_estado'),
]
