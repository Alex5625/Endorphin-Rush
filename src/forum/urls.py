from django.urls import path
from . import views

app_name = 'forum' 

urlpatterns = [
    path('', views.forum_board, name='board'),
    
    path('crear/', views.crear_publicacion, name='create_post'),
    
]