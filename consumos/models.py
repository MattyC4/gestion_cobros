from django.db import models
from usuarios.models import Usuario
from medidores.models import Medidor
from tarifas.models import Tarifa

from django.db import models
from usuarios.models import Usuario
from medidores.models import Medidor
from tarifas.models import Tarifa
from datetime import datetime  # Importa datetime para manejar fechas

class Consumo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    medidor = models.ForeignKey(Medidor, on_delete=models.CASCADE)
    tarifa_aplicada = models.ForeignKey(Tarifa, on_delete=models.CASCADE)
    fecha_consumo = models.DateField()
    cantidad_consumida = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_registro = models.DateTimeField(default=datetime.now)  # Fecha de creación automática

    def __str__(self):
        return f"Consumo de {self.usuario.nombre} - {self.fecha_consumo}"


    def __str__(self):
        return f"Consumo de {self.usuario.nombre} - {self.fecha_consumo}"

    def clean(self):
        # Validar que el medidor pertenezca al usuario seleccionado
        if self.medidor.usuario != self.usuario:
            raise ValidationError("El medidor no pertenece al usuario seleccionado.")

        # Validar que la tarifa estaba activa en la fecha del consumo
        if not self.tarifa_aplicada.activo and self.fecha_consumo >= self.tarifa_aplicada.fecha_vigencia:
            raise ValidationError("La tarifa no estaba activa en la fecha del consumo.")
