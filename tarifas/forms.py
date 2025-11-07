from django import forms
from .models import Tarifa


class TarifaForm(forms.ModelForm):
    """
    Formulario para el modelo Tarifa.
    """
    class Meta:
        model = Tarifa
        fields = ['valor', 'fecha_vigencia', 'descripcion']
        widgets = {
            'fecha_vigencia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Seleccione la fecha de vigencia'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción opcional'
            }),
            'valor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el valor en pesos chilenos (Ej: 9000)'
            }),
        }

    def clean_valor(self):
        """
        Limpia y valida el campo de valor para asegurar que sea un número positivo.
        """
        valor = self.cleaned_data.get('valor')
        if not valor:
            raise forms.ValidationError("El valor es obligatorio.")
        if valor <= 0:
            raise forms.ValidationError("El valor debe ser un número positivo.")
        return valor
