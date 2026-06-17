from .models import TipoEjercicio
from django import forms

class TipoEjercicioForm(forms.ModelForm):
#formulario para crear y editar categorías de grupos musculares
    class Meta:
        model= TipoEjercicio
        fields = ['nombre_categoria']
        widgets = {
            'nombre_categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Pecho, Espalda, Brazos, Hombros, Abdomen y Piernas',
                'autocomplete': 'off'
            })
        }
    # MÉTODO DE LIMPIEZA Y VALIDACION LOGICA
    def clean_nombre_categoria(self):
        # 1. Recuperamos el texto, eliminamos espacios extras y lo pasamos a minúsculas estrictas
        nombre = self.cleaned_data.get('nombre_categoria')
        if nombre:
            nombre = nombre.strip().lower()
        
        # 2. Comprobamos si ya existe en la base de datos para evitar duplicados lógicos
        # Usamos .exclude(pk=self.instance.pk) para que si estamos EDITANDO permita guardar el mismo
        existe = TipoEjercicio.objects.filter(nombre_categoria=nombre).exclude(pk=self.instance.pk).exists()
        
        if existe:
            raise forms.ValidationError(
                "Esta categoría de grupo muscular ya existe en la base de datos."
            )
            
        # 3. Retornamos el valor en minúsculas listo para ser guardado
        return nombre
