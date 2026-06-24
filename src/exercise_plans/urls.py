from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'exercise_plans'

urlpatterns = [
    path('', views.gestion_rutinas_view, name='lista_rutinas'),
    path('crear/', views.crear_rutina, name='crear_rutina'),
    path('editar/<int:pk>/', views.editar_rutina, name='editar_rutina'),
    path('mis-rutinas/', views.mis_rutinas, name='mis_rutinas'),
    path('rutina/<int:rutina_id>/guardar', views.guardar_rutina, name='guardar_rutina'),

    path('eliminar/<int:pk>/', views.eliminar_rutina, name='eliminar_rutina')
]