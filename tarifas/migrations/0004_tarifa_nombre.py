# Generated by Django 4.2.7 on 2024-11-14 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tarifas', '0003_remove_tarifa_nombre'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarifa',
            name='nombre',
            field=models.CharField(default='Tarifa Básica', help_text='Nombre de la tarifa', max_length=100),
        ),
    ]
