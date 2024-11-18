# usuarios/forms.py
from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'rut', 'correo', 'direccion', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ejemplo: Juan Pérez'}),
            'rut': forms.TextInput(attrs={'placeholder': '12.345.678-K'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+569XXXXXXXX'}),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.startswith('+569'):
            raise forms.ValidationError("El teléfono debe comenzar con +569.")
        if len(telefono) != 12:
            raise forms.ValidationError("El teléfono debe tener un total de 12 caracteres.")
        return telefono
