from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from .models import TipoEjercicio
from .forms import TipoEjercicioForm
from django.contrib import messages


# Create your views here.

def es_coach_o_admin(user):
    # esto es para detectar el grupo y darle o no acceso
    return user.groups.filter(name__in=['Coach', 'Administrador']).exists() or user.is_superuser or user.is_staff

@login_required
@user_passes_test(es_coach_o_admin, login_url='core:home')
def gestion_tipos_ejercicio(request):

    categorias = TipoEjercicio.objects.filter(activo=True).order_by('nombre_categoria')

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
@user_passes_test(es_coach_o_admin, login_url='core:home')
def editar_tipo_ejercicio(request, pk):

    categoria = get_object_or_404(TipoEjercicio, pk=pk, activo=True)

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
@user_passes_test(es_coach_o_admin, login_url='core:home')
@require_POST
def eliminar_tipo_ejercicio(request, pk):

    categoria = get_object_or_404(TipoEjercicio, pk=pk, activo=True)
    nombre = categoria.nombre_categoria
    categoria.delete()
    messages.success(request, f"El grupo muscular '{nombre}' ha sido eliminado exitosamente.")
    return redirect('exercise_types:gestion_tipos_ejercicio')
