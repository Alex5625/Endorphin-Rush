from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class HistorialAcciones(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    accion = models.CharField(max_length=255, verbose_name="Acción realizada")
    detalle = models.TextField(verbose_name="Detalles de la acción", blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Historial de Acción"
        verbose_name_plural = "Historial de Acciones"
        ordering = ['-fecha']

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema/Anónimo"
        return f"{usuario_str} - {self.accion} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"  