from django.db import models
from django.contrib.auth.models import User

from exercises.models import Ejercicio
# Create your models here.

class Rutina(models.Model):
    nombre_rutina = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Rutina*"
    )

    autor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Autor/Entrenador",
        related_name="rutinas_creadas",  
    )

    ejercicios = models.ManyToManyField(
        Ejercicio,
        through='RutinaEjercicio',
        verbose_name="Ejercicios incluidos en la rutina*",
        related_name="rutinas_incluidas"
    )

    descripcion_rutina = models.TextField(
        verbose_name="Descripción de la Rutina",
        blank=True,
    )

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        
    def __str__(self):
        return f"{self.nombre_rutina} (por {self.autor.username})"


class RutinaEjercicio(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, verbose_name="Ejercicio incluido en la rutina")
    
    series = models.IntegerField(default=3, verbose_name="Número de Series")
    descanso = models.IntegerField(default=20, verbose_name="Descanso entre series (segundos)")
    



    class Meta:

        verbose_name = "Ejercicio de la Rutina"
        verbose_name_plural = "Ejercicios de la Rutina"
        
    def __str__(self):
        return f"{self.ejercicio.nombre} en {self.rutina.nombre_rutina} "