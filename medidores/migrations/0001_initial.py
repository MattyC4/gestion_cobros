# Generated by Django 4.2.7 on 2024-11-14 05:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuarios', '0002_alter_usuario_correo_alter_usuario_direccion_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Medidor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_serial', models.CharField(max_length=50, unique=True)),
                ('fecha_instalacion', models.DateField(blank=True, null=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo', max_length=20)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medidores', to='usuarios.usuario')),
            ],
        ),
    ]
