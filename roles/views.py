from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from roles.decorators import role_required
from usuarios.models import Usuario
from tarifas.models import Tarifa
from consumos.models import Consumo
from medidores.models import Medidor
from boletas.models import Boleta
from django.db.models import Sum, Max
from datetime import datetime
import json

@login_required
@role_required('operario')
def operario_dashboard(request):
    """
    Panel del operario.
    """
    total_usuarios = Usuario.objects.count()
    medidores_activos = Medidor.objects.filter(estado='activo').count()

    context = {
        'titulo': 'Panel de Gestión - Operario',
        'mensaje_bienvenida': 'Bienvenido al panel del operario. Aquí puedes gestionar consumos y medidores.',
        'total_usuarios': total_usuarios,
        'medidores_activos': medidores_activos,
    }

    return render(request, 'roles/operario_dashboard.html', context)


@login_required
@role_required('secretaria')
def secretaria_dashboard(request):
    """
    Dashboard de la secretaria.
    """
    total_usuarios = Usuario.objects.count()
    boletas_pagadas = Boleta.objects.filter(pagado=True).count()
    boletas_pendientes = Boleta.objects.filter(pagado=False).count()
    medidores_activos = Medidor.objects.filter(estado='activo').count()

    context = {
        'titulo': 'Panel de la Secretaria',
        'mensaje_bienvenida': 'Bienvenido al panel de gestión de la secretaria. Aquí puedes supervisar y gestionar usuarios, consumos y boletas.',
        'total_usuarios': total_usuarios,
        'boletas_pagadas': boletas_pagadas,
        'boletas_pendientes': boletas_pendientes,
        'medidores_activos': medidores_activos,
    }
    return render(request, 'roles/secretaria_dashboard.html', context)


@login_required
def redireccion_dashboard(request):
    """
    Redirige al usuario al dashboard correspondiente según su rol.
    """
    user = request.user

    if hasattr(user, 'rol'):
        if user.rol == 'admin':
            return redirect('roles:admin_dashboard')
        elif user.rol == 'secretaria':
            return redirect('roles:secretaria_dashboard')
        elif user.rol == 'operario':
            return redirect('roles:operario_dashboard')
        else:
            messages.error(request, "Rol inválido. Contacta al administrador.")
    else:
        messages.error(request, "No tienes un rol asignado. Contacta al administrador.")

    return redirect('login:home')


@login_required
@role_required('admin')
def admin_dashboard(request):
    """
    Dashboard del administrador.
    """
    total_usuarios = Usuario.objects.count()
    consumos_maximos = (
        Consumo.objects
        .values('usuario_id')
        .annotate(max_consumo=Max('cantidad_consumida'))
    )
    total_consumo_mes = sum(dato['max_consumo'] for dato in consumos_maximos)

    tarifa_actual = Tarifa.objects.filter(activo=True).first()
    medidores_activos = Medidor.objects.filter(estado='activo').count()
    medidores_inactivos = Medidor.objects.filter(estado='inactivo').count()

    tarifas = Tarifa.objects.all().order_by('fecha_vigencia')
    labels_tarifas = [tarifa.fecha_vigencia.strftime('%Y-%m-%d') for tarifa in tarifas]
    valores_tarifas = [float(tarifa.valor) for tarifa in tarifas]
    grafico_tarifas_data = {
        'labels': labels_tarifas,
        'datasets': [{
            'label': 'Evolución de Tarifas',
            'data': valores_tarifas,
            'borderColor': 'rgba(75, 192, 192, 1)',
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
        }]
    }

    consumos = Consumo.objects.values('fecha_consumo__month').annotate(
        total=Sum('cantidad_consumida')
    ).order_by('fecha_consumo__month')
    labels_consumo = [
        datetime.strptime(str(dato['fecha_consumo__month']), "%m").strftime('%B')
        for dato in consumos
    ]
    valores_consumo = [float(dato['total']) for dato in consumos]
    grafico_consumo_data = {
        'labels': labels_consumo,
        'datasets': [{
            'label': 'Consumo Mensual',
            'data': valores_consumo,
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 1,
        }]
    }

    context = {
        'titulo': 'Dashboard del Administrador',
        'mensaje_bienvenida': 'Bienvenido al panel de administración.',
        'total_usuarios': total_usuarios,
        'total_consumo_mes': total_consumo_mes,
        'tarifa_actual': tarifa_actual.valor if tarifa_actual else "N/A",
        'medidores_activos': medidores_activos,
        'medidores_inactivos': medidores_inactivos,
        'grafico_tarifas_data': json.dumps(grafico_tarifas_data),
        'grafico_consumo_data': json.dumps(grafico_consumo_data),
    }
    return render(request, 'roles/admin_dashboard.html', context)
