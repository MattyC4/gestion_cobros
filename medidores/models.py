# medidores/models.py
from django.db import models
from usuarios.models import Usuario

class Medidor(models.Model):
    codigo_serial = models.CharField(max_length=50, unique=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='medidores')
    fecha_instalacion = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática
    estado = models.CharField(
        max_length=20,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='activo'
    )

    def __str__(self):
        return f"Medidor {self.codigo_serial} - Usuario: {self.usuario.nombre}"
