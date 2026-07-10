from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Ejercicio
from core.models import HistorialAcciones
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from exercise_types.models import TipoEjercicio
from django.views.decorators.http import require_POST
from .forms import ejercicioForm
# Create your views here.

def es_coach_o_admin(user):
    # esto es para detectar el grupo y darle o no acceso
    return user.groups.filter(name__in=['Coach', 'Administrador']).exists() or user.is_superuser or user.is_staff

@login_required
@user_passes_test(es_coach_o_admin, login_url='core:home')
def gestion_ejercicios(request):
    lista_ejercicios = Ejercicio.objects.filter(activo=True).order_by('nombre_ejercicio')

    if request.method == 'POST':
        form = ejercicioForm(request.POST, request.FILES)
        if form.is_valid():
            # CORRECCIÓN 1: Pausamos el guardado para inyectar al autor
            nuevo_ejercicio = form.save(commit=False)
            nuevo_ejercicio.autor = request.user 
            nuevo_ejercicio.autorizado = False  # Aseguramos que inicie pendiente
            nuevo_ejercicio.save()

            HistorialAcciones.objects.create(
                usuario=request.user,
                accion="Creación de Ejercicio (Pendiente)",
                detalle=f"El entrenador {request.user.username} creó el ejercicio '{nuevo_ejercicio.nombre_ejercicio}' (Falta aprobación)."
            )

            messages.success(request, "Ejercicio creado exitosamente!")
            return redirect('exercises:lista_ejercicios')
    else:
        form = ejercicioForm()

    contexto = {
        'form': form,
        'lista_ejercicios': lista_ejercicios
    }

    return render(request, 'exercises/lista_ejercicios.html', contexto)

# HU-07 permite al entrenador editar un ejercicio existente
@login_required
@user_passes_test(es_coach_o_admin, login_url='core:home')
def editar_ejercicio(request, pk):
    ejercicio = get_object_or_404(Ejercicio, pk=pk, activo=True)

    # CORRECCIÓN 2: Candado de seguridad para que nadie más entre por URL
    if ejercicio.autor != request.user and not request.user.is_staff:
        messages.error(request, "Acceso denegado: No puedes editar un ejercicio que no creaste.")
        return redirect('exercises:lista_ejercicios')
        
    if request.method == 'POST':
        form = ejercicioForm(request.POST, request.FILES, instance=ejercicio)
        if form.is_valid():
            ejercicio_modificado = form.save(commit=False)
            ejercicio_modificado.autorizado = False 
            ejercicio_modificado.save()

            HistorialAcciones.objects.create(
                usuario=request.user,
                accion="Modificación de Ejercicio (Pendiente)",
                detalle=f"El entrenador {request.user.username} editó '{ejercicio_modificado.nombre_ejercicio}'. Volvió a estado Pendiente de revisión."
            )

            messages.success(request, "Ejercicio actualizado exitosamente y enviado a revisión!")
            return redirect('exercises:lista_ejercicios')
        
    else:
        form= ejercicioForm(instance=ejercicio)

    return render(request, 'exercises/editar_ejercicio.html', {'form': form, 'ejercicio': ejercicio})

@login_required
@user_passes_test(es_coach_o_admin, login_url='core:home')
@require_POST
def eliminar_ejercicio(request, pk):
    
    ejercicio = get_object_or_404(Ejercicio, pk=pk, activo=True)
    nombre = ejercicio.nombre_ejercicio

    if ejercicio.autor != request.user and not request.user.is_staff:
        messages.error(request, "Acceso denegado: No puedes eliminar un ejercicio que no creaste.")
        return redirect('exercises:lista_ejercicios')
    
    #se deja registro en el historial antes de borrarlo
    HistorialAcciones.objects.create(
        usuario=request.user,
        accion="Ejercicio Eliminado",
        detalle=f"Se eliminó el ejercicio '{nombre}' del sistema."
    )

    ejercicio.delete()
    messages.success(request, f"El ejercicio '{nombre}' ha sido eliminado exitosamente.")
    return redirect('exercises:lista_ejercicios')

## para la hu-11 de visualización del catalago de ejercicios
## se modifica la funcion para el cumplimiento de la hu-12
## HU-12 Catálogo de Ejercicios con Filtros de grupos musculares y autor
def catalogo_ejercicios(request):
    #base inicial: solo ejercicios aprobados
    ejercicios = Ejercicio.objects.filter(autorizado=True, activo=True).order_by('nombre_ejercicio')
    
    #se capturan filtros desde la URL
    grupo_seleccionado = request.GET.get('grupo')
    autor_seleccionado = request.GET.get('autor')
    
    #se aplica filtro de grupo muscular si existe
    if grupo_seleccionado:
        ejercicios = ejercicios.filter(tipo_ejercicio__id=grupo_seleccionado)
        
    #se aplica filtro de autor si existe
    if autor_seleccionado:
        ejercicios = ejercicios.filter(autor__id=autor_seleccionado)
        
    # Consultas para armar los selectores de la interfaz
    grupos_musculares = TipoEjercicio.objects.all().order_by('nombre_categoria')
    autores = User.objects.filter(ejercicios_creados__autorizado=True, ejercicios_creados__activo=True).distinct()    
    context = {
        'ejercicios': ejercicios,
        'grupos_musculares': grupos_musculares,
        'autores': autores,
        'grupo_actual': grupo_seleccionado,
        'autor_actual': autor_seleccionado,
    }
    return render(request, 'exercises/catalogo.html', context)