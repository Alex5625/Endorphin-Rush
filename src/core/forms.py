from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# #from .models import Ejercicio, PerfilUsuario, TipoEjercicio
from .models import TerminosCondiciones

# from .models import HistorialAcciones
# from authentication.models import PerfilUsuario
# from exercise_types.models import TipoEjercicio
# from exercises.models import Ejercicio

# class RegistroCompletoForm(UserCreationForm):
#     # Campos por defecto de Django: username, password1, password2
#     #Se sobrescribe username para que sea un tipo correo electrónico
#     username = forms.EmailField(
#         label="Correo Electrónico",
#         widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@alumnos.utalca.cl'})
#     )
#     nombre = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan'}))
#     apellido = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Pérez'}))
#     edad = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}))
#     sexo = forms.ChoiceField(choices=PerfilUsuario.SEXO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
#     peso = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'En kg'}))
#     altura = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ej. 1.75'}))

#     class Meta(UserCreationForm.Meta):
#         model = User
#         # Esto define qué campos del modelo User se piden (puedes agregar 'email' si quieres)
#         fields = UserCreationForm.Meta.fields

# class EditarPerfilForm(forms.ModelForm):
#     class Meta:
#         model = PerfilUsuario
#         # Solo permitimos editar estos campos corporales/personales
#         fields = ['nombre', 'apellido', 'edad', 'sexo', 'peso', 'altura']
        
#         # Reutilizamos los mismos estilos de Bootstrap que el registro
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#             'apellido': forms.TextInput(attrs={'class': 'form-control'}),
#             'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
#             'sexo': forms.Select(attrs={'class': 'form-select'}),
#             'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
#             'altura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#         }

# ##formulario para los tipos de ejercicio

# class TipoEjercicioForm(forms.ModelForm):
# #formulario para crear y editar categorías de grupos musculares
#     class Meta:
#         model= TipoEjercicio
#         fields = ['nombre_categoria']
#         widgets = {
#             'nombre_categoria': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Ej: Pecho, Espalda, Brazos, Hombros, Abdomen y Piernas',
#                 'autocomplete': 'off'
#             })
#         }
#     # MÉTODO DE LIMPIEZA Y VALIDACION LOGICA
#     def clean_nombre_categoria(self):
#         # 1. Recuperamos el texto, eliminamos espacios extras y lo pasamos a minúsculas estrictas
#         nombre = self.cleaned_data.get('nombre_categoria')
#         if nombre:
#             nombre = nombre.strip().lower()
        
#         # 2. Comprobamos si ya existe en la base de datos para evitar duplicados lógicos
#         # Usamos .exclude(pk=self.instance.pk) para que si estamos EDITANDO permita guardar el mismo
#         existe = TipoEjercicio.objects.filter(nombre_categoria=nombre).exclude(pk=self.instance.pk).exists()
        
#         if existe:
#             raise forms.ValidationError(
#                 "Esta categoría de grupo muscular ya existe en la base de datos."
#             )
            
#         # 3. Retornamos el valor en minúsculas listo para ser guardado
#         return nombre


# class ejercicioForm(forms.ModelForm):
#     class Meta:
#         model = Ejercicio
#         fields = ['nombre_ejercicio', 'tipo_ejercicio', 'imagen', 'descripcion_ejercicio']
        
#         widgets = {
#             'nombre_ejercicio': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Ej: Press de Banca, Sentadillas, Curl de Bíceps',
#                 'autocomplete': 'off',
#                 'id': 'form_nombre_ejercicio'
#             }),
#             'tipo_ejercicio': forms.Select(attrs={'class': 'form-select', 'id': 'form_tipo_ejercicio'}),
#             'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'form_imagen_ejercicio'}),
#             'descripcion_ejercicio': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'id': 'form_descripcion_ejercicio',
#                 'placeholder': 'Describe cómo realizar el ejercicio, los músculos que trabaja, etc.',
#                 'rows': 4
#             }),
#         }
#     # MÉTODO DE LIMPIEZA Y VALIDACION LOGICA
#     def clean_nombre_ejercicio(self):
#         # 1. Recuperamos el texto, eliminamos espacios extras y lo pasamos a minúsculas estrictas
#         nombre = self.cleaned_data.get('nombre_ejercicio')
#         if nombre:
#             nombre = nombre.strip().lower()
        
#         # 2. Comprobamos si ya existe en la base de datos para evitar duplicados lógicos
#         existe = Ejercicio.objects.filter(nombre_ejercicio=nombre).exclude(pk=self.instance.pk).exists()
        
#         if existe:
#             raise forms.ValidationError(
#                 "Este ejercicio ya existe en la base de datos."
#             )
            
#         # 3. Retornamos el valor en minusculas listo para ser guardado
#         return nombre

class TerminosCondicionesForm(forms.ModelForm):
    class Meta:
        model = TerminosCondiciones
        fields = ['titulo', 'contenido']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control shadow-sm', 
                'placeholder': 'Ej: TyC Versión 2.0 - Actualización de Invierno'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control shadow-sm', 
                'rows': 6, 
                'placeholder': 'Escribe aquí las cláusulas legales...'
            }),
        }