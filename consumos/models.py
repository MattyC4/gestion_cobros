from django.db import models
from usuarios.models import Usuario
from medidores.models import Medidor
from tarifas.models import Tarifa
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, date


class Consumo(models.Model):
    """
    Modelo que representa los consumos de agua registrados en el sistema.
    """
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        help_text="Usuario al que pertenece este consumo."
    )
    medidor = models.ForeignKey(
        Medidor, 
        on_delete=models.CASCADE, 
        help_text="Medidor asociado a este consumo."
    )
    tarifa_aplicada = models.ForeignKey(
        Tarifa, 
        on_delete=models.CASCADE, 
        help_text="Tarifa aplicada al consumo."
    )
    fecha_consumo = models.DateField(
        help_text="Fecha en que se realizó el consumo."
    )
    cantidad_consumida = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Cantidad de agua consumida en metros cúbicos (m³)."
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True, 
        help_text="Fecha en la que se registró el consumo."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['medidor', 'fecha_consumo'], name='unique_consumo_por_fecha')
        ]
        verbose_name = "Consumo"
        verbose_name_plural = "Consumos"

    def __str__(self):
        return f"Consumo: {self.cantidad_consumida} m³ - {self.usuario.nombre} ({self.fecha_consumo})"

    def clean(self):
        """
        Validaciones personalizadas:
        - La cantidad consumida no debe ser menor al consumo anterior del medidor.
        - El medidor debe estar activo.
        - La tarifa debe estar activa.
        """
        super().clean()

        # Validar que el medidor esté activo
        if self.medidor.estado != 'activo':
            raise ValidationError("No se pueden registrar consumos para medidores inactivos.")

        # Validar que la tarifa esté activa
        if not self.tarifa_aplicada.activo:
            raise ValidationError("No se puede aplicar una tarifa inactiva.")

        # Validar que la cantidad consumida no sea menor al último consumo registrado
        ultimo_consumo = (
            Consumo.objects.filter(medidor=self.medidor)
            .exclude(id=self.id)  # Excluye el registro actual para evitar conflictos al editar
            .only('cantidad_consumida')
            .order_by('-fecha_consumo')
            .first()
        )

        if ultimo_consumo:
            cantidad_consumida_decimal = Decimal(self.cantidad_consumida)
            if cantidad_consumida_decimal < ultimo_consumo.cantidad_consumida:
                raise ValidationError(
                    f"La cantidad consumida ({cantidad_consumida_decimal} m³) no puede ser menor que el último registro ({ultimo_consumo.cantidad_consumida} m³)."
                )

    def save(self, *args, **kwargs):
        """
        Sobrescribimos el método save para ejecutar validaciones antes de guardar.
        """
        self.clean()
        super().save(*args, **kwargs)
