from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Ejercicio
from core.models import HistorialAcciones
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import redirect
from django.core.mail import send_mail

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

##para la autorizacion de ejercicios

#filtro de seguridad: para q solo entren los administradores 
def es_administrador(user):
    return user.is_staff or user.is_superuser

# 1- Vista para listar los ejercicios que esperan aprobación
@login_required
@user_passes_test(es_administrador)
def panel_pendientes(request):
    ejercicios_pendientes = Ejercicio.objects.filter(autorizado=False)
    return render(request, 'exercises/panel_pendientes.html', {'ejercicios': ejercicios_pendientes})

# 2- Vista que procesa el botón de Aprobar o Rechazar
@login_required
@user_passes_test(es_administrador)
def procesar_ejercicio(request, pk):
    ejercicio = get_object_or_404(Ejercicio, pk=pk)
    
    #obtenemos el correo del autor si existe, sino usamos uno de respaldo
    email_entrenador = ejercicio.autor.email if ejercicio.autor and ejercicio.autor.email else "entrenador_anonimo@correo.com"

    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'aprobar':
            ejercicio.autorizado = True
            ejercicio.save()
            
            #se registra en el Historial
            HistorialAcciones.objects.create(
                usuario=request.user,
                accion="Aprobación de Ejercicio",
                detalle=f"Se ha autorizado el ejercicio '{ejercicio.nombre_ejercicio}' para el catálogo público."
            )
            
            #se envia el Correo de aprobación
            send_mail(
                subject='¡Tu ejercicio ha sido aprobado! - Equipo Endorphin Rush',
                message=f"Hola,\n\nTe informamos que tu propuesta de ejercicio '{ejercicio.nombre_ejercicio}' ha sido aprobada por el administrador y ya está disponible en el catálogo público.\n\n¡Gracias por tu colaboración!",
                from_email=None,
                recipient_list=[email_entrenador],
                fail_silently=False,
            )
            
            messages.success(request, f"El ejercicio '{ejercicio.nombre_ejercicio}' ha sido aprobado con éxito.")
            
        elif accion == 'rechazar':
            motivo = request.POST.get('motivo_rechazo', 'No cumple con los estándares requeridos.')
            nombre_respaldo = ejercicio.nombre_ejercicio
            
            #se registra antes de borrarlo
            HistorialAcciones.objects.create(
                usuario=request.user,
                accion="Rechazo de Ejercicio",
                detalle=f"Se rechazó y eliminó el ejercicio '{nombre_respaldo}'. Motivo: {motivo}"
            )
            
            #enviar Correo de Rechazo con la retroalimentación dando el motivo de rechazo
            send_mail(
                subject='Actualización sobre tu propuesta de ejercicio - Endorphin Rush',
                message=f"Hola,\n\nLamentamos informarte que tu propuesta de ejercicio '{nombre_respaldo}' no fue aprobada.\n\nRetroalimentación del Administrador:\n\"{motivo}\"\n\nTe invitamos a revisar estas correcciones y volver a postular tu ejercicio en el futuro.\n\nSaludos cordiales,\nEquipo de Administración.",
                from_email=None,
                recipient_list=[email_entrenador],
                fail_silently=False,
            )
            
            #se elimina al ser rechazado 
            ejercicio.delete()
            
            messages.warning(request, f"El ejercicio '{nombre_respaldo}' ha sido rechazado y eliminado del sistema.")
            
    return redirect('exercises:panel_pendientes')