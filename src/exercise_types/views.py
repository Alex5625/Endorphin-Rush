from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import TipoEjercicio
from .forms import TipoEjercicioForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def gestion_tipos_ejercicio(request):

    categorias = TipoEjercicio.objects.all().order_by('nombre_categoria')

    if request.method== 'POST':
        form = TipoEjercicioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Grupo muscular agregado exitosamente!")
            return redirect('exercise_types:gestion_tipos_ejercicio')

    else:
        form = TipoEjercicioForm()

    context = {
        'categorias': categorias,
        'form': form
    }
    return render(request, 'exercise_types/gestion_tipos.html', context)

#hu-30 permite al entrenador modificar el nombre de un grupo muscular existente
@login_required
def editar_tipo_ejercicio(request, pk):

    categoria = get_object_or_404(TipoEjercicio, pk=pk)

    if request.method == 'POST':
        form = TipoEjercicioForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Grupo muscular actualizado exitosamente!")
            return redirect('exercise_types:gestion_tipos_ejercicio')

    else:
        form= TipoEjercicioForm(instance=categoria)

    return render(request, 'exercise_types/editar_tipo.html', {'form': form, 'categoria': categoria})

#HU-31 permite al entrenador eliminar un grupo muscular en forma directa.
@login_required
def eliminar_tipo_ejercicio(request, pk):

    categoria = get_object_or_404(TipoEjercicio, pk=pk)
    nombre = categoria.nombre_categoria
    categoria.delete()
    messages.success(request, f"El grupo muscular '{nombre}' ha sido eliminado exitosamente.")
    return redirect('exercise_types:gestion_tipos_ejercicio')
