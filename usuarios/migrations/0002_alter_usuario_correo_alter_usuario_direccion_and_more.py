# Generated by Django 4.2.7 on 2024-11-14 05:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='correo',
            field=models.EmailField(help_text='Ingrese un correo electrónico válido. Ejemplo: usuario@dominio.com', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='direccion',
            field=models.CharField(help_text='Ingrese la dirección completa. Ejemplo: Calle Falsa 123, Santiago', max_length=255),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='nombre',
            field=models.CharField(help_text='Ingrese nombre y apellido. Ejemplo: Juan Pérez', max_length=100),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='rut',
            field=models.CharField(help_text='Formato: 12.345.678-K', max_length=12, unique=True, validators=[django.core.validators.RegexValidator(message='Formato de RUT inválido. Ejemplo: 12.345.678-K', regex='^\\d{1,2}\\.\\d{3}\\.\\d{3}-[\\dkK]$')]),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='telefono',
            field=models.CharField(help_text='Formato: +569XXXXXXXX (donde X son sus 8 dígitos)', max_length=12, validators=[django.core.validators.RegexValidator(message='El teléfono debe comenzar con +569 y tener 8 dígitos después. Ejemplo: +56912345678', regex='^\\+569\\d{8}$')]),
        ),
    ]
