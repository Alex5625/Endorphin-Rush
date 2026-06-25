from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .forms import RutinaForm, RutinaEjercicioFormSet
from .models import Rutina
import time

@login_required
def gestion_rutinas_view(request):
    # Validamos el rol de forma segura
    es_coach = request.user.groups.filter(name__in=['Coach', 'Administrador']).exists() or request.user.is_staff or request.user.is_superuser
    
    # Catálogo global: Solo rutinas de OTROS entrenadores que sean PÚBLICAS
    rutinas = Rutina.objects.filter(~Q(autor=request.user) & Q(publico=True)).distinct()
    
    context = {
        'rutinas': rutinas, 
        'action': 'external',
        'es_coach': es_coach
    }
    return render(request, 'exercise_plans/gestion_rutinas.html', context)

@login_required
def mis_rutinas(request):
    # Panel privado/personal del usuario (Aquí ve todas las suyas: públicas y privadas)
    rutinas_propias = Rutina.objects.filter(autor=request.user)
    return render(request, 'exercise_plans/gestion_rutinas.html', {'rutinas': rutinas_propias, 'action': 'personal'})

@login_required
def crear_rutina(request):
    es_coach = request.user.groups.filter(name__in=['Coach', 'Administrador']).exists() or request.user.is_staff or request.user.is_superuser

    if request.method == 'POST':
        form = RutinaForm(request.POST)
        formset = RutinaEjercicioFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            rutina = form.save(commit=False)
            rutina.autor = request.user
            
            # Si no es coach, se fuerza a que sea privada
            if not es_coach:
                rutina.publico = False
                
            rutina.save()
            formset.instance = rutina
            formset.save()
            
            return redirect('exercise_plans:mis_rutinas')
    else:
        form = RutinaForm()
        formset = RutinaEjercicioFormSet()
        if not es_coach and 'publico' in form.fields:
            del form.fields['publico']
            
    context = {
        'form': form,
        'formset': formset,
        'action': 'crear'
    }
    return render(request, 'exercise_plans/configurar_rutina.html', context)
            
@login_required
def editar_rutina(request, pk):
    rutina = get_object_or_404(Rutina, pk=pk)
    
    # Control de autoría estricto
    if rutina.autor != request.user:
        return redirect('exercise_plans:lista_rutinas')

    es_coach = request.user.groups.filter(name__in=['Coach', 'Administrador']).exists() or request.user.is_staff or request.user.is_superuser

    if request.method == 'POST':
        form = RutinaForm(request.POST, instance=rutina)
        formset = RutinaEjercicioFormSet(request.POST, instance=rutina)
        
        if form.is_valid() and formset.is_valid():
            rutina_editada = form.save(commit=False)
            if not es_coach:
                rutina_editada.publico = False
            rutina_editada.save()

            formset.save() 
                
            return redirect('exercise_plans:mis_rutinas')
    else:
        form = RutinaForm(instance=rutina)
        formset = RutinaEjercicioFormSet(instance=rutina)
        if not es_coach and 'publico' in form.fields:
            del form.fields['publico']
            
    context = {
        'form': form,
        'formset': formset,
        'action': 'editar',
        'rutina': rutina
    }
    return render(request, 'exercise_plans/configurar_rutina.html', context)
@login_required
def guardar_rutina(request, rutina_id):
    # Forzar a que solo se clone mediante peticiones POST por seguridad (ej. desde un botón/formulario)
    if request.method == 'POST':
        rutina_original = get_object_or_404(Rutina, id=rutina_id)
        
        # Evaluamos de inmediato los ejercicios asociados antes de perder la referencia del objeto original
        mis_ejercicios_og = list(rutina_original.rutinaejercicio_set.all())
        
        # Clonamos la rutina principal cambiando sus llaves
        rutina_original.pk = None
        rutina_original.id = None # Seteamos ambos en None para blindar la clonación en SQLite
        rutina_original.autor = request.user
        rutina_original.publico = False
        
        # 🛡️ Formateo seguro para respetar el unique=True y el max_length=100
        marca_tiempo = int(time.time()) # Inyecta un timestamp único al final
        sufijo = f" (Copia-{marca_tiempo})" # ej: (Copia-1719284210)
        
        # Recortamos el nombre original a un máximo de 75 caracteres para dejar espacio al sufijo
        nombre_recortado = rutina_original.nombre_rutina[:75]
        rutina_original.nombre_rutina = f"{nombre_recortado}{sufijo}"

        # Guardamos la nueva rutina en la BD
        rutina_original.save()
        mi_nueva_rutina = rutina_original

        # Clonamos cada uno de los ejercicios asociados al plan
        for ejercicio in mis_ejercicios_og:
            ejercicio.pk = None
            ejercicio.id = None
            ejercicio.rutina = mi_nueva_rutina
            ejercicio.save()

        messages.success(request, f"¡Has guardado una copia del plan en tu biblioteca personal!")
        return redirect('exercise_plans:mis_rutinas')
        
    return redirect('forum:board')

@login_required
def eliminar_rutina(request, pk):
    rutina = get_object_or_404(Rutina, pk=pk)
    
    # Control de seguridad: Impedir que un usuario elimine rutinas ajenas por URL directa
    if rutina.autor != request.user:
        messages.error(request, "No tienes permisos para eliminar esta rutina.")
        return redirect('exercise_plans:lista_rutinas')
        
    titulo = rutina.nombre_rutina
    rutina.delete()
    
    messages.success(request, f"La rutina '{titulo}' ha sido eliminada exitosamente.")
    return redirect('exercise_plans:lista_rutinas')