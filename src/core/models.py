from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

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
    
class TerminosCondiciones(models.Model):
    #le agregamos un título para que el administrador los identifique facilmente
    titulo = models.CharField(
        max_length=150, 
        verbose_name="Título de la Versión", 
        help_text="Ej: TyC Actualización Ley de Protección 2026",
        default="Términos y Condiciones Generales"  #default temporal por si ya hay resgistros viejos
    )
    contenido = models.TextField(
        verbose_name="Texto Legal", 
        help_text="Escribe aquí todos los términos y condiciones. Se respetarán los saltos de línea."
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Publicación"
    )
    #campo clave para el versionado
    activo = models.BooleanField(
        default=False, 
        verbose_name="¿Es la versión vigente?"
    )

    class Meta:
        verbose_name = "Términos y Condiciones"
        verbose_name_plural = "Historial de Términos y Condiciones"
        ordering = ['-fecha_actualizacion'] #ordenar para que el historial muestre lo mas nuevo arriba

    def save(self, *args, **kwargs):
        #logica de Auditoría: Si el admin activa esta versión, apagamos todas las demás automáticamente
        if self.activo:
            TerminosCondiciones.objects.filter(activo=True).update(activo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        estado = "🟢 VIGENTE" if self.activo else "🔴 ARCHIVADO"
        return f"{self.titulo} - {estado} ({self.fecha_actualizacion.strftime('%d/%m/%Y')})"
    
class SesionEntrenamiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.RESTRICT)
    rutina = models.ForeignKey('exercise_plans.Rutina', on_delete=models.RESTRICT)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.rutina.nombre_rutina} - {self.fecha_inicio.strftime('%d/%m %H:%M')}"

    @property
    def esta_activa(self):
        ##devuelve True si la sesion sigue en curso y no han pasado 3 horas
        if self.fecha_fin:
            return False
        
        limite = self.fecha_inicio + timedelta(hours=3)
        if timezone.now()>limite:
            return False
        
        return True
    def cerrar_sesion(self):
        ##cierra la sesion actual aplicando la regla de las 3 horas si expiró
        if not self.fecha_fin:
            limite = self.fecha_inicio + timedelta(hours=3)
            if timezone.now() > limite:
                self.fecha_fin = limite
            else: 
                self.fecha_fin =  timezone.now()
            self.save()

class RegistroSerie(models.Model):
    #usamos RESTRICT para evitar el borrado en cascada y proteger el historial
    sesion = models.ForeignKey('core.SesionEntrenamiento', on_delete=models.RESTRICT)
    bloque = models.ForeignKey('exercise_plans.RutinaEjercicio', on_delete=models.RESTRICT)
    
    numero_serie = models.PositiveIntegerField(verbose_name="Número de Serie")
    peso_levantado = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Peso (kg)"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sesion', 'bloque', 'numero_serie'], 
                name='unique_serie_por_bloque_y_sesion'
            )
        ]
    def __str__(self):
        return f"Sesión {self.sesion.id} - Serie {self.numero_serie}: {self.peso_levantado}kg"

