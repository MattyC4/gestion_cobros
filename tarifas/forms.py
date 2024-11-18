# tarifas/forms.py
from django import forms
from .models import Tarifa

class TarifaForm(forms.ModelForm):
    class Meta:
        model = Tarifa
        fields = ['valor', 'fecha_vigencia', 'descripcion']
        widgets = {
            'fecha_vigencia': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción opcional'}),
        }
