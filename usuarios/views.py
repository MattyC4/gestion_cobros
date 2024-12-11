from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario
from .forms import UsuarioForm
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404


def verificar_permiso(roles_permitidos):
    """
    Decorador para verificar permisos basados en roles.
    """
    def decorador(vista):
        def _verificar_permiso(request, *args, **kwargs):
            if request.user.rol not in roles_permitidos:
                raise Http404("No tienes permiso para acceder a esta página.")
            return vista(request, *args, **kwargs)
        return _verificar_permiso
    return decorador


@login_required
@verificar_permiso(['admin', 'secretaria'])
def lista_usuarios(request):
    """
    Vista para listar los usuarios.
    """
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@verificar_permiso(['admin', 'secretaria'])
def agregar_usuario(request):
    """
    Vista para agregar un nuevo usuario.
    """
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Usuario agregado exitosamente.")
                return redirect('usuarios:lista_usuarios')
            except IntegrityError:
                messages.error(request, "Error: Este RUT o correo ya está registrado.")
        else:
            messages.error(request, "Error: Revisa los campos ingresados.")
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/agregar_usuario.html', {'form': form})


@login_required
@verificar_permiso(['admin', 'secretaria'])
def editar_usuario(request, usuario_id):
    """
    Vista para editar un usuario existente.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect('usuarios:lista_usuarios')
        else:
            messages.error(request, "Error: Revisa los campos ingresados.")
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


@login_required
@verificar_permiso(['admin'])
def eliminar_usuario(request, usuario_id):
    """
    Vista para eliminar un usuario existente.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, f"Usuario {usuario.nombre} eliminado exitosamente.")
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})
