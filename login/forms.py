from django import forms
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    """
    Formulario para iniciar sesión con validaciones básicas.
    """
    credential = forms.CharField(
        label="Correo electrónico o nombre de usuario",
        max_length=150,
        help_text="Puedes usar tu correo o nombre de usuario para iniciar sesión.",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Correo o Usuario',
            'autocomplete': 'username'  # Mejora la accesibilidad
        })
    )
    password = forms.CharField(
        label="Contraseña",
        help_text="Ingresa tu contraseña.",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password'  # Mejora la accesibilidad
        })
    )

    def clean_credential(self):
        """
        Validación personalizada para la credencial.
        """
        credential = self.cleaned_data.get('credential')
        if len(credential.strip()) < 4:
            raise ValidationError("La credencial debe tener al menos 4 caracteres.")
        return credential

    def clean_password(self):
        """
        Validación personalizada para la contraseña.
        """
        password = self.cleaned_data.get('password')
        if len(password.strip()) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if ' ' in password:  # Verifica que la contraseña no contenga espacios
            raise ValidationError("La contraseña no puede contener espacios.")
        return password

    def clean(self):
        """
        Validación general del formulario.
        Se puede usar para verificar combinaciones como credencial y contraseña.
        """
        cleaned_data = super().clean()
        credential = cleaned_data.get("credential")
        password = cleaned_data.get("password")

        # Ejemplo: Validar combinación específica
        if credential and password:
            if '@' not in credential and len(password) < 12:
                raise ValidationError("Si usas un nombre de usuario, la contraseña debe tener al menos 12 caracteres.")
        return cleaned_data
