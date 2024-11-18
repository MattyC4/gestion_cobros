# Generated by Django 4.2.7 on 2024-11-14 07:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tarifas', '0005_remove_tarifa_nombre'),
        ('medidores', '0001_initial'),
        ('consumos', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='consumo',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='consumo',
            name='medidor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medidores.medidor'),
        ),
        migrations.AlterField(
            model_name='consumo',
            name='tarifa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tarifas.tarifa'),
        ),
    ]
