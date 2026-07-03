from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from exercises.models import Ejercicio
# Create your models here.

class Rutina(models.Model):
    nombre_rutina = models.CharField(
        max_length=100,
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


    publico = models.BooleanField(
        default=False,
        verbose_name="¿Es pública?"
    )

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"

    constraints = [
            models.UniqueConstraint(
                fields=['autor', 'nombre_rutina'], 
                name='unique_rutina_per_user'
            )
    ] 

    lunes = models.BooleanField(default=False, verbose_name="Lunes")
    martes = models.BooleanField(default=False, verbose_name="Martes")
    miercoles = models.BooleanField(default=False, verbose_name="Miércoles")
    jueves = models.BooleanField(default=False, verbose_name="Jueves")
    viernes = models.BooleanField(default=False, verbose_name="Viernes")
    sabado = models.BooleanField(default=False, verbose_name="Sábado")
    domingo = models.BooleanField(default=False, verbose_name="Domingo")

        
    def clean(self):
        super().clean()
        
        dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        
        for dia in dias_semana:
            # Si el usuario marcó este día como True en el formulario...
            if getattr(self, dia):
                # Buscamos si ya tiene OTRA rutina que ocupe ese mismo día
                # (Usamos exclude para ignorar esta misma rutina si la estamos editando)
                rutinas_conflicto = Rutina.objects.filter(
                    autor=self.autor, 
                    **{dia: True}
                ).exclude(pk=self.pk)
                
                if rutinas_conflicto.exists():
                    nombre_conflicto = rutinas_conflicto.first().nombre_rutina
                    raise ValidationError({
                        dia: f"Día bloqueado. Ya ocupado por tu rutina '{nombre_conflicto}'."
                    })

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