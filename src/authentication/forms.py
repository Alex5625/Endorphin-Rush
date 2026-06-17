from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PerfilUsuario

class RegistroCompletoForm(UserCreationForm):
    # Campos por defecto de Django: username, password1, password2
    #Se sobrescribe username para que sea un tipo correo electrónico
    username = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@alumnos.utalca.cl'})
    )
    nombre = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan'}))
    apellido = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Pérez'}))
    edad = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}))
    sexo = forms.ChoiceField(choices=PerfilUsuario.SEXO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    peso = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'En kg'}))
    altura = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ej. 1.75'}))

    class Meta(UserCreationForm.Meta):
        model = User
        # Esto define qué campos del modelo User se piden (puedes agregar 'email' si quieres)
        fields = UserCreationForm.Meta.fields

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        # Solo permitimos editar estos campos corporales/personales
        fields = ['nombre', 'apellido', 'edad', 'sexo', 'peso', 'altura']
        
        # Reutilizamos los mismos estilos de Bootstrap que el registro
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
