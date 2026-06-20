from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Ejercicio(models.Model):
    nombre_ejercicio = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Ejercicio*"
    )

    # 2. Añadimos el autor. null=True y blank=True evitan conflictos con datos viejos.
    autor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Autor/Entrenador",
        related_name="ejercicios_creados",
        null=True,   
        blank=True   
    )

    # Relación cruzada apuntando a la app exercise_types de forma segura:
    tipo_ejercicio = models.ForeignKey(
        'exercise_types.TipoEjercicio',
        verbose_name="Tipo de Ejercicio*",
        on_delete=models.CASCADE,
    )

    imagen = models.ImageField(
        upload_to='media/ejercicios/',
        null=True,
        blank=True,
        verbose_name="Imagen del Ejercicio"
    )

    descripcion_ejercicio = models.TextField(
        verbose_name="Descripción del Ejercicio",
        blank=True,
    )

    autorizado = models.BooleanField(
        default=False,
        verbose_name="¿Autorizado para mostrar en la app?"
    )

    def __str__(self):
        return self.nombre_ejercicio