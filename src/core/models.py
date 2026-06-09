from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PerfilUsuario(models.Model):

    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    apellido = models.CharField(max_length=50, verbose_name="Apellido")
    edad = models.IntegerField(verbose_name="Edad")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo") # O un campo con opciones (Choices)
    peso = models.FloatField(verbose_name="Peso")  # en kg
    altura = models.FloatField(verbose_name="Altura") # en metros
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
class TipoEjercicio(models.Model):
#Modelo para las categorías de grupos musculares 
#Almacena los contenedores globales del gym (ej: tren superior,
#tren inferior, pectorales, etc...)

    nombre_categoria = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Grupo Muscular"
    )

    class Meta:
        verbose_name = "Tipo de Ejercicio"
        verbose_name_plural = "Tipos de Ejercicios"

    def __str__(self):
        return self.nombre_categoria

class Ejercicio(models.Model):
    nombre_ejercicio = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Ejercicio"
    )

    tipo_ejercicio = models.ForeignKey(
        'TipoEjercicio',
        on_delete=models.CASCADE,
    )

    imagen = models.ImageField(
        upload_to='ejercicios/',
        null=True, # vamos a permitir que sea opcional la imagen?
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