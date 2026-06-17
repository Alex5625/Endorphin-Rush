from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'exercise_types'

urlpatterns = [
    # HU-29: Gestión y creación de tipos de ejercicio
    path('gestion-tipos/', views.gestion_tipos_ejercicio, name='gestion_tipos_ejercicio'),
    
    # HU-30: Edición de tipo de ejercicio (recibe el ID/pk de la categoría)
    path('gestion-tipos/editar/<int:pk>/', views.editar_tipo_ejercicio, name='editar_tipo_ejercicio'),
    
    # HU-31: Eliminación de tipo de ejercicio (recibe el ID/pk de la categoría)
    path('gestion-tipos/eliminar/<int:pk>/', views.eliminar_tipo_ejercicio, name='eliminar_tipo_ejercicio'),
]
    