from django.urls import path
from . import views

app_name = 'exercise_plans'

urlpatterns = [
    # 🌍 Catálogo Global (Usa: gestion_rutinas.html con action='external')
    path('', views.gestion_rutinas_view, name='lista_rutinas'),
    
    # 🔒 Mis Rutinas Personales (Usa: gestion_rutinas.html con action='personal')
    path('mis-rutinas/', views.mis_rutinas, name='mis_rutinas'),
    
    # ➕ Crear Plan (Usa: configurar_rutina.html con action='crear')
    path('crear/', views.crear_rutina, name='crear_rutina'),
    
    # 🛠️ Editar Plan (Usa: configurar_rutina.html con action='editar')
    path('editar/<int:pk>/', views.editar_rutina, name='editar_rutina'),
    
    # 💾 Guardar/Clonar Rutina externa
    path('rutina/<int:rutina_id>/guardar/', views.guardar_rutina, name='guardar_rutina'),

    # ❌ Eliminar Rutina
    path('eliminar/<int:pk>/', views.eliminar_rutina, name='eliminar_rutina'),
    
    # 🗑️ Papelera de Rutinas
    path('papelera/', views.papelera_rutinas, name='papelera_rutinas'),
    # 🗑️ Restaurar Rutina desde Papelera
    path('rutina/<int:pk>/restaurar/', views.restaurar_rutina, name='restaurar_rutina'),
    
    # ⏰ Eliminar recordatorios 
    path('rutina/<int:rutina_id>/eliminar-recordatorios/', views.eliminar_recordatorios_ajax, name='eliminar_recordatorios_ajax'),
]