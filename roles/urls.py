from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('redireccion/', views.redireccion_dashboard, name='redireccion_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('secretaria-dashboard/', views.secretaria_dashboard, name='secretaria_dashboard'),
    path('operario-dashboard/', views.operario_dashboard, name='operario_dashboard'),
]
