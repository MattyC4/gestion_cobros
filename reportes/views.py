from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from usuarios.models import Usuario
from consumos.models import Consumo
from boletas.models import Boleta
import re
from datetime import datetime

from django.db.models import Sum, Count, Q
from django.contrib.auth.decorators import login_required
from roles.decorators import role_required
from boletas.models import Boleta
from usuarios.models import Usuario
from consumos.models import Consumo


# reportes/views.py
import calendar
import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg
from django.shortcuts import render
from django.utils import timezone

from boletas.models import Boleta
from consumos.models import Consumo


@login_required
def dashboard_reportes(request):
    today = timezone.localdate()

    # Rango del mes actual (1 al último día)
    first_day_month = today.replace(day=1)
    last_day_month = today.replace(
        day=calendar.monthrange(today.year, today.month)[1]
    )

    # Boletas del MES actual (todas)
    qs_mes = Boleta.objects.filter(
        fecha_emision__range=(first_day_month, last_day_month)
    )

    # Ingresos del mes = suma de total_a_pagar (pagadas o no)
    ingresos_mes = (
        qs_mes.aggregate(total=Sum("total_a_pagar")).get("total") or 0
    )

    # Cantidad de boletas del mes
    boletas_mes = qs_mes.count()
    boletas_pagadas_mes = qs_mes.filter(pagado=True).count()

    # Deuda total histórica = suma de total_a_pagar de boletas no pagadas
    deuda_total = (
        Boleta.objects.filter(pagado=False)
        .aggregate(total=Sum("total_a_pagar"))
        .get("total") or 0
    )

    # Consumo promedio del mes (en base a consumos_consumo)
    consumo_promedio = (
        Consumo.objects.filter(
            fecha_consumo__range=(first_day_month, last_day_month)
        )
        .aggregate(prom=Avg("cantidad_consumida"))
        .get("prom") or 0
    )

    # Últimas boletas para la tabla (histórico)
    ultimas_boletas = (
        Boleta.objects.select_related("usuario")
        .order_by("-fecha_emision", "-id")[:10]
    )

    # ========================
    # Gráfico: ingresos 6 meses
    # ========================
    labels_meses = []
    datos_ingresos = []

    # Tomamos los últimos 6 meses respecto al mes actual
    # (aprox. restando meses "a mano" con year/mes)
    year = first_day_month.year
    month = first_day_month.month

    # Generamos 6 pares (año, mes) hacia atrás
    meses = []
    for _ in range(6):
        meses.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    # Los mostramos del más antiguo al más reciente
    for y, m in reversed(meses):
        first = date(y, m, 1)
        last = date(y, m, calendar.monthrange(y, m)[1])

        total_mes = (
            Boleta.objects.filter(
                fecha_emision__range=(first, last)
            )
            .aggregate(total=Sum("total_a_pagar"))
            .get("total") or 0
        )

        labels_meses.append(f"{m:02d}/{str(y)[-2:]}")
        datos_ingresos.append(float(total_mes))

    # ========================
    # Gráfico: estado de boletas
    # ========================
    total_pagadas = Boleta.objects.filter(pagado=True).count()
    total_pendientes = Boleta.objects.filter(pagado=False).count()

    # Consideramos "vencidas" como boletas no pagadas con fecha anterior al mes actual
    vencidas = Boleta.objects.filter(
        pagado=False,
        fecha_emision__lt=first_day_month
    ).count()

    pendientes_no_vencidas = max(total_pendientes - vencidas, 0)

    datos_estado_boletas = [
        total_pagadas,
        pendientes_no_vencidas,
        vencidas,
    ]

    contexto = {
        "ingresos_mes": ingresos_mes,
        "deuda_total": deuda_total,
        "boletas_mes": boletas_mes,
        "boletas_pagadas_mes": boletas_pagadas_mes,
        "consumo_promedio": consumo_promedio,
        "ultimas_boletas": ultimas_boletas,
        "labels_meses": json.dumps(labels_meses),
        "datos_ingresos": json.dumps(datos_ingresos),
        "datos_estado_boletas": json.dumps(datos_estado_boletas),
    }

    return render(request, "reportes/dashboard.html", contexto)


def simular_pago(request, boleta_id):
    """
    Vista para simular el pago de una boleta.
    """
    # Obtener la boleta correspondiente
    boleta = get_object_or_404(Boleta, id=boleta_id)

    # Verificar si ya está pagada
    if boleta.pagado:
        messages.info(request, f"La boleta #{boleta.id} ya está pagada.")
        return redirect('reportes:revisar_consumo')  # Redirigir al reporte del usuario

    if request.method == 'POST':
        # Obtener los datos del formulario
        tarjeta_numero = request.POST.get('tarjeta_numero', '').strip()
        tarjeta_nombre = request.POST.get('tarjeta_nombre', '').strip()
        tarjeta_expiracion = request.POST.get('tarjeta_expiracion', '').strip()
        tarjeta_cvv = request.POST.get('tarjeta_cvv', '').strip()

        # Validaciones básicas
        errores = []
        if not tarjeta_numero or len(tarjeta_numero) != 16 or not tarjeta_numero.isdigit():
            errores.append("El número de la tarjeta debe tener 16 dígitos.")
        if not tarjeta_nombre or len(tarjeta_nombre) < 3:
            errores.append("El nombre del titular debe tener al menos 3 caracteres.")
        if not tarjeta_expiracion or not re.match(r'^\d{2}/\d{2}$', tarjeta_expiracion):
            errores.append("La fecha de expiración debe tener el formato MM/YY.")
        if not tarjeta_cvv or len(tarjeta_cvv) != 3 or not tarjeta_cvv.isdigit():
            errores.append("El CVV debe tener 3 dígitos.")

        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'reportes/simular_pago.html', {'boleta': boleta})

        # Cambiar el estado de la boleta a pagado
        try:
            boleta.pagado = True
            boleta.fecha_pago = datetime.now()
            boleta.metodo_pago = "Tarjeta de Crédito/Débito"
            boleta.save()

            messages.success(
                request,
                f"El pago de la boleta #{boleta.id} por ${boleta.total_a_pagar} se realizó exitosamente."
            )
            return redirect(f"{request.META.get('HTTP_REFERER')}")  # Volver a la vista previa
        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar el pago: {e}")

    return render(request, 'reportes/simular_pago.html', {'boleta': boleta})



def revisar_consumo(request):
    """
    Vista para consultar el historial de consumos, boletas y medidores asociados.
    Incluye funcionalidad de gráficos interactivos y simulación de pago.
    """
    if request.method == 'POST':
        rut = request.POST.get('rut')

        # Validar el formato del RUT
        if not validar_rut(rut):
            agregar_mensaje_unico(
                request,
                "El formato del RUT ingresado no es válido. Por favor, verifica e intenta nuevamente.",
                "error",
                "reportes"
            )
            return render(request, 'reportes/revisar_consumo.html')

        try:
            usuario = Usuario.objects.prefetch_related('medidores').get(rut=rut)
        except Usuario.DoesNotExist:
            agregar_mensaje_unico(
                request,
                "No se encontró un usuario con el RUT ingresado.",
                "error",
                "reportes"
            )
            return render(request, 'reportes/revisar_consumo.html')

        # Obtener consumos y boletas del usuario
        consumos = Consumo.objects.filter(usuario=usuario).order_by('fecha_consumo').select_related('tarifa_aplicada')
        boletas = Boleta.objects.filter(usuario=usuario).order_by('-fecha_emision')

        # Calcular estadísticas rápidas
        total_consumido = max([consumo.cantidad_consumida for consumo in consumos], default=0)
        boletas_pagadas = boletas.filter(pagado=True).count()
        boletas_pendientes = boletas.filter(pagado=False).count()

        # Datos para el gráfico de consumo
        labels_consumo = [consumo.fecha_consumo.strftime('%Y-%m') for consumo in consumos]
        valores_consumo = [float(consumo.cantidad_consumida) for consumo in consumos]

        context = {
            'usuario': usuario,
            'consumos': consumos,
            'medidores': usuario.medidores.all(),
            'boletas': boletas,
            'total_consumido': total_consumido,
            'boletas_pagadas': boletas_pagadas,
            'boletas_pendientes': boletas_pendientes,
            'grafico_consumo_data': {
                'labels': labels_consumo,
                'datasets': [{
                    'label': 'Consumo Mensual (m³)',
                    'data': valores_consumo,
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'tension': 0.4,
                }]
            },
        }

        return render(request, 'reportes/reporte_consumo.html', context)

    return render(request, 'reportes/revisar_consumo.html')


def validar_rut(rut):
    """Valida el formato básico del RUT chileno."""
    return re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut)


def agregar_mensaje_unico(request, mensaje, nivel, etiqueta):
    """
    Agrega un mensaje único para evitar duplicados.
    """
    if not any(msg.message == mensaje for msg in get_messages(request)):
        if nivel == "error":
            messages.error(request, mensaje, extra_tags=etiqueta)
        elif nivel == "success":
            messages.success(request, mensaje, extra_tags=etiqueta)
        elif nivel == "info":
            messages.info(request, mensaje, extra_tags=etiqueta)
