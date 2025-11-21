from django.db import models
from usuarios.models import Usuario
from medidores.models import Medidor
from tarifas.models import Tarifa
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, date

# --- MODELO OFICIAL (FACTURACIÓN) ---
class Consumo(models.Model):
    """
    Modelo que representa los consumos de agua registrados en el sistema.
    Tabla gestionada por Django (consumos_consumo).
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
        help_text="Lectura del medidor en metros cúbicos (m³)."
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
        Validaciones de negocio.
        """
        super().clean()

        # Validar que el medidor esté activo
        if self.medidor.estado != 'activo':
            raise ValidationError("No se pueden registrar consumos para medidores inactivos.")

        # Validar que la tarifa esté activa
        if not self.tarifa_aplicada.activo:
            raise ValidationError("No se puede aplicar una tarifa inactiva.")

        # Validar que la lectura no sea menor a la anterior (Anti-fraude / Error de lectura)
        ultimo_consumo = (
            Consumo.objects.filter(medidor=self.medidor)
            .exclude(id=self.id)  # Excluye el actual si se está editando
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
        self.clean()
        super().save(*args, **kwargs)


# --- NUEVO MODELO: ESPEJO IOT (LECTURA) ---
class MedidaRaw(models.Model):
    """
    Modelo de SOLO LECTURA que refleja la tabla 'medidas' en Supabase.
    Aquí es donde el ESP32 inserta los datos crudos.
    """
    # Suponemos que Supabase genera un ID autoincremental llamado 'id' o similar.
    # Si tu tabla 'medidas' no tiene PK, esto es un requerimiento de Django.
    # Usaremos id_lectura mapeado al campo que tenga la tabla.
    id_lectura = models.BigAutoField(primary_key=True) 
    
    # El ESP32 manda el serial como texto (ej: "esp32-agua-01")
    id_medidor = models.TextField(db_column='id_medidor', verbose_name="Serial ESP32")
    
    ts_utc = models.DateTimeField(verbose_name="Fecha/Hora")
    pulsos_periodo = models.IntegerField()
    caudal_lpm_prom = models.DecimalField(max_digits=10, decimal_places=3)
    litros_periodo = models.DecimalField(max_digits=10, decimal_places=3)
    litros_total = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Lectura Acumulada")
    
    temperatura_c = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    bateria_v = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    
    envio_ok = models.BooleanField()
    creado_en = models.DateTimeField()

    class Meta:
        managed = False  # ¡IMPORTANTE! Django no intentará crear/borrar esta tabla
        db_table = 'medidas' # Nombre exacto de la tabla en Supabase
        verbose_name = "Lectura Cruda (IoT)"
        verbose_name_plural = "Lecturas Crudas (IoT)"
        ordering = ['-ts_utc']

    def __str__(self):
        return f"{self.id_medidor} - {self.litros_total}L ({self.ts_utc})"