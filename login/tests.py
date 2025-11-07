from django.test import TestCase
from tu_app.models import Cuenta

class CuentaTestCase(TestCase):
    def setUp(self):
        self.cuenta = Cuenta.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='clave123',
            rol='operario'
        )

    def test_login(self):
        login = self.client.login(username='tester', password='clave123')
        self.assertTrue(login)

