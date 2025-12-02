from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UsuarioForm
from .models import Usuario


def verificar_permiso(roles_permitidos):
    """
    Decorador para verificar permisos basados en roles.

    Espera que el usuario tenga un atributo `rol` que puede ser:
    - un string, por ejemplo: "admin", "secretaria"
    - un objeto con atributo `nombre` (ej: user.rol.nombre)

    Si el rol del usuario no está en `roles_permitidos`, se lanza 404
    para no revelar información sobre la existencia de la vista.
    """
    def decorador(vista):
        @wraps(vista)
        def _verificar_permiso(request, *args, **kwargs):
            # Si no hay usuario o no está autenticado, login_required debe manejarlo,
            # pero si llegamos acá sin eso, devolvemos 404.
            if not hasattr(request, "user") or not request.user.is_authenticated:
                raise Http404("No tienes permiso para acceder a esta página.")

            rol = getattr(request.user, "rol", None)

            if rol is None:
                # Sin rol asociado, no tiene permiso
                raise Http404("No tienes permiso para acceder a esta página.")

            # Soportar rol como string o como objeto (ej: Rol.nombre)
            if hasattr(rol, "nombre"):
                rol_nombre = str(rol.nombre).lower()
            else:
                rol_nombre = str(rol).lower()

            roles_normalizados = [r.lower() for r in roles_permitidos]

            if rol_nombre not in roles_normalizados:
                raise Http404("No tienes permiso para acceder a esta página.")

            return vista(request, *args, **kwargs)

        return _verificar_permiso
    return decorador


@login_required
@verificar_permiso(['admin', 'secretaria'])
def lista_usuarios(request):
    """
    Vista para listar los usuarios con búsqueda y paginación.
    Solo accesible para roles 'admin' y 'secretaria'.
    """
    # Parámetro de búsqueda
    q = request.GET.get("q", "").strip()

    usuarios_qs = Usuario.objects.all()

    if q:
        usuarios_qs = usuarios_qs.filter(
            Q(nombre__icontains=q)
            | Q(rut__icontains=q)
            | Q(correo__icontains=q)
        )

    usuarios_qs = usuarios_qs.order_by("nombre")
    total_usuarios = usuarios_qs.count()

    # Paginación (10 por página)
    page = request.GET.get("page", 1)
    paginator = Paginator(usuarios_qs, 10)

    try:
        usuarios_page = paginator.page(page)
    except PageNotAnInteger:
        usuarios_page = paginator.page(1)
    except EmptyPage:
        usuarios_page = paginator.page(paginator.num_pages)

    context = {
        "usuarios": usuarios_page,       # Page object
        "q": q,                          # término de búsqueda actual
        "total_usuarios": total_usuarios,
        "is_paginated": usuarios_page.has_other_pages(),
    }
    return render(request, "usuarios/lista_usuarios.html", context)


@login_required
@verificar_permiso(['admin', 'secretaria'])
def agregar_usuario(request):
    """
    Vista para agregar un nuevo usuario.
    Solo accesible para roles 'admin' y 'secretaria'.
    """
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Usuario agregado exitosamente.")
                return redirect("usuarios:lista_usuarios")
            except IntegrityError:
                messages.error(
                    request,
                    "Error: Este RUT o correo ya está registrado. Verifica los datos ingresados."
                )
        else:
            messages.error(request, "Error: Revisa los campos ingresados.")
    else:
        form = UsuarioForm()

    context = {
        "form": form,
    }
    return render(request, "usuarios/agregar_usuario.html", context)


@login_required
@verificar_permiso(['admin', 'secretaria'])
def editar_usuario(request, usuario_id):
    """
    Vista para editar un usuario existente.
    Solo accesible para roles 'admin' y 'secretaria'.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Usuario actualizado exitosamente.")
                return redirect("usuarios:lista_usuarios")
            except IntegrityError:
                messages.error(
                    request,
                    "Error: Este RUT o correo ya está registrado para otro usuario."
                )
        else:
            messages.error(request, "Error: Revisa los campos ingresados.")
    else:
        form = UsuarioForm(instance=usuario)

    context = {
        "form": form,
        "usuario": usuario,
    }
    return render(request, "usuarios/editar_usuario.html", context)


@login_required
@verificar_permiso(['admin'])
def eliminar_usuario(request, usuario_id):
    """
    Vista para eliminar un usuario existente.
    Solo accesible para el rol 'admin'.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == "POST":
        nombre_usuario = usuario.nombre  # guardamos antes de eliminar
        usuario.delete()
        messages.success(request, f"Usuario {nombre_usuario} eliminado exitosamente.")
        return redirect("usuarios:lista_usuarios")

    context = {
        "usuario": usuario,
    }
    return render(request, "usuarios/eliminar_usuario.html", context)
