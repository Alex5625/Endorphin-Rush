from django import forms
from .models import Rutina, RutinaEjercicio

class RutinaForm(forms.ModelForm):
    class Meta:
        model = Rutina
        fields = ['nombre_rutina', 'descripcion_rutina']
        widgets = {
            'nombre_rutina': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Rutina de Pecho'}),
            'descripcion_rutina': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción de la rutina...', 'rows': 4}),
        }
        
RutinaEjercicioFormSet = forms.inlineformset_factory(
    Rutina, 
    RutinaEjercicio, 
    fields=['ejercicio', 'series', 'descanso', 'orden'], 
    extra=1,
    can_delete=True,
    widgets={
        'ejercicio': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        'series': forms.NumberInput(attrs={'class': 'form-control form-select-sm', 'min': 1}),
        'descanso': forms.NumberInput(attrs={'class': 'form-control form-select-sm', 'min': 0, 'planeholder': 'Segundos (ej: 60)'}),
        'orden': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-end', 'min': 1}),
    }
)