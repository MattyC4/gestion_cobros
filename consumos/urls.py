from django.urls import path
from . import views

app_name = 'consumos'

urlpatterns = [
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('registrar/<int:usuario_id>/', views.registrar_consumo, name='registrar_consumo'),
    path('usuarios-consumos/', views.lista_usuarios_consumos, name='lista_usuarios_consumos'),
    path('historial/<int:usuario_id>/', views.historial_consumos, name='historial_consumos'),
    path('eliminar/<int:consumo_id>/', views.eliminar_consumo, name='eliminar_consumo'),
    path('sincronizar-iot/', views.sincronizar_lecturas_iot, name='sincronizar_iot'),
]
