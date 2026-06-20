from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    #Se agrega la ruta para la vista home, que es la página de inicio a la que se redirige después de iniciar sesión o registrarse
    path('', views.home, name='home'),

    # # HU-02: Edición de perfil de usuario (solo datos corporales/personales)
    # path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    
    # # HU-03: Eliminación de perfil de usuario (desactivación de cuenta)
    # path('eliminar-perfil/', views.eliminar_perfil, name='eliminar_perfil'),
    
    #HU-09: Historial de Acciones y auditoria
    path('panel-auditoria/', views.panel_auditoria, name='panel_auditoria'),

    #HU-10: Autorización de Ejercicios
    path('ejercicio/<int:pk>/<str:accion>/', views.autorizar_ejercicio, name='autorizar_ejercicio'),

    path('panel-control/pendientes/', views.panel_pendientes, name='panel_pendientes'),
    path('panel-control/procesar/<int:pk>/', views.procesar_ejercicio, name='procesar_ejercicio'),


#     # HU-29: Gestión y creación de tipos de ejercicio
#     path('gestion-tipos/', views.gestion_tipos_ejercicio, name='gestion_tipos_ejercicio'),
    
#     # HU-30: Edición de tipo de ejercicio (recibe el ID/pk de la categoría)
#     path('gestion-tipos/editar/<int:pk>/', views.editar_tipo_ejercicio, name='editar_tipo_ejercicio'),
    
#     # HU-31: Eliminación de tipo de ejercicio (recibe el ID/pk de la categoría)
#     path('gestion-tipos/eliminar/<int:pk>/', views.eliminar_tipo_ejercicio, name='eliminar_tipo_ejercicio'),

#     # HU-06: Creación de ejercicios
#     path('lista-ejercicios/', views.gestion_ejercicios, name='lista_ejercicios'),    

#     # HU-07: Edición de ejercicios (recibe el ID/pk del ejercicio)
#     path('lista-ejercicios/editar/<int:pk>/', views.editar_ejercicio, name='editar_ejercicio'),

#     # HU-08: Eliminación de ejercicios (recibe el ID/pk del ejercicio)
#     path('lista-ejercicios/eliminar/<int:pk>/', views.eliminar_ejercicio, name='eliminar_ejercicio'),
 ] 
