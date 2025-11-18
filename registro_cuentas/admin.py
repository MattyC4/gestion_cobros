from django.contrib import admin
from .models import Cuenta

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('username', 'rol', 'email', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    ordering = ('username',)
