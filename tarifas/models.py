# tarifas/models.py
from django.db import models
from datetime import date

class Tarifa(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor de la tarifa en moneda local")
    fecha_vigencia = models.DateField(default=date.today, help_text="Fecha desde la que la tarifa es vigente")
    fecha_fin_vigencia = models.DateField(null=True, blank=True, help_text="Fecha en la que la tarifa dejó de estar vigente")
    descripcion = models.TextField(blank=True, help_text="Descripción opcional de la tarifa")
    activo = models.BooleanField(default=True, help_text="Indica si la tarifa está activa actualmente")

    def save(self, *args, **kwargs):
        # Si esta tarifa está activa, marcar como inactivas las tarifas activas anteriores
        if self.activo:
            Tarifa.objects.filter(activo=True).exclude(id=self.id).update(activo=False, fecha_fin_vigencia=date.today())
        super().save(*args, **kwargs)

    def __str__(self):
        estado = "Activa" if self.activo else "Histórica"
        return f"Tarifa de {self.valor} ({estado} desde {self.fecha_vigencia})"
