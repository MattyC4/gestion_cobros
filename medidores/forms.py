from django import forms
from .models import Medidor
from datetime import date
from django.core.exceptions import ValidationError

class MedidorForm(forms.ModelForm):
    """
    Formulario para el modelo Medidor, con validaciones personalizadas.
    """

    class Meta:
        model = Medidor
        fields = ['codigo_serial', 'fecha_instalacion', 'estado']
        widgets = {
            'fecha_instalacion': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Seleccione la fecha de instalación'
            }),
            'codigo_serial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el código serial del medidor'
            }),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con configuraciones adicionales.
        """
        self.usuario = kwargs.pop('usuario', None)  # Extraer el usuario del kwargs
        super().__init__(*args, **kwargs)

    def clean_fecha_instalacion(self):
        """
        Valida que la fecha de instalación no sea futura.
        """
        fecha_instalacion = self.cleaned_data.get('fecha_instalacion')
        if fecha_instalacion and fecha_instalacion > date.today():
            raise ValidationError("La fecha de instalación no puede ser una fecha futura.")
        return fecha_instalacion

    def clean_codigo_serial(self):
        """
        Valida que el código serial sea único y no esté vacío.
        """
        codigo_serial = self.cleaned_data.get('codigo_serial')
        if not codigo_serial:
            raise ValidationError("El código serial es obligatorio.")
        
        # Validar unicidad del código serial, excluyendo la instancia actual si existe
        if Medidor.objects.filter(codigo_serial=codigo_serial).exclude(id=self.instance.id).exists():
            raise ValidationError("El código serial ya está en uso. Por favor, elija uno diferente.")
        return codigo_serial

    def save(self, commit=True):
        """
        Guarda el medidor asignándolo al usuario correspondiente.
        """
        instance = super().save(commit=False)

        # Validar que el usuario esté asignado antes de guardar
        if not self.usuario:
            raise ValidationError("Debe asignarse un usuario al medidor antes de guardarlo.")

        instance.usuario = self.usuario

        if commit:
            instance.save()
        return instance
