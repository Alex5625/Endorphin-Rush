from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RutinaForm, RutinaEjercicioFormSet
from django.contrib import messages
from .models import Rutina
from django.db.models import Q
# Create your views here.

@login_required
def gestion_rutinas_view(request):
    # Buscamos todas las rutinas guardadas en la base de datos
    rutinas = Rutina.objects.filter(
        Q(autor=request.user) | 
        Q(publico=True)).distinct()
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

    es_coach = request.user.groups.filter(name__in=['Coach', 'Administrador']).exists() or request.user.is_staff

    if request.method == 'POST':
        
        form = RutinaForm(request.POST, instance=rutina)
        formset = RutinaEjercicioFormSet(request.POST, instance=rutina)
        
        if form.is_valid() and formset.is_valid():
            rutina_editada = form.save(commit=False)
            
            if not es_coach:
                rutina_editada.publico = False
                
            rutina_editada.save()

            ejercicios = formset.save(commit=False)
            for contador, ejercicio in enumerate(ejercicios, start=1):
                if not ejercicio.orden:
                    ejercicio.orden = contador
                ejercicio.save()
                
            for obj in formset.deleted_objects:
                obj.delete()
                
            return redirect('exercise_plans:lista_rutinas')
    else:
        
        form = RutinaForm(instance=rutina)
        formset = RutinaEjercicioFormSet(instance=rutina)
        if not es_coach and 'publico' in form.fields:
            del form.fields['publico']
            
    context = {
        'form': form,
        'formset': formset,
        
    }
            
    return render(request, 'exercise_plans/editar_rutina.html', context)

@login_required
def eliminar_rutina(request, pk):
    rutina = get_object_or_404(Rutina, pk=pk)
    titulo = rutina.nombre_rutina
    rutina.delete()
    messages.success(request, f"La rutina '{titulo}' ha sido eliminada existosamente")
    return redirect('exercise_plans:lista_rutinas')