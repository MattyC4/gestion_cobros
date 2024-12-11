# Generated by Django 4.2.7 on 2024-11-27 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medidores', '0002_alter_medidor_codigo_serial_alter_medidor_estado_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='medidor',
            options={'ordering': ['-fecha_instalacion']},
        ),
        migrations.AlterField(
            model_name='medidor',
            name='codigo_serial',
            field=models.CharField(db_index=True, help_text='Código serial único del medidor.', max_length=50, unique=True),
        ),
    ]