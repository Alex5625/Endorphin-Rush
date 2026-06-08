from django.urls import path
from . import views

urlpatterns = [
    #Se agrega la ruta para la vista home, que es la página de inicio a la que se redirige después de iniciar sesión o registrarse
    path('', views.home, name='home'),

    # HU-02: Edición de perfil de usuario (solo datos corporales/personales)
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    
    # HU-03: Eliminación de perfil de usuario (desactivación de cuenta)
    path('eliminar-perfil/', views.eliminar_perfil, name='eliminar_perfil'),
    
    # HU-29: Gestión y creación de tipos de ejercicio
    path('gestion-tipos/', views.gestion_tipos_ejercicio, name='gestion_tipos_ejercicio'),
    
    # HU-30: Edición de tipo de ejercicio (recibe el ID/pk de la categoría)
    path('gestion-tipos/editar/<int:pk>/', views.editar_tipo_ejercicio, name='editar_tipo_ejercicio'),
    
    # HU-31: Eliminación de tipo de ejercicio (recibe el ID/pk de la categoría)
    path('gestion-tipos/eliminar/<int:pk>/', views.eliminar_tipo_ejercicio, name='eliminar_tipo_ejercicio'),
    
]
