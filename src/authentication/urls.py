from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'

urlpatterns = [    
    path("login/", 
         auth_views.LoginView.as_view(template_name="registration/login.html",         
                                      redirect_authenticated_user=True,
                                      next_page="core:home",), 
         name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="authentication:login"), name="logout"),
    path('registro/', views.registrar_usuario, name='registro'),
    
    # HU-02: Edición de perfil de usuario (solo datos corporales/personales)
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    
    # HU-03: Eliminación de perfil de usuario (desactivación de cuenta)
    path('eliminar-perfil/', views.eliminar_perfil, name='eliminar_perfil'),
    
]