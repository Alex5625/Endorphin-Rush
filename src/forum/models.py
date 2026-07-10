from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Publicacion(models.Model):
    autor = models.ForeignKey(User, 
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                verbose_name='Autor del post', 
                                related_name='publicaciones')
    rutina_vinculada = models.ForeignKey('exercise_plans.Rutina', 
                                            on_delete=models.SET_NULL, 
                                            null=True, 
                                            blank=True)
    titulo = models.TextField(help_text="Asi se llamará la publicación")
    texto = models.TextField(help_text="Escribe tu consejo o mensaje aquí")
    imagen = models.ImageField(upload_to='foro_imagenes/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion'] 

    def __str__(self):
        return f"Post de {self.autor.username} - {self.fecha_creacion.strftime('%d/%m/%Y')}"