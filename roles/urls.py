# roles/urls.py
from django.urls import path
from .views import admin_dashboard

app_name = 'roles'

urlpatterns = [
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]
