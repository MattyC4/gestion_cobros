from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages import get_messages

from registro_cuentas.models import Cuenta
from .forms import LoginForm


def logout_view(request):
    """
    Vista para cerrar sesión del usuario.
    """
    logout(request)  # Cierra la sesión del usuario
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('login:home')  # Redirigir al índice después de cerrar sesión


def home(request):
    """
    Vista para la página principal del sistema (landing pública).
    """
    return render(request, 'login/index.html')


def login_view(request):
    """
    Vista para manejar el inicio de sesión de los usuarios registrados.
    Permite autenticarse utilizando el correo electrónico o nombre de usuario.
    """

    # Si ya está autenticado, no tiene sentido mostrar el login
    if request.user.is_authenticated:
        return redirect('roles:redireccion_dashboard')

    # Limpia mensajes previos irrelevantes para esta vista (GET)
    if request.method == 'GET':
        storage = get_messages(request)
        # Consumimos los mensajes, pero solo dejamos pasar los que no sean "success"
        preserved = []
        for message in storage:
            if message.level_tag != 'success':
                preserved.append(message)
        # Volvemos a meter los que sí queremos conservar
        for msg in preserved:
            messages.add_message(request, msg.level, msg.message, extra_tags=msg.tags)

    if request.method == 'POST':
        form = LoginForm(request.POST)  # Instancia del formulario con los datos enviados
        if form.is_valid():
            # Obtener las credenciales del formulario
            credential = form.cleaned_data['credential']
            password = form.cleaned_data['password']

            # Buscar usuario por nombre de usuario o correo electrónico
            user = authenticate_user(credential, password)

            if user:
                # Autenticar y redirigir al usuario
                login(request, user)
                messages.success(request, f"Bienvenido {user.username}")
                return redirect('roles:redireccion_dashboard')  # Redirigir según el rol del usuario
            else:
                messages.error(request, "Credenciales incorrectas. Por favor, inténtalo de nuevo.")
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        form = LoginForm()  # Formulario vacío para GET

    return render(request, 'login/login.html', {'form': form})


def authenticate_user(credential, password):
    """
    Función auxiliar para autenticar al usuario utilizando el correo electrónico o nombre de usuario.
    Devuelve el usuario si las credenciales son correctas, o None en caso contrario.
    """
    try:
        # Intentar encontrar al usuario por nombre de usuario
        user = Cuenta.objects.get(username=credential)
    except Cuenta.DoesNotExist:
        try:
            # Intentar encontrar al usuario por correo electrónico
            user = Cuenta.objects.get(email=credential)
        except Cuenta.DoesNotExist:
            return None  # Usuario no encontrado

    # Validar la contraseña
    if user and user.check_password(password):
        return user
    return None


def quienes_somos(request):
    """
    Vista para la página ¿Quiénes somos?.
    """
    return render(request, 'login/quienes_somos.html')
