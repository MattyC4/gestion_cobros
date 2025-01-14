# Generated by Django 4.2.7 on 2024-11-24 06:17

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuarios', '0003_alter_usuario_nombre_alter_usuario_rut'),
        ('consumos', '0011_alter_consumo_cantidad_consumida_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boleta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField(default=datetime.date.today)),
                ('total_a_pagar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pagado', models.BooleanField(default=False)),
                ('consumo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consumos.consumo')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.usuario')),
            ],
        ),
    ]
