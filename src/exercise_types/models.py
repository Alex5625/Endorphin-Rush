from django.db import models

# Create your models here.

class TipoEjercicio(models.Model):
    nombre_categoria = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Grupo Muscular"
    )
    #soft_delete
    activo = models.BooleanField(
            default=True,
            verbose_name="¿Activo?"
        )
    class Meta:
        verbose_name = "Tipo de Ejercicio"
        verbose_name_plural = "Tipos de Ejercicios"

    def __str__(self):
        return self.nombre_categoria
    
    def delete(self, *args, **kwargs):
        self.activo = False
        self.save()