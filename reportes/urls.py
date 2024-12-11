from django.urls import path
from . import views
from boletas.views import descargar_pdf as descargar_boleta_reportes  # Importar correctamente desde boletas.views

app_name = 'reportes'

urlpatterns = [
    path('revisar/', views.revisar_consumo, name='revisar_consumo'),
    path('descargar-boleta/<int:boleta_id>/', descargar_boleta_reportes, name='descargar_boleta'),
    path('simular-pago/<int:boleta_id>/', views.simular_pago, name='simular_pago'),
]
