# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .models import Usuario
from .forms import UsuarioForm
# usuarios/views.py
from django.db import IntegrityError
from django.shortcuts import render, redirect
from .forms import UsuarioForm
from django.contrib import messages  # Para mostrar mensajes al usuario


def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


def agregar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Usuario agregado exitosamente.")
                return redirect('usuarios:lista_usuarios')
            except IntegrityError:
                # Si hay un error de integridad, probablemente sea por RUT duplicado
                form.add_error('rut', "Este RUT ya está registrado. Ingrese un RUT diferente.")
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/agregar_usuario.html', {'form': form})

def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuarios:lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})

def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})
