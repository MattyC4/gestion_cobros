from django.contrib import admin
from .models import Consumo, MedidaRaw  # <--- IMPORTANTE: Agregamos MedidaRaw aquí

@admin.register(Consumo)
class ConsumoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'medidor', 'tarifa_aplicada', 'fecha_consumo', 'cantidad_consumida', 'fecha_registro')
    search_fields = ('usuario__nombre', 'medidor__codigo_serial')
    list_filter = ('fecha_consumo', 'medidor', 'tarifa_aplicada')
    ordering = ('-fecha_consumo',)

# --- NUEVO REGISTRO PARA EL IOT ---
@admin.register(MedidaRaw)
class MedidaRawAdmin(admin.ModelAdmin):
    # Qué columnas ver en la lista
    list_display = ('ts_utc', 'id_medidor', 'litros_total', 'caudal_lpm_prom', 'envio_ok')
    
    # Filtros laterales útiles
    list_filter = ('id_medidor', 'envio_ok', 'ts_utc')
    
    # Barra de búsqueda por serial del ESP32
    search_fields = ('id_medidor',)
    
    # Ordenar por el más reciente primero
    ordering = ('-ts_utc',)

    # --- BLOQUE DE SEGURIDAD ---
    # Esto evita que se creen, editen o borren lecturas manualmente desde el Admin.
    # Los datos crudos del hardware son sagrados.
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False