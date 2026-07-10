from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import RestrictedError
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import RutinaForm, RutinaEjercicioFormSet
from .models import Rutina
import json
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
    rutinas_propias = Rutina.objects.filter(autor=request.user, activa=True)
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
        
        # print("🔍 DATOS QUE ENVIÓ EL NAVEGADOR:", request.POST)
        
        if form.is_valid() and formset.is_valid():
            rutina_editada = form.save(commit=False)
            if not es_coach:
                rutina_editada.publico = False
            rutina_editada.save()

            formset.save() 
                
            return redirect('exercise_plans:mis_rutinas')
        # else:
            
        #     print("\n" + "="*40)
        #     print("❌ ERRORES DEL FORMULARIO:", form.errors)
        #     print("❌ ERRORES NON-FIELD:", form.non_field_errors())
        #     print("❌ ERRORES DEL FORMSET:", formset.errors)
        #     print("="*40 + "\n")
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


@login_required
@require_POST
def eliminar_rutina(request, pk):
    rutina = get_object_or_404(Rutina, pk=pk, autor=request.user)

    # En lugar de destruir (rutina.delete()), simplemente "apagamos" la rutina
    rutina.activa = False
    
    # Opcional pero recomendado: Quitarla de la agenda semanal si estaba programada
    rutina.lunes = False
    rutina.martes = False
    rutina.miercoles = False
    rutina.jueves = False
    rutina.viernes = False
    rutina.sabado = False
    rutina.domingo = False
    
    rutina.save()

    messages.success(request, f"La rutina '{rutina.nombre_rutina}' fue archivada. Tu historial de pesos se mantiene intacto.")
    return redirect('exercise_plans:mis_rutinas')

@login_required
def papelera_rutinas(request):
    # Filtramos solo las rutinas inactivas del usuario
    rutinas_archivadas = Rutina.objects.filter(autor=request.user, activa=False).order_by('-id')
    
    context = {
        'rutinas': rutinas_archivadas,
        'titulo': 'Papelera de Rutinas'
    }
    return render(request, 'exercise_plans/papelera_rutinas.html', context)

@login_required
@require_POST 
def restaurar_rutina(request, pk):
    rutina = get_object_or_404(Rutina, pk=pk, autor=request.user)
    
    # Volvemos a encender el interruptor
    rutina.activa = True
    rutina.save()
    
    messages.success(request, f"¡La rutina '{rutina.nombre_rutina}' ha sido restaurada con éxito! Ya puedes verla en tu listado principal.")
    return redirect('exercise_plans:papelera_rutinas')

@require_POST
@login_required
def eliminar_recordatorios_ajax(request, rutina_id):
    # print(f"🚀 ¡AJAX llegó a la vista! Intentando modificar rutina ID: {rutina_id}")
    # print(f"👤 Usuario actual: {request.user.username} (ID: {request.user.id})")
    
    # Buscamos la rutina SIN el filtro de autor para ver si existe
    rutina_existe = Rutina.objects.filter(id=rutina_id).first()
    
    if not rutina_existe:
        print("❌ La rutina no existe en la base de datos.")
        return JsonResponse({'status': 'error', 'mensaje': 'La rutina no existe.'}, status=404)
        
    # print(f"📝 Autor de la rutina: {rutina_existe.autor.username} (ID: {rutina_existe.autor.id})")
    
    # Aquí es donde fallaba tu código original
    if rutina_existe.autor != request.user:
        print("⛔ ERROR: El usuario actual NO es el dueño de esta rutina.")
        return JsonResponse({'status': 'error', 'mensaje': 'No tienes permiso para modificar esta rutina.'}, status=403)

    # Si pasamos las validaciones, procedemos a borrar
    try:
        data = json.loads(request.body)
        tipo = data.get('tipo')
        # print(f"✅ Permiso concedido. Eliminando tipo: {tipo}")

        if tipo in ['correo', 'ambos']:
            rutina_existe.recordatorio_correo = False
            rutina_existe.hora_correo = None
            
        if tipo in ['popup', 'ambos']:
            rutina_existe.recordatorio_popup = False
            rutina_existe.hora_popup = None

        rutina_existe.save()
        return JsonResponse({'status': 'success', 'mensaje': 'Recordatorios actualizados.'})
    
    except Exception as e:
        print(f"💥 Error en el proceso: {str(e)}")
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)