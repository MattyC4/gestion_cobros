from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX, UNUSABLE_PASSWORD_SUFFIX_LENGTH
)
from django.utils.crypto import get_random_string

FIRED_PASSWORD_MARK = ':fired-password:'
FIRED_PASSWORD_PREFIX = UNUSABLE_PASSWORD_PREFIX + FIRED_PASSWORD_MARK
FIRED_PASSWORD_SUFFIX_LENGTH = (
    UNUSABLE_PASSWORD_SUFFIX_LENGTH - len(FIRED_PASSWORD_MARK)
)


def is_password_fired(encoded):
    return encoded.startswith(FIRED_PASSWORD_PREFIX)


def make_fired_password():
    return FIRED_PASSWORD_PREFIX + get_random_string(FIRED_PASSWORD_SUFFIX_LENGTH)
