from django.db import models
from django.core.exceptions import ValidationError
from usuarios.models import Usuario
from consumos.models import Consumo
from datetime import date
from decimal import Decimal


class Boleta(models.Model):
    """
    Modelo para representar una boleta generada para un usuario basada en su consumo.
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        help_text="Usuario asociado a esta boleta."
    )
    consumo_inicio = models.ForeignKey(
        Consumo,
        on_delete=models.CASCADE,
        related_name='boletas_inicio',
        null=True,
        blank=True,
        help_text="Consumo inicial para calcular el total."
    )
    consumo_fin = models.ForeignKey(
        Consumo,
        on_delete=models.CASCADE,
        related_name='boletas_fin',
        null=True,
        blank=True,
        help_text="Consumo final para calcular el total."
    )
    fecha_emision = models.DateField(
        default=date.today,
        help_text="Fecha de emisión de la boleta."
    )
    consumo_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Consumo total calculado en m³."
    )
    tarifa_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Tarifa base aplicada en pesos."
    )
    total_a_pagar = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monto total a pagar en pesos."
    )
    pagado = models.BooleanField(
        default=False,
        help_text="Indica si la boleta ha sido pagada."
    )

    def clean(self):
        """
        Validaciones personalizadas antes de guardar:
        - El consumo inicial no debe ser igual al consumo final.
        - El consumo inicial debe ser anterior al consumo final.
        """
        if self.consumo_inicio and self.consumo_fin:
            if self.consumo_inicio == self.consumo_fin:
                raise ValidationError("El consumo inicial no puede ser igual al consumo final.")
            if self.consumo_inicio.fecha_consumo >= self.consumo_fin.fecha_consumo:
                raise ValidationError("El consumo inicial debe ser anterior al consumo final.")

    def calcular_total(self):
        """
        Calcula el total a pagar basado en el consumo total y tarifas escalonadas.
        """
        if not self.consumo_inicio or not self.consumo_fin:
            raise ValueError("Debe seleccionar consumos válidos para generar la boleta.")

        consumo_total = Decimal(self.consumo_fin.cantidad_consumida) - Decimal(self.consumo_inicio.cantidad_consumida)
        tarifa_base = Decimal(self.consumo_inicio.tarifa_aplicada.valor)

        # Estructura escalonada para tarifas
        if consumo_total > 10:
            if consumo_total <= 15:
                tarifa_base += Decimal(1000)
            else:
                tarifa_base += Decimal(1000) + (Decimal(1000) * (consumo_total - 15))

        total = consumo_total * tarifa_base
        self.consumo_total = consumo_total.quantize(Decimal('0.01'))  # Redondeo
        self.tarifa_base = tarifa_base.quantize(Decimal('0.01'))
        self.total_a_pagar = total.quantize(Decimal('0.01'))
        return total

    def save(self, *args, **kwargs):
        """
        Sobrescribir el método save para calcular el total antes de guardar.
        """
        self.clean()
        if self.consumo_total is None or self.total_a_pagar is None:
            self.calcular_total()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Representación en cadena del modelo.
        """
        return f"Boleta {self.id} - {self.usuario.nombre} - {self.fecha_emision}"
