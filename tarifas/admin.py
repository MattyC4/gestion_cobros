from django.contrib import admin
from .models import Tarifa

@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ('valor', 'activo', 'fecha_vigencia', 'fecha_fin_vigencia', 'descripcion')
    list_filter = ('activo', 'fecha_vigencia')
    search_fields = ('descripcion',)
    ordering = ('-fecha_vigencia',)
