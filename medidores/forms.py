# medidores/forms.py
from django import forms
from .models import Medidor

class MedidorForm(forms.ModelForm):
    class Meta:
        model = Medidor
        fields = ['codigo_serial', 'fecha_instalacion', 'estado']
        widgets = {
            'fecha_instalacion': forms.DateInput(attrs={'type': 'date'}),
        }
