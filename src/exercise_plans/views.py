from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RutinaForm, RutinaEjercicioFormSet
from .models import Rutina
from django.db.models import Q
# Create your views here.

@login_required
def gestion_rutinas_view(request):
    # Buscamos todas las rutinas guardadas en la base de datos
    rutinas = Rutina.objects.filter(
        Q(autor=request.user) | 
        Q(autor__groups__name__in=['Coach', 'Administrador']) |
        Q(autor__is_staff=True) |
        Q(autor__is_superuser=True)
    ).distinct()
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
            
            
@login_required
def editar_rutina(request, pk):
    
    rutina = get_object_or_404(Rutina, pk=pk)
    
    
    if rutina.autor != request.user:
        return redirect('exercise_plans:lista_rutinas')

    if request.method == 'POST':
        
        form = RutinaForm(request.POST, instance=rutina)
        formset = RutinaEjercicioFormSet(request.POST, instance=rutina)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('exercise_plans:lista_rutinas')
    else:
        
        form = RutinaForm(instance=rutina)
        formset = RutinaEjercicioFormSet(instance=rutina)
            
    context = {
        'form': form,
        'formset': formset,
        
    }
            
    return render(request, 'exercise_plans/editar_rutina.html', context)