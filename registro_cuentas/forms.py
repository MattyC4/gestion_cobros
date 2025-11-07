from django import forms
from .models import Cuenta

class CuentaForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la contraseña'}),
        label="Contraseña"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme la contraseña'}),
        label="Confirmar Contraseña"
    )

    class Meta:
        model = Cuenta
        fields = ['username', 'email', 'rol', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el correo electrónico'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # Permite pasar la instancia actual de la cuenta al formulario
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validaciones adicionales:
        - Verificar que las contraseñas coincidan.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden. Por favor, inténtalo de nuevo.")

        return cleaned_data

    def clean_username(self):
        """
        Validar que el nombre de usuario no exista en otra cuenta.
        """
        username = self.cleaned_data.get('username')
        if Cuenta.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("El nombre de usuario ya está registrado.")
        return username

    def clean_email(self):
        """
        Validar que el correo electrónico no exista en otra cuenta.
        """
        email = self.cleaned_data.get('email')
        if Cuenta.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("El correo electrónico ya está registrado.")
        return email
