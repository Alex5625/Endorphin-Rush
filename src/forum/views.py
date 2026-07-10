#from pyexpat.errors import messages 
from django.utils import timezone
from django.utils.timezone import localtime
from django.contrib import messages
from django.views.decorators.http import require_POST 
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Publicacion
from .forms import PostForm
from exercise_plans.models import Rutina, RutinaEjercicio
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from exercise_plans.models import Notificacion
from django.contrib.auth.models import User

# Create your views here.

def es_entrenador_o_admin(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser or user.groups.filter(name__in=['Coach', 'Administrador']).exists()

@login_required
def forum_board(request):
    #primero traemos todas las publicaciones
    publicaciones = Publicacion.objects.all()
    es_entrenador = es_entrenador_o_admin(request.user)

    #despues capturamos los parámetros de filtrado desde la URL
    autor_id = request.GET.get('autor')
    ordenar_por = request.GET.get('ordenar')

    # se aplica el Filtro por Autor
    if autor_id:
        publicaciones = publicaciones.filter(autor_id=autor_id)

    #aplicar Ordenamiento
    if ordenar_por == 'alfa_asc':
        publicaciones = publicaciones.order_by('titulo')
    elif ordenar_por == 'alfa_desc':
        publicaciones = publicaciones.order_by('-titulo')
    elif ordenar_por == 'antiguas':
        publicaciones = publicaciones.order_by('fecha_creacion')
    else:
        # recientes o por defecto: La fecha más nueva arriba
        publicaciones = publicaciones.order_by('-fecha_creacion')

    #Obtener solo los usuarios que han hecho al menos una publicación
    autores_foro = User.objects.filter(publicaciones__isnull=False).distinct()

    return render(request, 'forum/board.html', {
        'publicaciones': publicaciones,
        'es_entrenador': es_entrenador,
        'autores_foro': autores_foro,
        'autor_actual': autor_id,
        'orden_actual': ordenar_por
    })
@login_required
@user_passes_test(es_entrenador_o_admin, login_url='forum:board')
def crear_publicacion(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        
        # Ocultamos los "Snapshots" para que el entrenador solo vea sus rutinas vivas
        form.fields['rutina_vinculada'].queryset = Rutina.objects.filter(
            Q(autor=request.user) & Q(publico=True) & Q(es_snapshot=False)
        ).distinct()
            
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.autor = request.user
            
            rutina_viva = form.cleaned_data.get('rutina_vinculada')
            
            if rutina_viva:
                with transaction.atomic():
                    
                    fecha_version = localtime(timezone.now())
                    nombre_version = f"{rutina_viva.nombre_rutina} (v. {fecha_version})"
                    
                    # 1. Creamos la copia fotográfica (Snapshot)
                    snapshot = Rutina.objects.create(
                        nombre_rutina=nombre_version,
                        autor=rutina_viva.autor,
                        es_snapshot=True,
                        rutina_padre=rutina_viva # El cordón umbilical hacia la viva
                    )
                    
                    # 2. Le pasamos los ejercicios tal como están HOY
                    for bloque in rutina_viva.rutinaejercicio_set.all():
                        RutinaEjercicio.objects.create(
                            rutina=snapshot,
                            ejercicio=bloque.ejercicio,
                            series=bloque.series
                        )
                    
                    # 3. Pegamos el Snapshot al post y guardamos
                    new_post.rutina_vinculada = snapshot
                    new_post.save()
                    
                    # 4. ¡LA ALARMA DE NOTIFICACIONES!
                    usuarios_que_clonaron = Rutina.objects.filter(
                        rutina_padre=rutina_viva, 
                        es_snapshot=False
                    ).exclude(autor=rutina_viva.autor).values_list('autor', flat=True).distinct()
                    
                    # Ajusta 'forum:board' si tienes una URL específica para ver un solo post
                    url_post = reverse('forum:board') 
                    
                    notificaciones = [
                        Notificacion(
                            usuario_id=user_id,
                            mensaje=f"Actualización: ¡Se ha publicado una nueva versión de '{rutina_viva.nombre_rutina}'!",
                            enlace=url_post
                        ) for user_id in usuarios_que_clonaron
                    ]
                    
                    if notificaciones:
                        Notificacion.objects.bulk_create(notificaciones)
            else:
                # Si publicó texto o imagen pero sin adjuntar rutina, solo guarda el post
                new_post.save()
                
            return redirect('forum:board')
    else:
        form = PostForm()
        form.fields['rutina_vinculada'].queryset = Rutina.objects.filter(
            Q(autor=request.user) & Q(publico=True) & Q(es_snapshot=False)
        ).distinct()

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

@login_required
@user_passes_test(es_entrenador_o_admin, login_url='forum:board')
def eliminar_publicacion(request, post_id):
    # SE PONE ASI PARA MANTENER COHERENCIA DE EQUIPO. SE MODIFICARÁ A FUTURO
    # PARA HACER UN SOFT DELETE COMO SE RECOMENDÓ !!! 
    publicacion = get_object_or_404(Publicacion, id=post_id)

    if publicacion.autor != request.user:
        return redirect('forum:board')

    if request.method == 'POST':
        publicacion.delete()
        return redirect('forum:board')

    return render(request, 'forum/board.html', {'publicacion': publicacion})


@login_required
@require_POST
def adoptar_rutina_foro(request, publicacion_id):
    # Buscamos la publicación que el usuario está viendo
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    snapshot_del_foro = publicacion.rutina_vinculada

    if not snapshot_del_foro:
        messages.error(request, "Esta publicación no tiene una rutina vinculada.")
        return redirect('forum:inicio_foro')

    # evitamos nombres duplicados para el usuario que adopta la rutina del foro
    nombre_base = snapshot_del_foro.nombre_rutina
    nombre_final = nombre_base
    contador = 1
    
    # Mientras exista una rutina con ese nombre para este usuario, le cambiamos el nombre
    while Rutina.objects.filter(autor=request.user, nombre_rutina=nombre_final).exists():
        nombre_final = f"{nombre_base} (Copia {contador})"
        contador += 1
    # -------------------------------------------------------------------------

    try:
        # se crea la copia "Viva" para el usuario común con el nombre validado
        nueva_rutina_usuario = Rutina.objects.create(
            nombre_rutina=nombre_final,
            autor=request.user, 
            es_snapshot=False,  
            rutina_padre=snapshot_del_foro.rutina_padre if snapshot_del_foro.rutina_padre else snapshot_del_foro
        )

        # se clona los bloques de ejercicios
        for bloque in snapshot_del_foro.rutinaejercicio_set.all():
            RutinaEjercicio.objects.create(
                rutina=nueva_rutina_usuario,
                ejercicio=bloque.ejercicio,
                series=bloque.series
            )

        messages.success(request, f"¡Excelente! La rutina '{nueva_rutina_usuario.nombre_rutina}' se ha guardado en tu agenda.")
        return redirect('exercise_plans:mis_rutinas') 
        
    except ValidationError as e:
        # Escudo defensivo final por si otra validación falla
        messages.error(request, f"No se pudo guardar la rutina: {e}")
        return redirect('forum:inicio_foro')