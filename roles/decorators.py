from django.core.exceptions import PermissionDenied

def role_required(*roles):
    """
    Decorador para restringir acceso a vistas según el rol del usuario.
    :param roles: Lista de roles permitidos.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'rol') and request.user.rol in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied  # Error 403 si el rol no es válido
        return _wrapped_view
    return decorator
