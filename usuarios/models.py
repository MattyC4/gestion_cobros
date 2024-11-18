# usuarios/models.py
from django.core.validators import RegexValidator
from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(
        max_length=100,
        help_text="Ingrese nombre y apellido. Ejemplo: Juan Pérez"
    )
    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$',
            message='Formato de RUT inválido. Ejemplo: 12.345.678-K'
        )],
        help_text="Formato: 12.345.678-K"
    )
    correo = models.EmailField(
        max_length=255,
        unique=True,
        help_text="Ingrese un correo electrónico válido. Ejemplo: usuario@dominio.com"
    )
    direccion = models.CharField(
        max_length=255,
        help_text="Ingrese la dirección completa. Ejemplo: Calle Falsa 123, Santiago"
    )
    telefono = models.CharField(
        max_length=12,
        validators=[RegexValidator(
            regex=r'^\+569\d{8}$',
            message='El teléfono debe comenzar con +569 y tener 8 dígitos después. Ejemplo: +56912345678'
        )],
        help_text="Formato: +569XXXXXXXX (donde X son sus 8 dígitos)"
    )

    def __str__(self):
        return f"{self.nombre} ({self.rut})"
