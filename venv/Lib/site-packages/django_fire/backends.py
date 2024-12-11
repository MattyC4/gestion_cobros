from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from django_fire.exceptions import FiredPassword
from django_fire.hashers import is_password_fired

UserModel = get_user_model()


class FiredPasswordBackend:
    """Check if user's password is fired (by command)
    NOTE Use this backend with ModelBackend or an subclass of that.
    (this backend just checks invalidation of user's password)
    """
    def authenticate(self, request, username=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # NOTE If there is no appropriate user from request,
            # We have no data to check if password is fired.
            # non-existence of user instance should be handled by another backend.
            return None

        if is_password_fired(user.password):
            error_msg = _('Your password is fired. please reset your password '
                          'through password reset request.')
            messages.add_message(request, messages.ERROR, error_msg)
            raise FiredPassword(error_msg)
