# Generated by Django 4.2.7 on 2024-11-20 20:20

import django.core.validators
from django.db import migrations, models
import usuarios.models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_usuario_correo_alter_usuario_direccion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='nombre',
            field=models.CharField(help_text='Ingrese nombre y apellido. Ejemplo: Juan Pérez', max_length=100, validators=[usuarios.models.Usuario.validar_nombre]),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='rut',
            field=models.CharField(help_text='Formato: 12.345.678-K', max_length=12, unique=True, validators=[django.core.validators.RegexValidator(message='Formato de RUT inválido. Ejemplo: 12.345.678-K', regex='^\\d{1,2}\\.\\d{3}\\.\\d{3}-[\\dkK]$'), usuarios.models.Usuario.validar_rut]),
        ),
    ]