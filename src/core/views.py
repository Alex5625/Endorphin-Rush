from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from core.models import HistorialAcciones, SesionEntrenamiento
from exercises.models import Ejercicio
from exercise_plans.models import Rutina
from datetime import datetime, timedelta
from django.utils import timezone
from .models import SesionEntrenamiento, RegistroSerie
import json
from django.db.models import Avg

def home(request):
    context = {}
    
    if request.user.is_authenticated:
        # Obtenemos TODAS las rutinas del usuario en una sola consulta a la base de datos
        rutinas_usuario = list(Rutina.objects.filter(autor=request.user))
        
        # Armamos el calendario buscando en la lista en memoria usando 'next'
        agenda = {
            'Lunes': next((r for r in rutinas_usuario if r.lunes), None),
            'Martes': next((r for r in rutinas_usuario if r.martes), None),
            'Miércoles': next((r for r in rutinas_usuario if r.miercoles), None),
            'Jueves': next((r for r in rutinas_usuario if r.jueves), None),
            'Viernes': next((r for r in rutinas_usuario if r.viernes), None),
            'Sábado': next((r for r in rutinas_usuario if r.sabado), None),
            'Domingo': next((r for r in rutinas_usuario if r.domingo), None),
        }
        
        context['agenda'] = agenda

        ##logica para hu-24: incio rapido diario

        #1. saber q dia es hoy mapeado exacto a las llaves de la agenda creada
        dias_semana =['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        hoy_index = datetime.today().weekday()      ##0=Lunes,  6=Domingo
        dia_actual_str = dias_semana[hoy_index]

        #2. extraer la rutina de hoy directamente de la agenda
        rutina_hoy = agenda[dia_actual_str]
        sesion_activa = None

        #3. buscar si el usuario tiene una sesion sin terminar
        sesion_pendiente = SesionEntrenamiento.objects.filter(
            usuario=request.user,
            fecha_fin__isnull=True
        ).first()

        if sesion_pendiente:
            if not sesion_pendiente.esta_activa:
                sesion_pendiente.cerrar_sesion()        #se cierra automaticamente si pasaron 3 horas
            else:
                sesion_activa = sesion_pendiente    #sigue activa
        
        #se guarda en el context para usarlo en el html
        context['rutina_hoy']= rutina_hoy
        context['sesion_activa']= sesion_activa
        
        #principio de popup de notificaciones
        agenda_dict = {}
        for dia, rutina in agenda.items():
            if rutina:
                hora_str = rutina.hora_popup.strftime('%H:%M') if rutina.hora_popup else None
                agenda_dict[dia] = {
                    'nombre': rutina.nombre_rutina,
                    'descripcion': rutina.descripcion_rutina,
                    'usa_popup': rutina.recordatorio_popup,
                    'hora': hora_str
                }
            else:
                agenda_dict[dia] = None
        
        # Lo metemos al contexto junto a lo que ya tenías
        context['agenda_dict'] = agenda_dict
        
        # EL PRINT DE LA VERDAD
        print("\n" + "="*40)
        print("📦 DICCIONARIO PARA JS CREADO CORRECTAMENTE EN HOME:")
        print(agenda_dict.get('Martes'))
        print("="*40 + "\n")

    return render(request, 'core/home.html', context)


##vistas exclusivas del admin

def es_admin_o_staff(user):
    if not user.is_authenticated:
        return False
    # staff nativo de django, super user o administrador del gimnasio (grupos)
    return user.is_staff or user.groups.filter(name='Administrador').exists() or user.is_superuser

@login_required
@user_passes_test(es_admin_o_staff, login_url='core:home')
@require_POST
def autorizar_ejercicio(request, pk, accion):

##Vista para que el admin apruebe o rechace un ejercicio.
###accion q puede ser aprobar o rechazar.

    ejercicio = get_object_or_404(Ejercicio, pk=pk)
    
    if accion == 'aprobar':
        ejercicio.autorizado = True
        ejercicio.save()
        
        HistorialAcciones.objects.create(
            usuario=request.user,
            accion="Ejercicio Aprobado",
            detalle=f"El administrador aprobó el ejercicio '{ejercicio.nombre_ejercicio}'."
        )
        messages.success(request, f"El ejercicio '{ejercicio.nombre_ejercicio}' ha sido aprobado.")
        
    elif accion == 'rechazar':
        nombre_ejercicio = ejercicio.nombre_ejercicio
        ejercicio.delete() #si se rechaza, se elimina para que el entrenador lo suba bien
        
        HistorialAcciones.objects.create(
            usuario=request.user,
            accion="Ejercicio Rechazado",
            detalle=f"El administrador rechazó y eliminó el ejercicio '{nombre_ejercicio}'."
        )
        messages.warning(request, f"El ejercicio '{nombre_ejercicio}' ha sido rechazado y removido.")
        
    return redirect('exercises:lista_ejercicios')


@login_required
@user_passes_test(es_admin_o_staff, login_url='core:home')

def panel_auditoria(request):
###Vista del panel exclusivo para que el admin vea todo el historial de movimientos

    logs = HistorialAcciones.objects.all() #viene ordenado por fecha desde el modelo
    return render(request, 'core/panel_auditoria.html', {'logs': logs})

# 1- Vista para listar los ejercicios que esperan aprobación

@login_required
@user_passes_test(es_admin_o_staff, login_url='core:home')
def panel_pendientes(request):
    ejercicios_pendientes = Ejercicio.objects.filter(autorizado=False)
    return render(request, 'core/panel_pendientes.html', {'ejercicios': ejercicios_pendientes})

# 2- Vista que procesa el botón de Aprobar o Rechazar
@login_required
@user_passes_test(es_admin_o_staff, login_url='core:home')
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
            
    return redirect('core:panel_pendientes')


#Nueva vista para la HU-24: control del boton:)
@login_required
def cambiar_estado_sesion(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id, autor=request.user)
    
    #1.buscamos si el usuario ya está entrenando en este momento
    sesion_activa = SesionEntrenamiento.objects.filter(
        usuario=request.user, 
        fecha_fin__isnull=True
    ).first()

    if sesion_activa:
        #2. si el boton se presiona y hay sesion activa, significa TERMINAR
        sesion_activa.cerrar_sesion()
        messages.success(request, f"¡Excelente trabajo! Has finalizado tu rutina de {rutina.nombre_rutina}.")
        
        #redirigidimos al inicio despues de cerrar
        return redirect('core:home')
 
    else:
        #3. si el boton se presiona y NO HAY sesion, entonces significa INICIAR
        nueva_sesion = SesionEntrenamiento.objects.create(
            usuario=request.user,
            rutina = rutina
        )   
        messages.success(request, f"¡Sesión iniciada! A darle con todo a {rutina.nombre_rutina}.")
        #redirigimos al modo de ejecucion
        return redirect('core:ejecutar_entrenamiento', sesion_id=nueva_sesion.id)
    


##para la ejecución del entrenamiento 
@login_required
def ejecutar_entrenamiento(request, sesion_id):
    # 1. Buscamos la sesión activa en la base de datos
    sesion = get_object_or_404(SesionEntrenamiento, id=sesion_id, usuario=request.user)
    
    # 2. Obtenemos la rutina asociada a esta sesión
    rutina = sesion.rutina 

    # Armamos una lista dinámica con los bloques y sus pesos guardados
    bloques_con_series = []
    for bloque in rutina.rutinaejercicio_set.all():
        series_data = []
        for i in range(1, bloque.series + 1):
            # Buscamos si ya existe un peso guardado en la base de datos
            registro = RegistroSerie.objects.filter(sesion=sesion, bloque=bloque, numero_serie=i).first()
            
            #se fuerza el punto decimal
            if registro and registro.peso_levantado is not None:
                peso = str(registro.peso_levantado).replace(',', '.')
            else:
                peso = ""
            
            series_data.append({'numero': i, 'peso': peso})
        
        bloques_con_series.append({
            'bloque': bloque,
            'series_data': series_data
        })

    return render(request, 'core/ejecucion_entrenamiento.html', {
        'sesion': sesion,
        'rutina': rutina,
        'bloques_con_series': bloques_con_series 
    })


@login_required
def guardar_peso(request, sesion_id, bloque_id):
    if request.method == 'POST':
        from exercise_plans.models import RutinaEjercicio
        
        sesion = get_object_or_404(SesionEntrenamiento, id=sesion_id, usuario=request.user)
        # Nota: Si RutinaEjercicio no tiene un campo 'usuario' directo (sino que pasa por Rutina), 
        # asegúrate de que esta validación funcione en tu modelo, o cámbiala a `rutina__usuario=request.user`.
        bloque = get_object_or_404(RutinaEjercicio, id=bloque_id, rutina__autor=request.user)
        
        # Recorremos el número de series para atrapar cada caja de texto
        for i in range(1, bloque.series + 1):
            peso_str = request.POST.get(f'peso_serie_{i}')
            if peso_str: # Solo guardamos si el usuario de verdad escribió algo
                try:
                    RegistroSerie.objects.update_or_create(
                        sesion=sesion,
                        bloque=bloque,
                        numero_serie=i,
                        defaults={'peso_levantado': float(peso_str)}
                    )
                except MultipleObjectsReturned:
                    # Si el ORM detecta filas duplicadas por un error previo de concurrencia,
                    # se capturan todas esas filas corruptas.
                    registros_duplicados = RegistroSerie.objects.filter(
                        sesion=sesion, 
                        bloque=bloque, 
                        numero_serie=i
                    )
                    
                    # Nos quedamos con el primer registro válido y lo actualizamos con el nuevo peso
                    registro_valido = registros_duplicados.first()
                    registro_valido.peso_levantado = float(peso_str)
                    registro_valido.save()
                    
                    # Eliminamos silenciosamente el resto de registros duplicados 
                    # para que la base de datos vuelva a estar limpia
                    registros_duplicados.exclude(id=registro_valido.id).delete()
        
        # se redirecciona de vuelta a la misma pantalla para que siga entrenando
        return redirect('core:ejecutar_entrenamiento', sesion_id=sesion.id)
        
    return redirect('core:home')

# AQUI INICIA HISTORIAL DE ENTRENAMIENTOS

def datos_calendario_historial(usuario):
    sesiones = SesionEntrenamiento.objects.filter(
        usuario=usuario
    ).select_related(
        'rutina'
    ).prefetch_related(
        'registroserie_set__bloque__ejercicio'
    ).order_by('fecha_inicio')

    historial_calendario = []
    for sesion in sesiones:
        historial_calendario.append({
            'id': str(sesion.id),
            'title': sesion.rutina.nombre_rutina,
            'start': sesion.fecha_inicio.isoformat(),
            'allDay': False
        })

    return sesiones, historial_calendario

def datos_stats_entrenamiento(usuario, dias):
    fecha_filtrada= timezone.now() - timedelta (days=dias)

    sesiones = SesionEntrenamiento.objects.filter(
        usuario = usuario,
        registroserie__peso_levantado__isnull = False,
        fecha_inicio__gte=fecha_filtrada,
    ).annotate(
        peso_promedio=Avg('registroserie__peso_levantado')
    ).order_by('fecha_inicio')

    fechas_x = []
    pesos_y = []

    for sesion in sesiones:
        fechas_x.append(sesion.fecha_inicio.strftime('%d %b'))
        pesos_y.append(round(float(sesion.peso_promedio), 2))
    
    return fechas_x, pesos_y


@login_required
def historial_entrenamiento(request):
    dias_filtro = int(request.GET.get('dias', 30))
    sesiones, historial_calendario = datos_calendario_historial(request.user)
    fechas_x, pesos_y = datos_stats_entrenamiento(request.user, dias_filtro)

    return render(request, 'core/historial.html', {
        'sesiones': sesiones,
        'historial_json': historial_calendario,
        'fechas_json': fechas_x,
        'pesos_json': pesos_y,
        'dias_actual': dias_filtro

    })