// static/core/js/recordatorio_popup.js
document.addEventListener('DOMContentLoaded', function() {
    const dataContainer = document.getElementById('agenda-data-json');
    if (!dataContainer) return;

    try {
        const agendaJson = JSON.parse(dataContainer.textContent);
        
        const fechaActual = new Date();
        const diasSemana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
        const nombreHoy = diasSemana[fechaActual.getDay()];

        const rutinaDeHoy = agendaJson[nombreHoy];

        // 🛠️ MODO DE PRUEBA: Si la URL tiene '?test=1', forzamos el modal con datos simulados o reales
        const urlParams = new URLSearchParams(window.location.search);
        const modoTest = urlParams.get('test') === '1';

        if (modoTest) {
            console.log("🚀 Modo de prueba activo: Forzando visualización del recordatorio.");
            document.getElementById('lbl-nombre-rutina').innerText = rutinaDeHoy?.nombre || "Rutina de Prueba (Modo Test)";
            document.getElementById('lbl-desc-rutina').innerText = rutinaDeHoy?.descripcion || "Esta es una simulación en tiempo real para verificar el diseño de la alerta.";
            const miModal = new bootstrap.Modal(document.getElementById('modalRecordatorio'));
            miModal.show();
            return; // Detenemos el resto de la lógica para que no interfiera el localStorage
        }

        // LÓGICA DE PRODUCCIÓN CONTINÚA AQUÍ
        if (rutinaDeHoy && rutinaDeHoy.usa_popup) {
            const fechaClave = `${fechaActual.getFullYear()}-${fechaActual.getMonth() + 1}-${fechaActual.getDate()}`;
            const storageKey = `alerta_rutina_${fechaClave}`;

            // Si ya se mostró hoy, no hacemos nada
            if (localStorage.getItem(storageKey) === 'visto') {
                return;
            }

            const [horaRutina, minRutina] = rutinaDeHoy.hora.split(':').map(Number);
            const momentoAlerta = new Date();
            momentoAlerta.setHours(horaRutina, minRutina, 0, 0);

            // Función interna para desplegar el modal de forma limpia
            const dispararNotificacion = () => {
                document.getElementById('lbl-nombre-rutina').innerText = rutinaDeHoy.nombre;
                document.getElementById('lbl-desc-rutina').innerText = rutinaDeHoy.descripcion || "Sin descripción disponible.";
                
                const miModal = new bootstrap.Modal(document.getElementById('modalRecordatorio'));
                miModal.show();

                localStorage.setItem(storageKey, 'visto');
            };

            // ESCENARIO A: La hora configurada YA PASÓ o es justo AHORA
            if (fechaActual >= momentoAlerta) {
                dispararNotificacion();
                
                // Limpieza de registros antiguos
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key && key.startsWith('alerta_rutina_') && key !== storageKey) {
                        localStorage.removeItem(key);
                    }
                }
            } 
            // ESCENARIO B: El usuario entró ANTES. Programamos la alarma en tiempo real.
            else {
                const milisegundosFaltantes = momentoAlerta.getTime() - fechaActual.getTime();
                console.log(`⏰ Alarma programada en tiempo real. El entrenamiento iniciará en ${(milisegundosFaltantes / 60000).toFixed(1)} minutos.`);
                
                setTimeout(function() {
                    // Verificación de doble seguridad por si acaso mutó el almacenamiento mientras esperaba
                    if (localStorage.getItem(storageKey) !== 'visto') {
                        dispararNotificacion();
                    }
                }, milisegundosFaltantes);
            }
        }
    } catch (e) {
        console.error("Error en el sistema de alertas:", e);
    }
});