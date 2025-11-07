from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('', views.home, name='home'),
    path('iniciar-sesion/', views.login_view, name='login'),
    path('cerrar-sesion/', views.logout_view, name='logout'),  # Nueva ruta
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),  # Nueva ruta
]
