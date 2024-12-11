from django.db import models
from django.contrib.auth.models import AbstractUser

class Cuenta(AbstractUser):
    # Opciones predefinidas para roles
    NOMBRE_ROLES = [
        ('admin', 'Administrador'),
        ('secretaria', 'Secretaria'),
        ('operario', 'Operario'),
    ]

    rol = models.CharField(
        max_length=50,
        choices=NOMBRE_ROLES,
        default='operario',
        help_text="Seleccione el rol asignado a esta cuenta"
    )

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    # Métodos de conveniencia para verificar roles
    def is_admin(self):
        return self.rol == 'admin'

    def is_secretaria(self):
        return self.rol == 'secretaria'

    def is_operario(self):
        return self.rol == 'operario'
