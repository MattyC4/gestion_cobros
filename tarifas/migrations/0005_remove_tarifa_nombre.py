# Generated by Django 4.2.7 on 2024-11-14 07:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tarifas', '0004_tarifa_nombre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarifa',
            name='nombre',
        ),
    ]
