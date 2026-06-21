from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RutinaForm, RutinaEjercicioFormSet
from .models import Rutina
# Create your views here.

@login_required
def gestion_rutinas_view(request):
    # Buscamos todas las rutinas guardadas en la base de datos
    rutinas = Rutina.objects.all() 
    # Se las pasamos al HTML a través del contexto
    return render(request, 'exercise_plans/gestion_rutinas.html', {'rutinas': rutinas})

@login_required
def crear_rutina(request):
    if request.method == 'POST':
        form = RutinaForm(request.POST)
        formset = RutinaEjercicioFormSet(request.POST)
        
        
        #Ambos formularios deben ser validos:
        if form.is_valid() and formset.is_valid():
            #Se guarda la rutina en memoria pero sin asignar un espacio en la BD 
            rutina = form.save(commit=False)
            #Asignar el autor como el usuario con sesion activa
            rutina.autor = request.user
            #Guardar por completo la rutina en la BD
            rutina.save()
            
            formset.instance = rutina
            formset.save()
            
            return redirect('exercise_plans:lista_rutinas')
    else:
        
        #Inicializar los formularios limpios
        form = RutinaForm()
        formset = RutinaEjercicioFormSet()
            
    context = {
        'form': form,
        'formset': formset
    }
            
    return render(request, 'exercise_plans/crear_rutina.html', context)
            
            