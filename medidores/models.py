from django.db import models
from usuarios.models import Usuario
from django.core.exceptions import ValidationError

class Medidor(models.Model):
    """
    Modelo que representa un medidor asignado a un usuario.
    """
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('danado', 'Dañado'),
    ]

    codigo_serial = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código serial único del medidor."
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='medidores',
        null=True,  # Permitir que sea nulo temporalmente para asignar un medidor
        blank=True,
        help_text="Usuario al que está asignado este medidor."
    )
    fecha_instalacion = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha en la que se instaló el medidor."
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha en la que se registró el medidor."
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='activo',
        help_text="Estado actual del medidor."
    )

    def clean(self):
        """
        Validación adicional para asegurar que un usuario solo tenga un medidor activo.
        """
        if self.usuario and self.estado == 'activo':
            if Medidor.objects.filter(usuario=self.usuario, estado='activo').exclude(id=self.id).exists():
                raise ValidationError("Este usuario ya tiene un medidor activo asignado.")

    def __str__(self):
        """
        Representación en cadena del medidor.
        """
        usuario_info = f"Usuario: {self.usuario.nombre}" if self.usuario else "Sin asignar"
        return f"Medidor {self.codigo_serial} - {usuario_info}"
