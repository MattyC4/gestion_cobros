from django.db import models
from datetime import date
from django.core.exceptions import ValidationError


class Tarifa(models.Model):
    """
    Modelo para gestionar las tarifas del sistema.
    """
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor de la tarifa en moneda local"
    )
    fecha_vigencia = models.DateField(
        default=date.today,
        help_text="Fecha desde la que la tarifa es vigente"
    )
    fecha_fin_vigencia = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha en la que la tarifa dejó de estar vigente"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción opcional de la tarifa"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si la tarifa está activa actualmente"
    )

    def clean(self):
        """
        Validaciones antes de guardar el modelo.
        """
        # Validar que la fecha de fin de vigencia sea posterior a la fecha de vigencia
        if self.fecha_fin_vigencia and self.fecha_fin_vigencia <= self.fecha_vigencia:
            raise ValidationError("La fecha de fin de vigencia debe ser posterior a la fecha de vigencia.")

    def save(self, *args, **kwargs):
        """
        Método para guardar el modelo. Desactiva otras tarifas si esta es activada.
        """
        # Llamar las validaciones antes de guardar
        self.clean()

        # Desactivar otras tarifas activas si esta está marcada como activa
        if self.activo:
            Tarifa.objects.filter(activo=True).exclude(id=self.id).update(
                activo=False,
                fecha_fin_vigencia=date.today()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        estado = "Activa" if self.activo else "Histórica"
        return f"Tarifa de {self.valor} ({estado} desde {self.fecha_vigencia})"
