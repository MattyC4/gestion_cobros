from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.decorators import login_required

from medidores.models import Medidor
from tarifas.models import Tarifa
from .models import Consumo, MedidaRaw

# Modelos
from usuarios.models import Usuario
from medidores.models import Medidor
from tarifas.models import Tarifa
from .models import Consumo, MedidaRaw


# ================================
#  Decorador para permisos por rol
# ================================
def verificar_permiso(roles_permitidos):
    """
    Decorador para verificar que el usuario tenga uno de los roles permitidos.
    Si no lo tiene, muestra mensaje de error y redirige al dashboard.
    """
    def decorador(vista):
        def _wrapped(request, *args, **kwargs):
            rol = getattr(request.user, "rol", None)
            if rol not in roles_permitidos:
                messages.error(request, "No tienes permiso para acceder a esta función.")
                return redirect('roles:redireccion_dashboard')
            return vista(request, *args, **kwargs)
        return _wrapped
    return decorador


# ================================
#  Vistas principales
# ================================

@login_required
@verificar_permiso(['admin', 'operario'])
def lista_usuarios(request):
    """
    Lista de usuarios que tienen al menos un medidor asignado.
    Incluye búsqueda por nombre y paginación.
    """
    query = request.GET.get('search', '').strip()

    # Base: usuarios que tienen al menos un medidor
    usuarios_qs = Usuario.objects.filter(medidores__isnull=False).distinct()

    # Filtro por nombre si hay búsqueda
    if query:
        usuarios_qs = usuarios_qs.filter(nombre__icontains=query)

    # Totales para mostrar en tarjeta
    total_usuarios = usuarios_qs.count()

    # Paginación (10 por página)
    paginator = Paginator(usuarios_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'usuarios': page_obj,                 # iterable en el template
        'page_obj': page_obj,                 # objeto de paginación
        'is_paginated': page_obj.has_other_pages(),
        'search': query,
        'total_usuarios': total_usuarios,
    }
    return render(request, 'consumos/lista_usuarios.html', context)



@login_required
@verificar_permiso(['admin', 'operario'])
def registrar_consumo(request, usuario_id):
    """
    Vista para registrar consumo de un usuario MANUALMENTE.
    """
    if request.user.rol not in ['admin', 'operario']:
        messages.error(request, "No tienes permiso para acceder a esta función.")
        return redirect('roles:redireccion_dashboard')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    medidor = usuario.medidores.filter(estado='activo').first()
    tarifa = Tarifa.objects.filter(activo=True).first()

    if not medidor:
        messages.error(request, "El usuario no tiene un medidor activo asignado.")
        return redirect('consumos:lista_usuarios')

    if not tarifa:
        messages.error(request, "No hay tarifas activas disponibles para registrar el consumo.")
        return redirect('consumos:lista_usuarios')

   
    ultimo_consumo = (
        Consumo.objects
        .filter(medidor=medidor)
        .order_by('-fecha_consumo')
        .first()
    )

    if request.method == 'POST':
        cantidad_consumida = request.POST.get('cantidad_consumida')
        fecha_consumo = request.POST.get('fecha_consumo')

        consumo = Consumo(
            usuario=usuario,
            medidor=medidor,
            tarifa_aplicada=tarifa,
            cantidad_consumida=cantidad_consumida,
            fecha_consumo=fecha_consumo
        )
        try:
            consumo.full_clean()  # Valida el objeto antes de guardar
            consumo.save()        # Guarda el registro de consumo
            messages.success(request, "Consumo registrado exitosamente.")
            return redirect('consumos:lista_usuarios_consumos')
        except ValidationError as e:
            for error in e.message_dict.values():
                messages.error(request, error)

    return render(request, 'consumos/registrar_consumo.html', {
        'usuario': usuario,
        'medidor': medidor,
        'tarifa': tarifa,
        'ultimo_consumo': ultimo_consumo,  
    })


@login_required
@verificar_permiso(['admin', 'operario'])
def lista_usuarios_consumos(request):
    """
    Lista usuarios que tienen al menos un consumo registrado.
    Permite filtrar por nombre.
    """
    query = request.GET.get('search', '').strip()
    usuarios = Usuario.objects.filter(consumo__isnull=False).distinct()

    if query:
        usuarios = usuarios.filter(nombre__icontains=query)

    context = {
        'usuarios': usuarios,
        'search': query,
    }
    return render(request, 'consumos/lista_usuarios_consumos.html', context)


@login_required
@verificar_permiso(['admin', 'operario'])
def historial_consumos(request, usuario_id):
    """
    Historial de consumos de un usuario específico.
    Muestra consumos más recientes primero.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    consumos = (
        Consumo.objects
        .filter(usuario=usuario)
        .select_related('medidor', 'tarifa_aplicada')
        .order_by('-fecha_consumo')
    )

    return render(request, 'consumos/historial_consumos.html', {
        'usuario': usuario,
        'consumos': consumos,
    })


@login_required
@verificar_permiso(['admin', 'operario'])
def eliminar_consumo(request, consumo_id):
    """
    Elimina un registro de consumo.
    Pide confirmación por POST (formulario en template).
    """
    consumo = get_object_or_404(Consumo, id=consumo_id)

    if request.method == 'POST':
        usuario_id = consumo.usuario.id
        consumo.delete()
        messages.success(request, "El registro de consumo ha sido eliminado exitosamente.")
        return redirect('consumos:historial_consumos', usuario_id=usuario_id)

    return render(request, 'consumos/eliminar_consumo.html', {'consumo': consumo})


# ================================
#  Sincronización IoT
# ================================

@login_required
@verificar_permiso(['admin', 'operario'])

def sincronizar_lecturas_iot(request):
    """
    Busca la última lectura en la tabla 'medidas' (ESP32) para cada medidor
    y crea/actualiza el registro de Consumo del día de hoy.
    Convierte litros → m³ y marca los registros como provenientes de IoT.
    """
    if request.user.rol not in ['admin', 'operario']:
        messages.error(request, "No tienes permiso para sincronizar medidores.")
        return redirect('roles:redireccion_dashboard')

    # 1. Medidores activos
    medidores_activos = Medidor.objects.filter(estado='activo').select_related('usuario')

    # 2. Tarifa activa
    tarifa_actual = Tarifa.objects.filter(activo=True).first()
    if not tarifa_actual:
        messages.error(request, "No hay tarifa activa. No se pueden procesar lecturas IoT.")
        return redirect('consumos:lista_usuarios_consumos')

    contadores = {'creados': 0, 'actualizados': 0, 'errores': 0}
    fecha_hoy = timezone.now().date()

    for medidor in medidores_activos:
        # Solo procesamos si tiene usuario
        if not medidor.usuario:
            continue

        # 3. Última lectura cruda del ESP32 para este serial
        ultima_lectura = (
            MedidaRaw.objects
            .filter(id_medidor=medidor.codigo_serial)
            .order_by('-ts_utc')
            .first()
        )

        if not ultima_lectura:
            continue

        # 4. Convertir litros acumulados → m³ (y dejar 2 decimales)
        # litros_total: Decimal con 3 decimales (ej: 73.000 litros)
        # m³ = litros / 1000 → puede quedar con 3 decimales, así que lo redondeamos a 2.
        litros_total_en_m3 = (
            ultima_lectura.litros_total / Decimal('1000')
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        try:
            # 5. Crear o recuperar consumo de HOY
            consumo_obj, created = Consumo.objects.get_or_create(
                medidor=medidor,
                fecha_consumo=fecha_hoy,
                defaults={
                    'usuario': medidor.usuario,
                    'tarifa_aplicada': tarifa_actual,
                    'cantidad_consumida': litros_total_en_m3,
                    'fecha_registro': timezone.now()
                }
            )

            # Marcamos que viene de IoT para relajar reglas si hace falta
            consumo_obj._from_iot = True

            if created:
                contadores['creados'] += 1
            else:
                # Si la lectura cambió, actualizamos
                if consumo_obj.cantidad_consumida != litros_total_en_m3:
                    consumo_obj.cantidad_consumida = litros_total_en_m3
                    consumo_obj.fecha_registro = timezone.now()
                    consumo_obj.full_clean()  # valida con las reglas del modelo
                    consumo_obj.save()
                    contadores['actualizados'] += 1

        except ValidationError as e:
            contadores['errores'] += 1
            # Log para que veas qué pasó en consola
            print(
                f"[SYNC IOT] Error en medidor {medidor.codigo_serial}: {e}. "
                f"Última lectura litros_total={ultima_lectura.litros_total}"
            )

    # 6. Mensaje final
    mensaje = f"Sincronización IoT: {contadores['creados']} nuevos, {contadores['actualizados']} actualizados."
    if contadores['errores'] > 0:
        mensaje += f" ({contadores['errores']} errores de validación)."

    messages.success(request, mensaje)
    return redirect('consumos:lista_usuarios_consumos')


