# Generated by Django 4.2.7 on 2024-11-14 07:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medidores', '0001_initial'),
        ('consumos', '0004_alter_consumo_cantidad_alter_consumo_medidor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumo',
            name='medidor',
            field=models.ForeignKey(default=1234, on_delete=django.db.models.deletion.CASCADE, to='medidores.medidor'),
            preserve_default=False,
        ),
    ]