from django import forms
from .models import Publicacion

class PostForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['titulo', 'texto', 'imagen', 'rutina_vinculada']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de tu publicación',
                'autocomplete': 'off',
                'id': 'titulo_post'
            }),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'form_imagen_post'}),
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'contenido_post',
                'placeholder': 'Contenido de tu publicación',
                'rows': 4
            }),
            'rutina_vinculada': forms.Select(attrs={'class': 'form-select', 'id': 'form_rutina_vinculada'}),
        
        }