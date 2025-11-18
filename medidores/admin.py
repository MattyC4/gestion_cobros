from django.contrib import admin
from .models import Medidor

@admin.register(Medidor)
class MedidorAdmin(admin.ModelAdmin):
    list_display = ('codigo_serial', 'usuario', 'estado', 'fecha_instalacion', 'fecha_registro')
    search_fields = ('codigo_serial', 'usuario__nombre')
    list_filter = ('estado',)
    ordering = ('-fecha_registro',)
