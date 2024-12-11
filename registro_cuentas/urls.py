from django.urls import path
from . import views

app_name = 'registro_cuentas'

urlpatterns = [
    path('', views.lista_cuentas, name='lista_cuentas'),
    path('gestionar/', views.gestionar_cuenta, name='gestionar_cuenta'),
    path('gestionar/<int:cuenta_id>/', views.gestionar_cuenta, name='gestionar_cuenta'),
    path('eliminar/<int:cuenta_id>/', views.eliminar_cuenta, name='eliminar_cuenta'),
]
