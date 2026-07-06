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
        rutina_base = Rutina(autor=request.user)
        
        form = RutinaForm(request.POST, instance=rutina_base)
        formset = RutinaEjercicioFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            rutina = form.save(commit=False)
            
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
    if request.method == 'POST':
        # 🛡️ FIX IDOR: Solo permitimos clonar si es pública o si le pertenece al usuario
        rutina_original = get_object_or_404(
            Rutina, 
            Q(id=rutina_id) & (Q(publico=True) | Q(autor=request.user))
        )
        mis_ejercicios_og = list(rutina_original.rutinaejercicio_set.all())
        
        rutina_original.pk = None
        rutina_original.id = None 
        rutina_original.autor = request.user
        rutina_original.publico = False
        
        # 🛡️ Limpiamos la agenda para que no choque con los días del usuario que clona
        rutina_original.lunes = False
        rutina_original.martes = False
        rutina_original.miercoles = False
        rutina_original.jueves = False
        rutina_original.viernes = False
        rutina_original.sabado = False
        rutina_original.domingo = False
        
        marca_tiempo = int(time.time())
        sufijo = f" (Copia-{marca_tiempo})" 
        nombre_recortado = rutina_original.nombre_rutina[:75]
        rutina_original.nombre_rutina = f"{nombre_recortado}{sufijo}"

        rutina_original.save()
        mi_nueva_rutina = rutina_original

        for ejercicio in mis_ejercicios_og:
            ejercicio.pk = None
            ejercicio.id = None
            ejercicio.rutina = mi_nueva_rutina
            ejercicio.save()

        messages.success(request, f"¡Has guardado una copia del plan en tu biblioteca personal!")
        return redirect('exercise_plans:mis_rutinas')
        
    return redirect('forum:board')

# Esta es la vista que debe renderizar el home.html
def home_view(request):
    context = {}
    if request.user.is_authenticated:
        rutinas_usuario = Rutina.objects.filter(autor=request.user)
        
        # Estructuramos un diccionario con la rutina asignada a cada día
        # Usamos .first() porque nuestro modelo ya garantiza que solo haya 1 por día
        agenda = {
            'Lunes': rutinas_usuario.filter(lunes=True).first(),
            'Martes': rutinas_usuario.filter(martes=True).first(),
            'Miércoles': rutinas_usuario.filter(miercoles=True).first(),
            'Jueves': rutinas_usuario.filter(jueves=True).first(),
            'Viernes': rutinas_usuario.filter(viernes=True).first(),
            'Sábado': rutinas_usuario.filter(sabado=True).first(),
            'Domingo': rutinas_usuario.filter(domingo=True).first(),
        }
        context['agenda'] = agenda
        
    return render(request, 'core/home.html', context)

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