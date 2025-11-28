from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CuentaForm
from .models import Cuenta

# NOTA: He cambiado la vista basada en función 'lista_cuentas' a una Class Based View (ListView)
# como parece sugerir tu estructura, o mantengo la función si prefieres. 
# Basado en tu código proporcionado anteriormente que era una función, aquí la actualizo manteniendo esa estructura funcional
# para no romper tus URLs, pero inyectando los datos de estadísticas.

@login_required
def gestionar_cuenta(request, cuenta_id=None):
    """
    Vista para crear o editar cuentas.
    """
    cuenta = get_object_or_404(Cuenta, id=cuenta_id) if cuenta_id else None
    
    # Validar permisos: solo admin puede editar otras cuentas
    # Asumiendo que tienes un método o propiedad is_admin, si no, ajusta esto (ej: request.user.rol == 'administrador')
    if cuenta_id and not getattr(request.user, 'is_admin', lambda: request.user.is_superuser)(): 
        # Fallback seguro si is_admin() no existe, usa is_superuser o ajusta a tu modelo
        if not request.user.is_superuser and request.user.rol != 'administrador':
             messages.error(request, "No tienes permiso para editar esta cuenta.", extra_tags="registro_cuentas")
             return redirect('roles:redireccion_dashboard')
    
    mensaje_exito = "Cuenta actualizada exitosamente." if cuenta_id else "Cuenta creada exitosamente."

    if request.method == 'POST':
        form = CuentaForm(request.POST, instance=cuenta)
        if form.is_valid():
            try:
                cuenta_obj = form.save(commit=False)
                # Solo actualizar contraseña si se proporciona una nueva
                if form.cleaned_data.get('password'):
                    cuenta_obj.set_password(form.cleaned_data['password'])
                cuenta_obj.save()
                messages.success(request, mensaje_exito, extra_tags="registro_cuentas")
                return redirect('registro_cuentas:lista_cuentas')
            except IntegrityError:
                messages.error(request, "El nombre de usuario o correo ya existe.", extra_tags="registro_cuentas")
        else:
            campo_nombres = {
                'password': 'Contraseña',
                'confirm_password': 'Confirmación de contraseña',
                'username': 'Nombre de usuario',
                'email': 'Correo electrónico',
            }
            for field, errors in form.errors.items():
                nombre_campo = campo_nombres.get(field, field.replace('_', ' ').title())
                mensaje = f"{nombre_campo}: {errors[0]}"
                # Evitar mensajes duplicados
                if mensaje not in [m.message for m in messages.get_messages(request)]:
                    messages.error(request, mensaje, extra_tags="registro_cuentas")
    else:
        form = CuentaForm(instance=cuenta)

    return render(request, 'registro_cuentas/gestionar_cuenta.html', {
        'form': form,
        'cuenta': cuenta
    })

@login_required
def lista_cuentas(request):
    """
    Vista para listar todas las cuentas registradas.
    Accesible solo para administradores.
    """
    # Validación de rol (ajusta según tu modelo exacto)
    if not request.user.is_superuser and getattr(request.user, 'rol', '') != 'administrador':
        messages.error(request, "No tienes permiso para acceder a esta función.", extra_tags="registro_cuentas")
        return redirect('roles:redireccion_dashboard')

    # Búsqueda
    query = request.GET.get('q', request.GET.get('search', '')).strip()
    cuentas_qs = Cuenta.objects.all().order_by('-date_joined')
    
    if query and len(query) <= 50:
        cuentas_qs = cuentas_qs.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(username__icontains=query)
        )

    # --- ESTADÍSTICAS REALES ---
    # Se calculan antes de la paginación para reflejar el total del sistema, no de la página actual
    stats = {
        'total_cuentas': Cuenta.objects.count(),
        'total_admins': Cuenta.objects.filter(rol='administrador').count(),
        'total_operarios': Cuenta.objects.filter(rol='operario').count(),
        'total_secretarias': Cuenta.objects.filter(rol='secretaria').count(),
    }

    # Paginación: 10 por página
    paginator = Paginator(cuentas_qs, 10)
    page_number = request.GET.get('page')
    try:
        cuentas_page = paginator.page(page_number)
    except PageNotAnInteger:
        cuentas_page = paginator.page(1)
    except EmptyPage:
        cuentas_page = paginator.page(paginator.num_pages)

    context = {
        'cuentas': cuentas_page.object_list,
        'page_obj': cuentas_page,
        'paginator': paginator,
        'is_paginated': cuentas_page.has_other_pages(),
        'query': query,
        # Pasamos las estadísticas al template
        **stats
    }

    return render(request, 'registro_cuentas/lista_cuentas.html', context)


@login_required
def eliminar_cuenta(request, cuenta_id):
    """
    Vista para eliminar cuentas específicas.
    Accesible solo para administradores.
    """
    # Validación básica de permisos
    if not request.user.is_superuser and getattr(request.user, 'rol', '') != 'administrador':
        messages.error(request, "No tienes permiso para realizar esta acción.", extra_tags="registro_cuentas")
        return redirect('roles:redireccion_dashboard')

    cuenta = get_object_or_404(Cuenta, id=cuenta_id)
    
    # Validar que no intente eliminarse a sí mismo
    if cuenta.id == request.user.id:
        messages.error(request, "No puedes eliminar tu propia cuenta.", extra_tags="registro_cuentas")
        return redirect('registro_cuentas:lista_cuentas')

    if request.method == 'POST':
        try:
            nombre_cuenta = cuenta.username
            cuenta.delete()
            messages.success(request, f"Cuenta '{nombre_cuenta}' eliminada exitosamente.", extra_tags="registro_cuentas")
        except Exception as e:
            messages.error(request, "Error al eliminar la cuenta.", extra_tags="registro_cuentas")
        return redirect('registro_cuentas:lista_cuentas')

    return render(request, 'registro_cuentas/eliminar_cuenta.html', {
        'cuenta': cuenta
    })