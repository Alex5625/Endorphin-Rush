from django import forms
from .models import Rutina, RutinaEjercicio

class RutinaForm(forms.ModelForm):
    
    # Campos auxiliares para el selector móvil (estilo 1-12, min, AM/PM)
    select_attrs = {'class': 'form-select form-select-sm rounded-3 text-center fw-medium',
                    'style': 'min-width: 75px; padding-left: 5px; padding-right: 22px; cursor: pointer;'}
    
    # IMPORTANTE: required=False y opciones vacías ('') agregadas
    hora_c_sel = forms.ChoiceField(choices=[('', 'Hora')] + [(f"{i:02d}", f"{i}") for i in range(1, 13)], label="Hora", required=False, widget=forms.Select(attrs=select_attrs))
    min_c_sel = forms.ChoiceField(choices=[('', 'Min')] + [(f"{i:02d}", f"{i:02d}") for i in range(0, 60, 5)], label="Minutos", required=False, widget=forms.Select(attrs=select_attrs))
    ampm_c_sel = forms.ChoiceField(choices=[('', 'AM/PM'), ('AM', 'AM'), ('PM', 'PM')], label="AM/PM", required=False, widget=forms.Select(attrs=select_attrs))

    hora_p_sel = forms.ChoiceField(choices=[('', 'Hora')] + [(f"{i:02d}", f"{i}") for i in range(1, 13)], label="Hora", required=False, widget=forms.Select(attrs=select_attrs))
    min_p_sel = forms.ChoiceField(choices=[('', 'Min')] + [(f"{i:02d}", f"{i:02d}") for i in range(0, 60, 5)], label="Minutos", required=False, widget=forms.Select(attrs=select_attrs))
    ampm_p_sel = forms.ChoiceField(choices=[('', 'AM/PM'), ('AM', 'AM'), ('PM', 'PM')], label="AM/PM", required=False, widget=forms.Select(attrs=select_attrs))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Desactivar la obligación de los campos reales
        self.fields['hora_correo'].required = False
        self.fields['hora_popup'].required = False
        
        # Si estamos editando (instancia existe)
        if self.instance and self.instance.pk:
            # Precargamos los valores desde la base de datos
            hora_c = self.instance.hora_correo
            if hora_c:
                self.fields['hora_c_sel'].initial = f"{hora_c.hour % 12 or 12:02d}"
                self.fields['min_c_sel'].initial = f"{hora_c.minute:02d}"
                self.fields['ampm_c_sel'].initial = 'AM' if hora_c.hour < 12 else 'PM'
            
            # Repetir para Pop-up
            hora_p = self.instance.hora_popup
            if hora_p:
                self.fields['hora_p_sel'].initial = f"{hora_p.hour % 12 or 12:02d}"
                self.fields['min_p_sel'].initial = f"{hora_p.minute:02d}"
                self.fields['ampm_p_sel'].initial = 'AM' if hora_p.hour < 12 else 'PM'
    
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
        
    def clean(self):
        cleaned_data = super().clean()
        # Obtenemos los selectores desde self.data y los booleanos desde cleaned_data
        h_c = self.data.get('hora_c_sel')
        m_c = self.data.get('min_c_sel')
        ap_c = self.data.get('ampm_c_sel')
        recordatorio_correo = cleaned_data.get('recordatorio_correo')
        
        h_p = self.data.get('hora_p_sel')
        m_p = self.data.get('min_p_sel')
        ap_p = self.data.get('ampm_p_sel')
        recordatorio_popup = cleaned_data.get('recordatorio_popup')

        # Procesar Correo: Solo asigna hora si el switch está encendido y los campos están completos
        if recordatorio_correo and all([h_c, m_c, ap_c]):
            h_c_int = int(h_c)
            m_c_int = int(m_c)
            if ap_c == 'PM' and h_c_int < 12: h_c_int += 12
            if ap_c == 'AM' and h_c_int == 12: h_c_int = 0
            cleaned_data['hora_correo'] = time(h_c_int, m_c_int)
        else:
            # Limpiamos el campo si el switch se apagó o la hora está incompleta
            cleaned_data['hora_correo'] = None
        
        # Procesar Pop-up: Solo asigna hora si el switch está encendido y los campos están completos
        if recordatorio_popup and all([h_p, m_p, ap_p]):
            h_p_int = int(h_p)
            m_p_int = int(m_p)
            if ap_p == 'PM' and h_p_int < 12: h_p_int += 12
            if ap_p == 'AM' and h_p_int == 12: h_p_int = 0
            cleaned_data['hora_popup'] = time(h_p_int, m_p_int)
        else:
             # Limpiamos el campo si el switch se apagó o la hora está incompleta
            cleaned_data['hora_popup'] = None
        
        return cleaned_data

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