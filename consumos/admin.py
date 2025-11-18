from django.contrib import admin
from .models import Consumo

@admin.register(Consumo)
class ConsumoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'medidor', 'tarifa_aplicada', 'fecha_consumo', 'cantidad_consumida', 'fecha_registro')
    search_fields = ('usuario__nombre', 'medidor__codigo_serial')
    list_filter = ('fecha_consumo', 'medidor', 'tarifa_aplicada')
    ordering = ('-fecha_consumo',)
