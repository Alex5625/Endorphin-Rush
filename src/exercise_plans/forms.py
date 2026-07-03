from django import forms
from .models import Rutina, RutinaEjercicio

class RutinaForm(forms.ModelForm):
    class Meta:
        model = Rutina
        fields = [
            'nombre_rutina', 'descripcion_rutina', 'publico',
            'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'
        ]
        widgets = {
            'nombre_rutina': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Rutina de Pecho'}),
            'descripcion_rutina': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción de la rutina...', 'rows': 4}),
            'lunes': forms.CheckboxInput(attrs={'class': 'btn-check', 'autocomplete': 'off'}),
            'martes': forms.CheckboxInput(attrs={'class': 'btn-check', 'autocomplete': 'off'}),
            'miercoles': forms.CheckboxInput(attrs={'class': 'btn-check', 'autocomplete': 'off'}),
            'jueves': forms.CheckboxInput(attrs={'class': 'btn-check', 'autocomplete': 'off'}),
            'viernes': forms.CheckboxInput(attrs={'class': 'btn-check', 'autocomplete': 'off'}),
            'sabado': forms.CheckboxInput(attrs={'class': 'btn-check', 'autocomplete': 'off'}),
            'domingo': forms.CheckboxInput(attrs={'class': 'btn-check', 'autocomplete': 'off'}),
        }
        
RutinaEjercicioFormSet = forms.inlineformset_factory(
    Rutina, 
    RutinaEjercicio, 
    fields=['ejercicio', 'series', 'descanso'], 
    extra=1,
    can_delete=True,
    widgets={
        'ejercicio': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        'series': forms.NumberInput(attrs={'class': 'form-control form-select-sm', 'min': 1}),
        'descanso': forms.NumberInput(attrs={'class': 'form-control form-select-sm', 'min': 0, 'placeholder': 'Segundos (ej: 60)'}),
    }
)