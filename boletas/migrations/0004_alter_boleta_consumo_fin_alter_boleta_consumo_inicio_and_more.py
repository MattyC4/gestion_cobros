# Generated by Django 4.2.7 on 2024-11-28 00:14

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_alter_usuario_nombre_alter_usuario_rut'),
        ('consumos', '0012_alter_consumo_options_and_more'),
        ('boletas', '0003_alter_boleta_consumo_fin_alter_boleta_consumo_inicio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boleta',
            name='consumo_fin',
            field=models.ForeignKey(blank=True, help_text='Consumo final para calcular el total.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='boletas_fin', to='consumos.consumo'),
        ),
        migrations.AlterField(
            model_name='boleta',
            name='consumo_inicio',
            field=models.ForeignKey(blank=True, help_text='Consumo inicial para calcular el total.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='boletas_inicio', to='consumos.consumo'),
        ),
        migrations.AlterField(
            model_name='boleta',
            name='consumo_total',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Consumo total calculado en m³.', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='boleta',
            name='fecha_emision',
            field=models.DateField(default=datetime.date.today, help_text='Fecha de emisión de la boleta.'),
        ),
        migrations.AlterField(
            model_name='boleta',
            name='pagado',
            field=models.BooleanField(default=False, help_text='Indica si la boleta ha sido pagada.'),
        ),
        migrations.AlterField(
            model_name='boleta',
            name='tarifa_base',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Tarifa base aplicada en pesos.', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='boleta',
            name='total_a_pagar',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Monto total a pagar en pesos.', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='boleta',
            name='usuario',
            field=models.ForeignKey(help_text='Usuario asociado a esta boleta.', on_delete=django.db.models.deletion.CASCADE, to='usuarios.usuario'),
        ),
    ]
