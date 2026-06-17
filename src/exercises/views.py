from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Ejercicio
from core.models import HistorialAcciones
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

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
