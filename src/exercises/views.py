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
from .forms import ejercicioForm
# Create your views here.

@login_required
def gestion_ejercicios(request):
    lista_ejercicios = Ejercicio.objects.all()

    if request.method == 'POST':
        form = ejercicioForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_ejercicio = form.save()

            #para guardar en el historial
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
def editar_ejercicio(request, pk):
    
    ejercicio = get_object_or_404(Ejercicio, pk=pk)

    if request.method == 'POST':
        form = ejercicioForm(request.POST, request.FILES, instance=ejercicio)
        if form.is_valid():

            ejercicio_modificado = form.save(commit=False)
            #asi al ser editado por un entrenador, vuelve a requerir revision del admin
            ejercicio_modificado.autorizado = False 
            ejercicio_modificado.save()

            #se guarda la edición en el historial
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
def eliminar_ejercicio(request, pk):
    
    ejercicio = get_object_or_404(Ejercicio, pk=pk)
    nombre = ejercicio.nombre_ejercicio

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
    ejercicios = Ejercicio.objects.filter(autorizado=True)
    
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
    autores = User.objects.filter(ejercicios_creados__autorizado=True).distinct()
    
    context = {
        'ejercicios': ejercicios,
        'grupos_musculares': grupos_musculares,
        'autores': autores,
        'grupo_actual': grupo_seleccionado,
        'autor_actual': autor_seleccionado,
    }
    return render(request, 'exercises/catalogo.html', context)