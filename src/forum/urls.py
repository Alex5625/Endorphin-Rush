from django.urls import path
from . import views

app_name = 'forum' 

urlpatterns = [
    path('', views.forum_board, name='board'),
    
    path('crear/', views.crear_publicacion, name='create_post'),
    path('editar/<int:post_id>/', views.editar_publicacion, name='editar_publicacion'),
    path('eliminar/<int:post_id>/', views.eliminar_publicacion, name='eliminar_publicacion'),
    path('adoptar/<int:publicacion_id>/', views.adoptar_rutina_foro, name='adoptar_rutina'),
]