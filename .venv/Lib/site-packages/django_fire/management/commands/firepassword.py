from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from django_fire.hashers import make_fired_password

UserModel = get_user_model()


class Command(BaseCommand):
    help = 'Fire (expire) password for users, which have weak password'

    def add_arguments(self, parser):
        self.parser = parser

        parser.add_argument(
            '--all', action='store_true',
            help=('Fire all passwords. use this only if YOU ARE VERY SURE '
                  'such as all passwords are leaked, or all kinds of '
                  'password hashers you use are vulnerable.'),
        )

        parser.add_argument(
            '--hashers', metavar='hasher', type=str, nargs='+',
            help=('Fire passwords for specific hashers you declare. '
                  'Use this when password hasher\'s algorithm is broken.'),
        )

        parser.add_argument(
            '--users', metavar='user_id', type=int, nargs='+',
            help=('It deletes password for specific users. Use this '
                  'when some user\'s password is leaked. '
                  'e.g. their passwords are littered public sites.'),
        )

    def handle(self, *args, **kwargs):
        if kwargs['all']:
            # fire all passwords
            # NOTE `_base_manager` should be used because password should be fired
            # even if some user instances are filtered out.
            queryset = UserModel._base_manager.all()

        elif kwargs['hashers']:
            # fire passwords for hashers
            # TODO
            queryset = UserModel._base_manager.none()

        elif kwargs['users']:
            # fire passwords for users
            queryset = UserModel._base_manager.filter(pk__in=kwargs['users'])

        else:
            self.parser.print_help()
            raise CommandError('Select one of options. all, hashers or users')
        passwd = make_fired_password()
        queryset.update(password=passwd)
