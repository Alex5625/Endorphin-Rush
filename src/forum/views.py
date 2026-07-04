from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Publicacion
from .forms import PostForm
from exercise_plans.models import Rutina
from django.db.models import Q

# Create your views here.

def es_entrenador_o_admin(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser or user.groups.filter(name__in=['Coach', 'Administrador']).exists()

@login_required
def forum_board(request):
    publicaciones = Publicacion.objects.all()
    es_entrenador = es_entrenador_o_admin(request.user)

    return render(request, 'forum/board.html', {
        'publicaciones': publicaciones,
        'es_entrenador': es_entrenador
    })

@login_required
@user_passes_test(es_entrenador_o_admin, login_url='forum:board')
def crear_publicacion(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        
        form.fields['rutina_vinculada'].queryset = Rutina.objects.filter(
            Q(autor=request.user) & Q(publico=True)).distinct()
            
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.autor = request.user
            new_post.save()
            return redirect('forum:board')
    else:
        form = PostForm()
        form.fields['rutina_vinculada'].queryset = Rutina.objects.filter(
            Q(autor=request.user) & Q(publico=True)).distinct()

    return render(request, 'forum/create_post.html', {'form':form}) 


@login_required
@user_passes_test(es_entrenador_o_admin, login_url='forum:board')
def editar_publicacion(request, post_id):
    
    publicacion = get_object_or_404(Publicacion, id=post_id)

    if publicacion.autor != request.user:
        return redirect('forum:board')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=publicacion)
        
        rutina_qs = Rutina.objects.filter(Q(autor=request.user) & Q(publico=True))

        if publicacion.rutina_vinculada_id:
            rutina_qs = (rutina_qs | Rutina.objects.filter(id=publicacion.rutina_vinculada_id, autor=request.user))
        form.fields['rutina_vinculada'].queryset = Rutina.objects.filter(
            Q(autor=request.user) & Q(publico=True)
        ).distinct()

        if form.is_valid():
            form.save()
            return redirect('forum:board')

    else:
        form = PostForm(instance=publicacion)
        rutina_qs = Rutina.objects.filter(Q(autor=request.user) & Q(publico=True))
        if publicacion.rutina_vinculada_id:
            rutina_qs = (rutina_qs | Rutina.objects.filter(id=publicacion.rutina_vinculada_id, autor=request.user))
        form.fields['rutina_vinculada'].queryset = rutina_qs.distinct()
    return render(request, 'forum/create_post.html', {'form':form, 'publicacion': publicacion})