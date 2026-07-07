// static/core/js/recordatorio_popup.js
document.addEventListener('DOMContentLoaded', function() {
    const dataContainer = document.getElementById('agenda-data-json');
    if (!dataContainer) {
        console.warn("🛑 No se encontró el contenedor del JSON de la agenda.");
        return;
    }

    try {
        const agendaJson = JSON.parse(dataContainer.textContent);
        console.log("📦 Datos recibidos desde Django:", agendaJson);
        
        const fechaActual = new Date();
        const diasSemana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
        const nombreHoy = diasSemana[fechaActual.getDay()];

        console.log(`📅 Hoy es: ${nombreHoy}`);
        const rutinaDeHoy = agendaJson[nombreHoy];
        console.log("🏋️‍♂️ Rutina detectada para hoy:", rutinaDeHoy);

        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('test') === '1') {
            console.log("🚀 MODO TEST: Abriendo modal forzosamente.");
            const miModal = new bootstrap.Modal(document.getElementById('modalRecordatorio'));
            miModal.show();
            return; 
        }

        if (rutinaDeHoy && rutinaDeHoy.usa_popup && rutinaDeHoy.hora) {
            console.log("✅ La rutina tiene el Pop-up activado y tiene hora configurada.");
            
            const fechaClave = `${fechaActual.getFullYear()}-${fechaActual.getMonth() + 1}-${fechaActual.getDate()}`;
            const storageKey = `alerta_rutina_${fechaClave}`;

            if (localStorage.getItem(storageKey) === 'visto') {
                console.log("🚫 El Pop-up ya fue mostrado hoy (bloqueado por localStorage).");
                return;
            }

            const [horaRutina, minRutina] = String(rutinaDeHoy.hora).split(':').map(Number);
            const momentoAlerta = new Date();
            momentoAlerta.setHours(horaRutina, minRutina, 0, 0);

            console.log(`⏰ Hora objetivo de la alarma: ${momentoAlerta.toLocaleTimeString()}`);
            console.log(`🕒 Hora exacta en tu PC ahora: ${fechaActual.toLocaleTimeString()}`);

            const dispararNotificacion = () => {
                console.log("🔔 ¡DISPARANDO NOTIFICACIÓN AHORA!");
                document.getElementById('lbl-nombre-rutina').innerText = rutinaDeHoy.nombre;
                document.getElementById('lbl-desc-rutina').innerText = rutinaDeHoy.descripcion || "Sin descripción disponible.";
                const miModal = new bootstrap.Modal(document.getElementById('modalRecordatorio'));
                miModal.show();
                localStorage.setItem(storageKey, 'visto');
            };

            if (fechaActual >= momentoAlerta) {
                console.log("⚡ La hora ya pasó. Mostrando Pop-up de inmediato (si no se ha visto hoy).");
                dispararNotificacion();
            } else {
                const milisegundosFaltantes = momentoAlerta.getTime() - fechaActual.getTime();
                console.log(`⏳ Faltan ${(milisegundosFaltantes / 60000).toFixed(1)} minutos. Temporizador activado en segundo plano.`);
                setTimeout(dispararNotificacion, milisegundosFaltantes);
            }
        } else {
            console.log("❌ No se cumplen las condiciones para la alarma (No hay rutina, switch apagado o falta hora).");
        }
    } catch (e) {
        console.error("💥 Error crítico procesando la agenda JSON:", e);
    }
});