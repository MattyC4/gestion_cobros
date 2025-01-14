# Generated by Django 4.2.7 on 2024-11-14 05:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tarifa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre de la tarifa', max_length=100)),
                ('valor', models.DecimalField(decimal_places=2, help_text='Valor de la tarifa en moneda local', max_digits=10)),
                ('fecha_vigencia', models.DateField(default=datetime.date.today, help_text='Fecha desde la que la tarifa es vigente')),
                ('activo', models.BooleanField(default=True, help_text='Indica si la tarifa está activa actualmente')),
            ],
        ),
    ]
