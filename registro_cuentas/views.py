from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CuentaForm
from .models import Cuenta


@login_required
def gestionar_cuenta(request, cuenta_id=None):
    """
    Vista para crear o editar cuentas.
    """
    cuenta = get_object_or_404(Cuenta, id=cuenta_id) if cuenta_id else None
    mensaje_exito = "Cuenta actualizada exitosamente." if cuenta_id else "Cuenta creada exitosamente."

    if request.method == 'POST':
        form = CuentaForm(request.POST, instance=cuenta)
        if form.is_valid():
            cuenta = form.save(commit=False)
            cuenta.set_password(form.cleaned_data['password'])
            cuenta.save()
            messages.success(request, mensaje_exito, extra_tags="registro_cuentas")
            return redirect('registro_cuentas:lista_cuentas')
        else:
            # Agrega mensajes de error específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}", extra_tags="registro_cuentas")
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
    if not request.user.is_admin():
        messages.error(request, "No tienes permiso para acceder a esta función.", extra_tags="registro_cuentas")
        return redirect('roles:redireccion_dashboard')

    query = request.GET.get('search', '').strip()
    cuentas = Cuenta.objects.all()
    if query:
        cuentas = cuentas.filter(username__icontains=query)

    return render(request, 'registro_cuentas/lista_cuentas.html', {
        'cuentas': cuentas,
        'query': query,
    })


@login_required
def eliminar_cuenta(request, cuenta_id):
    """
    Vista para eliminar cuentas específicas.
    Accesible solo para administradores.
    """
    if not request.user.is_admin():
        messages.error(request, "No tienes permiso para acceder a esta función.", extra_tags="registro_cuentas")
        return redirect('roles:redireccion_dashboard')

    cuenta = get_object_or_404(Cuenta, id=cuenta_id)

    if request.method == 'POST':
        cuenta.delete()
        messages.success(request, "Cuenta eliminada exitosamente.", extra_tags="registro_cuentas")
        return redirect('registro_cuentas:lista_cuentas')

    return render(request, 'registro_cuentas/eliminar_cuenta.html', {
        'cuenta': cuenta
    })
