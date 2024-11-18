# Generated by Django 4.2.7 on 2024-11-18 01:15

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_usuario_correo_alter_usuario_direccion_and_more'),
        ('medidores', '0001_initial'),
        ('tarifas', '0005_remove_tarifa_nombre'),
        ('consumos', '0007_alter_consumo_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='consumo',
            options={'ordering': ['-fecha_consumo']},
        ),
        migrations.AlterUniqueTogether(
            name='consumo',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='consumo',
            name='cantidad_consumida',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='consumo',
            name='fecha_consumo',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='consumo',
            name='tarifa_aplicada',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tarifas.tarifa'),
        ),
        migrations.AlterField(
            model_name='consumo',
            name='medidor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medidores.medidor'),
        ),
        migrations.AlterField(
            model_name='consumo',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.usuario'),
        ),
        migrations.AlterUniqueTogether(
            name='consumo',
            unique_together={('usuario', 'medidor', 'fecha_consumo')},
        ),
        migrations.RemoveField(
            model_name='consumo',
            name='consumo_registrado',
        ),
        migrations.RemoveField(
            model_name='consumo',
            name='fecha_creacion',
        ),
        migrations.RemoveField(
            model_name='consumo',
            name='mes',
        ),
        migrations.RemoveField(
            model_name='consumo',
            name='tarifa',
        ),
    ]