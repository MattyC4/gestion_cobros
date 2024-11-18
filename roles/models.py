# roles/models.py

from django.db import models

class Rol(models.Model):
    NOMBRE_ROLES = [
        ('admin', 'Administrador'),
        ('secretaria', 'Secretaria'),
        ('usuario', 'Usuario'),
        ('operario', 'Operario'),
    ]

    nombre = models.CharField(max_length=50, choices=NOMBRE_ROLES, unique=True)

    def __str__(self):
        return self.nombre
