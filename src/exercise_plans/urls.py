from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'exercise_plans'

urlpatterns = [
    path('', views.gestion_rutinas_view, name='lista_rutinas'),
    path('crear/', views.crear_rutina, name='crear_rutina'),
]