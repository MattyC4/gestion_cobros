from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'correo', 'telefono', 'direccion')
    search_fields = ('nombre', 'rut', 'correo')
    list_filter = ('direccion',)  # Puedes filtrar por comuna si agregas campo
    ordering = ('nombre',)
