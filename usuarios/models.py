from django.core.validators import RegexValidator
from django.db import models
from django.core.exceptions import ValidationError

class Usuario(models.Model):
    # Validación personalizada para nombres
    def validar_nombre(value):
        """
        Valida que el nombre solo contenga letras y espacios.
        """
        if not value.replace(" ", "").isalpha():
            raise ValidationError("El nombre solo debe contener letras y espacios.")

    # Validación personalizada para RUT
    def validar_rut(value):
        """
        Valida el RUT chileno con su dígito verificador.
        """
        # Remover puntos y guión del RUT
        rut = value.replace(".", "").replace("-", "")
        if len(rut) < 2:
            raise ValidationError("El RUT ingresado no es válido.")

        cuerpo, dv = rut[:-1], rut[-1].upper()

        # Verificar que el cuerpo sea numérico
        if not cuerpo.isdigit():
            raise ValidationError("El RUT ingresado no es válido.")

        # Cálculo del dígito verificador
        suma, factor = 0, 2
        for c in reversed(cuerpo):
            suma += int(c) * factor
            factor = 2 if factor == 7 else factor + 1

        dv_calculado = 11 - (suma % 11)
        if dv_calculado == 10:
            dv_calculado = "K"
        elif dv_calculado == 11:
            dv_calculado = "0"
        else:
            dv_calculado = str(dv_calculado)

        # Comparar dígito verificador calculado con el ingresado
        if dv_calculado != dv:
            raise ValidationError(f"El RUT ingresado no es válido. Dígito verificador esperado: {dv_calculado}")

    nombre = models.CharField(
        max_length=100,
        validators=[validar_nombre],
        help_text="Ingrese nombre y apellido. Ejemplo: Juan Pérez"
    )
    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$',
                message='Formato de RUT inválido. Ejemplo: 12.345.678-K'
            ),
            validar_rut  # Validación personalizada para el RUT
        ],
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
