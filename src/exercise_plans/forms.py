from django import forms
from .models import Rutina, RutinaEjercicio
from datetime import time

class RutinaForm(forms.ModelForm):
    # Campos auxiliares para el selector móvil (estilo 1-12, min, AM/PM)
    
    select_attrs = {'class': 'form-select form-select-sm rounded-3'}
    
    # Creamos dos juegos: uno para correo y otro para pop-up
    hora_c_sel = forms.ChoiceField(choices=[(f"{i:02d}", f"{i}") for i in range(1, 13)], label="Hora", widget=forms.Select(attrs=select_attrs))
    min_c_sel = forms.ChoiceField(choices=[(f"{i:02d}", f"{i:02d}") for i in range(0, 60, 5)], label="Minutos", widget=forms.Select(attrs=select_attrs))
    ampm_c_sel = forms.ChoiceField(choices=[('AM', 'AM'), ('PM', 'PM')], label="AM/PM", widget=forms.Select(attrs=select_attrs))

    hora_p_sel = forms.ChoiceField(choices=[(f"{i:02d}", f"{i}") for i in range(1, 13)], label="Hora", widget=forms.Select(attrs=select_attrs))
    min_p_sel = forms.ChoiceField(choices=[(f"{i:02d}", f"{i:02d}") for i in range(0, 60, 5)], label="Minutos", widget=forms.Select(attrs=select_attrs))
    ampm_p_sel = forms.ChoiceField(choices=[('AM', 'AM'), ('PM', 'PM')], label="AM/PM", widget=forms.Select(attrs=select_attrs))

    class Meta:
        model = Rutina
        fields = [
            'nombre_rutina', 'descripcion_rutina', 'publico',
            'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo', 
            'recordatorio_correo', 'recordatorio_popup'
        ]
        widgets = {
            'nombre_rutina': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Rutina de Pecho'}),
            'descripcion_rutina': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción de la rutina...', 'rows': 4}),
            # Agregada la clase 'dia-checkbox' a los días
            'lunes': forms.CheckboxInput(attrs={'class': 'btn-check dia-checkbox', 'autocomplete': 'off'}),
            'martes': forms.CheckboxInput(attrs={'class': 'btn-check dia-checkbox', 'autocomplete': 'off'}),
            'miercoles': forms.CheckboxInput(attrs={'class': 'btn-check dia-checkbox', 'autocomplete': 'off'}),
            'jueves': forms.CheckboxInput(attrs={'class': 'btn-check dia-checkbox', 'autocomplete': 'off'}),
            'viernes': forms.CheckboxInput(attrs={'class': 'btn-check dia-checkbox', 'autocomplete': 'off'}),
            'sabado': forms.CheckboxInput(attrs={'class': 'btn-check dia-checkbox', 'autocomplete': 'off'}),
            'domingo': forms.CheckboxInput(attrs={'class': 'btn-check dia-checkbox', 'autocomplete': 'off'}),
            'recordatorio_correo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'recordatorio_popup': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Conversión Correo
        h_c = int(cleaned_data.get('hora_c_sel'))
        m_c = int(cleaned_data.get('min_c_sel'))
        if cleaned_data.get('ampm_c_sel') == 'PM' and h_c < 12: h_c += 12
        if cleaned_data.get('ampm_c_sel') == 'AM' and h_c == 12: h_c = 0
        cleaned_data['hora_correo'] = time(h_c, m_c)

        # Conversión Pop-up
        h_p = int(cleaned_data.get('hora_p_sel'))
        m_p = int(cleaned_data.get('min_p_sel'))
        if cleaned_data.get('ampm_p_sel') == 'PM' and h_p < 12: h_p += 12
        if cleaned_data.get('ampm_p_sel') == 'AM' and h_p == 12: h_p = 0
        cleaned_data['hora_popup'] = time(h_p, m_p)
        
        return cleaned_data

RutinaEjercicioFormSet = forms.inlineformset_factory(
    Rutina, RutinaEjercicio, fields=['ejercicio', 'series', 'descanso'], extra=1, can_delete=True,
    widgets={
        'ejercicio': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        'series': forms.NumberInput(attrs={'class': 'form-control form-select-sm', 'min': 1}),
        'descanso': forms.NumberInput(attrs={'class': 'form-control form-select-sm', 'min': 0, 'placeholder': 'Segundos'}),
    }
)