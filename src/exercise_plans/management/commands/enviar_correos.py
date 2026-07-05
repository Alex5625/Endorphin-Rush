from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from exercise_plans.models import Rutina

class Command(BaseCommand):
    help = 'Envía correos de recordatorio a la terminal según la hora configurada'

    def handle(self, *args, **kwargs):
        ahora = timezone.localtime()
        
        # Mapeamos el día actual
        dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        dia_actual = dias_semana[ahora.weekday()]

        # # ==========================================
        # # 🕵️‍♂️ BLOQUE DE DEBUG: ¿Qué está viendo Django?
        # # ==========================================
        # self.stdout.write(self.style.WARNING("--- MODO DETECTIVE ACTIVADO ---"))
        # self.stdout.write(f"1. El script cree que hoy es: {dia_actual}")
        # self.stdout.write(f"2. El script cree que la hora es: {ahora.hour}:{ahora.minute}")
        
        # rutinas_activas = Rutina.objects.filter(recordatorio_correo=True)
        # self.stdout.write(f"3. Rutinas totales con correo activado en la BD: {rutinas_activas.count()}")
        
        # for r in rutinas_activas:
        #     estado_dia = getattr(r, dia_actual)
        #     self.stdout.write(f"   -> Rutina: '{r.nombre_rutina}' | Hora guardada: {r.hora_correo} | ¿Está activa para {dia_actual}?: {estado_dia}")
        # self.stdout.write(self.style.WARNING("-------------------------------"))
        # # ==========================================
        
        # Filtramos rutinas para el día y hora actual
        # Asegúrate de que tu modelo Rutina tenga campos como 'hora_email' y 'email_activo'
        filtros = {
            dia_actual: True,
            'recordatorio_correo': True,
            'hora_correo__hour': ahora.hour,
            'hora_correo__minute': ahora.minute,
        }
        
        rutinas_ahora = Rutina.objects.filter(**filtros)

        if not rutinas_ahora.exists():
            self.stdout.write("No hay correos programados para este minuto.")
            return

        for rutina in rutinas_ahora:
            asunto = f"¡Es hora de entrenar: {rutina.nombre_rutina}!"
            mensaje = f"Hola {rutina.autor.username},\n\nTe recordamos que tienes programada tu rutina '{rutina.nombre_rutina}' para hoy.\n\n¡Ánimo, tú puedes!"
            correo_destino = rutina.autor.email if rutina.autor.email else 'prueba@ejemplo.com'
            try:
                send_mail(
                    subject=asunto,
                    message=mensaje,
                    from_email='no-reply@endorphinrush.com',
                    recipient_list=[correo_destino],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Correo "enviado" (a terminal) para {rutina.autor.username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error enviando correo: {str(e)}'))