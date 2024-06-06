# core/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(error_messages={'required': 'Por favor, ingrese su correo electrónico.'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        error_messages = {
            'username': {
                'required': 'Por favor, ingrese su nombre de usuario.',
                'unique': 'El nombre de usuario ya está en uso. Por favor, elija otro.',
            },
            'password1': {
                'required': 'Por favor, ingrese una contraseña.',
                'min_length': 'La contraseña debe tener al menos 8 caracteres.',
            },
            'password2': {
                'required': 'Por favor, confirme su contraseña.',
                'min_length': 'La confirmación de la contraseña debe tener al menos 8 caracteres.',
            },
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        

        return password2

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if password1:
            if password1.isdigit():
                raise ValidationError("La contraseña no puede ser completamente numérica.")
            if len(set(password1)) < 4:
                raise ValidationError("Esta contraseña es demasiado común.")
        
        return password1
