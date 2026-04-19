from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingrese Password',
        'class': 'form-control',
    }))
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repita Password',
        'class': 'form-control',
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Ingrese Nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Ingrese Apellido'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Ingrese Número de Teléfono'
        self.fields['email'].widget.attrs['placeholder'] = 'Ingrese Correo Electrónico'
        self.fields['password'].widget.attrs['placeholder'] = 'Ingrese Password'
        self.fields['confirm_password'].widget.attrs['placeholder'] = 'Repita Password'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'    