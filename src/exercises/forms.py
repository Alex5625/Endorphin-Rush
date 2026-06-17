from django import forms
from django.contrib.auth.models import User
from .models import Ejercicio
from authentication.models import PerfilUsuario
from exercise_types.models import TipoEjercicio
from core.models import HistorialAcciones

class ejercicioForm(forms.ModelForm):
    class Meta:
        model = Ejercicio
        fields = ['nombre_ejercicio', 'tipo_ejercicio', 'imagen', 'descripcion_ejercicio']
        
        widgets = {
            'nombre_ejercicio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Press de Banca, Sentadillas, Curl de Bíceps',
                'autocomplete': 'off',
                'id': 'form_nombre_ejercicio'
            }),
            'tipo_ejercicio': forms.Select(attrs={'class': 'form-select', 'id': 'form_tipo_ejercicio'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'form_imagen_ejercicio'}),
            'descripcion_ejercicio': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'form_descripcion_ejercicio',
                'placeholder': 'Describe cómo realizar el ejercicio, los músculos que trabaja, etc.',
                'rows': 4
            }),
        }
    # MÉTODO DE LIMPIEZA Y VALIDACION LOGICA
    def clean_nombre_ejercicio(self):
        # 1. Recuperamos el texto, eliminamos espacios extras y lo pasamos a minúsculas estrictas
        nombre = self.cleaned_data.get('nombre_ejercicio')
        if nombre:
            nombre = nombre.strip().lower()
        
        # 2. Comprobamos si ya existe en la base de datos para evitar duplicados lógicos
        existe = Ejercicio.objects.filter(nombre_ejercicio=nombre).exclude(pk=self.instance.pk).exists()
        
        if existe:
            raise forms.ValidationError(
                "Este ejercicio ya existe en la base de datos."
            )
            
        # 3. Retornamos el valor en minusculas listo para ser guardado
        return nombre