from django.contrib import admin
from .models import Boleta

@admin.register(Boleta)
class BoletaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'consumo_inicio', 'consumo_fin', 'consumo_total', 'tarifa_base', 'total_a_pagar', 'pagado', 'fecha_emision')
    search_fields = ('usuario__nombre',)
    list_filter = ('pagado', 'fecha_emision')
    ordering = ('-fecha_emision',)
