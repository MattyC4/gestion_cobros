
# reportes/views.py
import calendar
import json
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from boletas.models import Boleta
from consumos.models import Consumo
from usuarios.models import Usuario

import re
from django.contrib.messages import get_messages



# ==========================
# DASHBOARD OPERARIO / ADMIN
# ==========================

@login_required
def dashboard_reportes(request):
    """
    Dashboard financiero para admin / operario.
    Controlamos el rol dentro de la vista.
    """
    if getattr(request.user, "rol", None) not in ["admin", "operario"]:
        messages.error(request, "No tienes permiso para acceder al módulo de reportes.")
        return redirect("roles:redireccion_dashboard")

    today = timezone.localdate()

    # Rango del mes actual
    first_day_month = today.replace(day=1)
    last_day_month = today.replace(
        day=calendar.monthrange(today.year, today.month)[1]
    )

    # Boletas del mes (todas)
    qs_mes = Boleta.objects.filter(
        fecha_emision__range=(first_day_month, last_day_month)
    )

    # Ingresos del mes = SOLO boletas pagadas
    ingresos_mes = (
        qs_mes.filter(pagado=True)
        .aggregate(total=Sum("total_a_pagar"))
        .get("total")
        or 0
    )

    boletas_mes = qs_mes.count()
    boletas_pagadas_mes = qs_mes.filter(pagado=True).count()

    if boletas_mes > 0:
        porcentaje_pagadas = round((boletas_pagadas_mes * 100) / boletas_mes, 1)
    else:
        porcentaje_pagadas = 0

    # Deuda histórica (no pagadas)
    deuda_total = (
        Boleta.objects.filter(pagado=False)
        .aggregate(total=Sum("total_a_pagar"))
        .get("total")
        or 0
    )

    # Consumo promedio del mes
    consumo_promedio = (
        Consumo.objects.filter(
            fecha_consumo__range=(first_day_month, last_day_month)
        )
        .aggregate(prom=Avg("cantidad_consumida"))
        .get("prom")
        or 0
    )

    # Últimas boletas
    ultimas_boletas = (
        Boleta.objects.select_related("usuario")
        .order_by("-fecha_emision", "-id")[:10]
    )

    # ====== Gráfico ingresos 6 meses (pagado vs pendiente) ======
    labels_meses = []
    datos_ingresos_pagados = []
    datos_ingresos_pendientes = []

    year = first_day_month.year
    month = first_day_month.month

    meses = []
    for _ in range(6):
        meses.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    for y, m in reversed(meses):
        first = date(y, m, 1)
        last = date(y, m, calendar.monthrange(y, m)[1])

        qs_mes_loop = Boleta.objects.filter(
            fecha_emision__range=(first, last)
        )

        total_pagado_mes = (
            qs_mes_loop.filter(pagado=True)
            .aggregate(total=Sum("total_a_pagar"))
            .get("total")
            or 0
        )

        total_pendiente_mes = (
            qs_mes_loop.filter(pagado=False)
            .aggregate(total=Sum("total_a_pagar"))
            .get("total")
            or 0
        )

        labels_meses.append(f"{m:02d}/{str(y)[-2:]}")
        datos_ingresos_pagados.append(float(total_pagado_mes))
        datos_ingresos_pendientes.append(float(total_pendiente_mes))

    # Estado global boletas
    total_pagadas = Boleta.objects.filter(pagado=True).count()
    total_pendientes = Boleta.objects.filter(pagado=False).count()
    vencidas = Boleta.objects.filter(
        pagado=False,
        fecha_emision__lt=first_day_month,
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
        "porcentaje_pagadas": porcentaje_pagadas,
        "consumo_promedio": consumo_promedio,
        "ultimas_boletas": ultimas_boletas,
        "labels_meses": json.dumps(labels_meses),
        "datos_ingresos_pagados": json.dumps(datos_ingresos_pagados),
        "datos_ingresos_pendientes": json.dumps(datos_ingresos_pendientes),
        "datos_estado_boletas": json.dumps(datos_estado_boletas),
    }

    return render(request, "reportes/dashboard.html", contexto)




# ==========================
# SIMULACIÓN DE PAGO (USUARIO)
# ==========================

def simular_pago(request, boleta_id):
    """
    Vista para simular el pago de una boleta.
    Pensado para el flujo público desde revisar_consumo.
    """
    boleta = get_object_or_404(Boleta, id=boleta_id)

    # Ya pagada
    if boleta.pagado:
        messages.info(request, f"La boleta #{boleta.id} ya está pagada.")
        return redirect('reportes:revisar_consumo')

    if request.method == 'POST':
        tarjeta_numero = request.POST.get('tarjeta_numero', '').strip()
        tarjeta_nombre = request.POST.get('tarjeta_nombre', '').strip()
        tarjeta_expiracion = request.POST.get('tarjeta_expiracion', '').strip()
        tarjeta_cvv = request.POST.get('tarjeta_cvv', '').strip()

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

        # Procesar “pago”
        try:
            boleta.pagado = True
            # Si en tu modelo Boleta no tienes estos campos, quita estas líneas:
            boleta.fecha_pago = datetime.now()
            boleta.metodo_pago = "Tarjeta de Crédito/Débito"
            boleta.save()

            messages.success(
                request,
                f"El pago de la boleta #{boleta.id} por ${boleta.total_a_pagar} se realizó exitosamente."
            )
            # Volver a la página anterior si existe, si no al revisar_consumo
            return redirect(request.META.get('HTTP_REFERER') or 'reportes:revisar_consumo')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar el pago: {e}")

    return render(request, 'reportes/simular_pago.html', {'boleta': boleta})


# ==========================
# CONSULTA PÚBLICA POR RUT
# ==========================

def revisar_consumo(request):
    """
    Vista pública para consultar historial de consumos y boletas por RUT.
    Incluye gráfico de consumo y badges de estado.
    """
    if request.method == 'POST':
        rut = request.POST.get('rut')

        # Validar formato RUT
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

        consumos = (
            Consumo.objects
            .filter(usuario=usuario)
            .order_by('fecha_consumo')
            .select_related('tarifa_aplicada')
        )

        boletas = Boleta.objects.filter(usuario=usuario).order_by('-fecha_emision')

        # Estadísticas rápidas
        total_consumido = max(
            [c.cantidad_consumida for c in consumos], default=0
        )
        boletas_pagadas = boletas.filter(pagado=True).count()
        boletas_pendientes = boletas.filter(pagado=False).count()

        # Datos para gráfico
        labels_consumo = [c.fecha_consumo.strftime('%Y-%m') for c in consumos]
        valores_consumo = [float(c.cantidad_consumida) for c in consumos]

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


# ==========================
# HELPERS
# ==========================

def validar_rut(rut: str) -> bool:
    """
    Valida el formato básico del RUT chileno (sin validar dígito verificador).
    Ej: 12.345.678-9 o 1.234.567-8
    """
    if not rut:
        return False
    return re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut) is not None


def agregar_mensaje_unico(request, mensaje: str, nivel: str, etiqueta: str = ""):
    """
    Agrega un mensaje evitando duplicados exactos.
    nivel: "error", "success" o "info".
    etiqueta: para extra_tags (ej: 'reportes').
    """
    if any(msg.message == mensaje for msg in get_messages(request)):
        return

    if nivel == "error":
        messages.error(request, mensaje, extra_tags=etiqueta)
    elif nivel == "success":
        messages.success(request, mensaje, extra_tags=etiqueta)
    elif nivel == "info":
        messages.info(request, mensaje, extra_tags=etiqueta)
