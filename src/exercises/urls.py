from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'exercises'

urlpatterns = [
    # HU-06: Creación de ejercicios
    path('lista-ejercicios/', views.gestion_ejercicios, name='lista_ejercicios'),    

    # HU-07: Edición de ejercicios (recibe el ID/pk del ejercicio)
    path('lista-ejercicios/editar/<int:pk>/', views.editar_ejercicio, name='editar_ejercicio'),

    # HU-08: Eliminación de ejercicios (recibe el ID/pk del ejercicio)
    path('lista-ejercicios/eliminar/<int:pk>/', views.eliminar_ejercicio, name='eliminar_ejercicio'),

    path('panel-control/pendientes/', views.panel_pendientes, name='panel_pendientes'),
    path('panel-control/procesar/<int:pk>/', views.procesar_ejercicio, name='procesar_ejercicio'),
]

