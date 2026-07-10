from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Ejercicio(models.Model):
    nombre_ejercicio = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Ejercicio*"
    )

    # CAMBIO: Usamos SET_NULL para que el ejercicio no se borre si el autor elimina su cuenta
    autor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        verbose_name="Autor/Entrenador",
        related_name="ejercicios_creados",
        null=True,   
        blank=True   
    )

    # CAMBIO: Usamos PROTECT para evitar que se borren ejercicios si se elimina un TipoEjercicio
    tipo_ejercicio = models.ForeignKey(
        'exercise_types.TipoEjercicio',
        verbose_name="Tipo de Ejercicio*",
        on_delete=models.PROTECT,
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

    # soft_delete
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Ejercicio Activo?"
    )

    def __str__(self):
        return self.nombre_ejercicio

    def delete(self, *args, **kwargs):
        self.activo = False
        self.save()