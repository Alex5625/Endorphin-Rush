from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    #Se agrega la ruta para la vista home, que es la página de inicio a la que se redirige después de iniciar sesión o registrarse
    path('', views.home, name='home'),

    #HU-09: Historial de Acciones y auditoria
    path('panel-auditoria/', views.panel_auditoria, name='panel_auditoria'),

    #HU-10: Autorización de Ejercicios
    path('ejercicio/<int:pk>/<str:accion>/', views.autorizar_ejercicio, name='autorizar_ejercicio'),

    path('panel-control/pendientes/', views.panel_pendientes, name='panel_pendientes'),
    path('panel-control/procesar/<int:pk>/', views.procesar_ejercicio, name='procesar_ejercicio'),

    # HU-24: Inicio Rápido Diario
    path('sesion/cambiar-estado/<int:rutina_id>/', views.cambiar_estado_sesion, name='cambiar_estado_sesion'),

    #para ejecución de entrenamiento
    path('ejecucion/<int:sesion_id>/', views.ejecutar_entrenamiento, name='ejecutar_entrenamiento'),

    #para guardar el peso de un bloque de entrenamiento
    path('sesion/<int:sesion_id>/guardar-peso/<int:bloque_id>/', views.guardar_peso, name='guardar_peso'),

    #para guardar el peso de un bloque de entrenamiento
    path('historial/', views.historial_entrenamiento, name='historial'),
    
    #para ver la notificación y marcarla como leída
    path('notificacion/leer/<int:notificacion_id>/', views.leer_notificacion, name='leer_notificacion'),

 ] 
