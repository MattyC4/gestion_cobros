from django import forms
from .models import Usuario
from django.core.exceptions import ValidationError


class UsuarioForm(forms.ModelForm):
    """
    Formulario para el modelo Usuario con validaciones y mensajes personalizados.
    """

    class Meta:
        model = Usuario
        fields = ['nombre', 'rut', 'correo', 'direccion', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ejemplo: Juan Pérez',
                'class': 'form-control'
            }),
            'rut': forms.TextInput(attrs={
                'placeholder': '12.345.678-K',
                'class': 'form-control'
            }),
            'correo': forms.EmailInput(attrs={
                'placeholder': 'usuario@dominio.com',
                'class': 'form-control'
            }),
            'direccion': forms.TextInput(attrs={
                'placeholder': 'Ejemplo: Calle Falsa 123, Santiago',
                'class': 'form-control'
            }),
            'telefono': forms.TextInput(attrs={
                'placeholder': '+569XXXXXXXX',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['rut'].widget.attrs['readonly'] = True  # Desactivar RUT en edición

    def clean_telefono(self):
        """
        Valida que el teléfono tenga el formato +569 seguido de 8 dígitos.
        """
        telefono = self.cleaned_data.get('telefono')
        if not telefono.startswith('+569'):
            raise ValidationError("El teléfono debe comenzar con +569.")
        if len(telefono) != 12:
            raise ValidationError("El teléfono debe tener un total de 12 caracteres.")
        return telefono

    def clean_nombre(self):
        """
        Valida que el nombre contenga solo letras y espacios.
        """
        nombre = self.cleaned_data.get('nombre')
        if not nombre.replace(" ", "").isalpha():
            raise ValidationError("El nombre solo debe contener letras y espacios.")
        return nombre

    def clean_rut(self):
        """
        Valida que el RUT sea único y tenga el formato correcto.
        """
        rut = self.cleaned_data.get('rut')
        if Usuario.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
            raise ValidationError("El RUT ingresado ya está registrado.")
        return rut

    def clean_correo(self):
        """
        Valida que el correo electrónico sea único.
        """
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exclude(pk=self.instance.pk).exists():
            raise ValidationError("El correo ingresado ya está registrado.")
        return correo
