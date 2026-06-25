import email

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PerfilUsuario

class RegistroCompletoForm(UserCreationForm):
    # Campos por defecto de Django: username, password1, password2
    #Se sobrescribe username para que sea un tipo correo electrónico
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@alumnos.utalca.cl'}),
        # verbose_name="Correo Electrónico*"
    )
    edad = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}))
    sexo = forms.ChoiceField(choices=PerfilUsuario.SEXO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    peso = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'En kg'}))
    altura = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ej. 1.75'}))
    terminos_y_condiciones = forms.BooleanField(
        required=True,
        error_messages={'required': 'Debes aceptar los términos y condiciones para registrarte.'}
    )

    
    class Meta(UserCreationForm.Meta):
        model = User
        # Esto define qué campos del modelo User se piden (puedes agregar 'email' si quieres)
        fields = [ "username", "email", "first_name", "last_name", "password1", "password2" ]
        widgets = {       
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Pérez'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Le decimos a Django que no exija el username en el POST enviado por el HTML
        self.fields['username'].required = False
        # self.fields['email'].required = True
        # self.fields['email'].label = "Correo Electrónico*"
        # self.fields['first_name'].label = "Nombre*"
        # self.fields['last_name'].label = "Apellido*"
        # self.fields['password1'].label = "Contraseña*"
        # self.fields['password2'].label = "Confirmar Contraseña*"
        #self.fields['email'].verbose_name = "Correo Electrónico*"
        campos_a_modificar = ['email', 'first_name', 'last_name', 'password1', 'password2']
        for nombre_campo in campos_a_modificar:
            if nombre_campo in self.fields:
                field = self.fields[nombre_campo]
                
                # Lo volvemos obligatorio
                field.required = True
                
                # Evitamos el error del NoneType: Si no tiene label, usamos el nombre del campo capitalizado
                label_actual = field.label if field.label is not None else nombre_campo.replace('_', ' ').capitalize()
                
                # Asignamos el nuevo formato
                field.label = f"{label_actual} *"
            
        #for field in self.fields.values():
        #    field.widget.attrs["class"] = "form-control"
        for nombre_campo, field in self.fields.items():
            if nombre_campo != 'terminos_y_condiciones':
                field.widget.attrs["class"] = "form-control"
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Como el email será el username, revisamos si ya existe en la base de datos
        if email:
            if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
                raise forms.ValidationError("Este correo electrónico ya se encuentra registrado.")
        return email
    
    def clean_username(self):
        # En lugar de leer el campo oculto 'username', tomamos el email directo de los datos POST
        email = self.data.get('email')
        if email:
            return email
        return self.cleaned_data.get('username')
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email:
            # Sincronizamos ambos campos en el diccionario final de datos limpios
            cleaned_data['username'] = email
            
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        print(user)
        print(self)
        # Forzamos que tanto el email del modelo como el username sean idénticos antes de escribir el disco
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        return user
    
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
