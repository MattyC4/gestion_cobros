from django.urls import path
from . import views

app_name = 'boletas'

urlpatterns = [
    # 1. Lista de Boletas Recientes
    path('historial-reciente/', views.historial_recientes, name='historial_recientes'),

    # 2. Buscar Usuarios para Historial de Boletas
    path('buscar-usuario/', views.buscar_usuario, name='buscar_usuario'),

    # 3. Historial de Boletas por Usuario
    path('historial-usuario/<int:usuario_id>/', views.historial_usuario, name='historial_usuario'),

    # 4. Generar Boleta: Selección de Usuario
    path('seleccionar-usuario/', views.seleccionar_usuario, name='seleccionar_usuario'),

    # 5. Generar Boleta: Selección de Consumos
    path('seleccionar-consumos/<int:usuario_id>/', views.seleccionar_consumos, name='seleccionar_consumos'),

    # 6. Generar Boleta: Crear Boleta
    path('generar/<int:usuario_id>/<int:consumo_inicio_id>/<int:consumo_fin_id>/', views.generar_boleta, name='generar_boleta'),

    # 7. Descargar Boleta como PDF
    path('descargar/<int:boleta_id>/', views.descargar_pdf, name='descargar_pdf'),

    # 8. Confirmar y Cambiar Estado de Boleta
    path('confirmar-estado/<int:boleta_id>/', views.actualizar_estado_boleta, name='confirmar_actualizar_estado_boleta'),

    # 9. Confirmar y Eliminar Boleta
    path('confirmar-eliminar/<int:boleta_id>/', views.confirmar_eliminar_boleta, name='confirmar_eliminar_boleta'),

    # 10. Cambiar Estado de Boleta
    path('actualizar-estado/<int:boleta_id>/', views.actualizar_estado_boleta, name='actualizar_estado_boleta'),

    # 11. Eliminar Boleta
    path('eliminar/<int:boleta_id>/', views.eliminar_boleta, name='eliminar_boleta'),

    path('imprimir/<int:boleta_id>/', views.imprimir_boleta, name='imprimir_boleta'),
]

