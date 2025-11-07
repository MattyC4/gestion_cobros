from django.core.exceptions import PermissionDenied


class FireException(Exception):
    """Base exception for django_fire
    """


class FiredPassword(FireException, PermissionDenied):
    """Password is fired by staff's operation
    """
