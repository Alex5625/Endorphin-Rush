    document.addEventListener('DOMContentLoaded', function() {
        var calendarEl = document.getElementById('calendar');
        
        var historialData = document.getElementById('historial-data').textContent;
        var historial = JSON.parse(historialData);
        
        function abrirModalNavegable(eventos, index) {
        var evento = eventos[index];
        var modalId = '#modal-sesion-' + evento.id;
        var modalNode = document.querySelector(modalId);
        
        if (!modalNode) return;

        var footer = modalNode.querySelector('#footer-sesion-' + evento.id);
        var btnPrev = modalNode.querySelector('#prev-sesion-' + evento.id);
        var btnNext = modalNode.querySelector('#next-sesion-' + evento.id);
        var contador = modalNode.querySelector('#contador-sesion-' + evento.id);

        if (eventos.length > 1) {
            footer.classList.remove('d-none');
            contador.innerText = (index + 1) + " de " + eventos.length;
            
            btnPrev.style.visibility = (index > 0) ? 'visible' : 'hidden';
            btnPrev.onclick = function() {
                bootstrap.Modal.getInstance(modalNode).hide(); // Cerramos el actual
                setTimeout(() => abrirModalNavegable(eventos, index - 1), 400); 
            };
            
            btnNext.style.visibility = (index < eventos.length - 1) ? 'visible' : 'hidden';
            btnNext.onclick = function() {
                bootstrap.Modal.getInstance(modalNode).hide();
                setTimeout(() => abrirModalNavegable(eventos, index + 1), 400);
            };
        } else {
            footer.classList.add('d-none');
        }

        var myModal = new bootstrap.Modal(modalNode);
        myModal.show();
    }

        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es',
            events: historial,
            height: 'auto',
            aspectRatio: 1.1,
            dayHeaderFirnat: { weekday: 'narrow' },
            
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                day: 'Día'
            },
            headerToolbar: {
                left: 'prev',
                center: 'title',
                right: 'next'
            },
            eventContent: function(arg) {
                var dotEl = document.createElement('div');
                dotEl.style.width = '6px';
                dotEl.style.height = '6px';
                dotEl.style.backgroundColor = arg.event.backgroundColor || '#212529';
                dotEl.style.borderRadius = '50%';
                dotEl.style.margin = '2px auto'; 
                return { domNodes: [dotEl] };
            },
            dateClick: function(info) {
                var eventosDelDia = calendar.getEvents().filter(e => e.startStr.split('T')[0] === info.dateStr);
                
                if (eventosDelDia.length > 0) {
                    abrirModalNavegable(eventosDelDia, 0);
                }
            },
            eventClick: function(info) {
                var dateStr = info.event.startStr.split('T')[0];
                var eventosDelDia = calendar.getEvents().filter(e => e.startStr.split('T')[0] === dateStr);
                var index = eventosDelDia.findIndex(e => e.id === info.event.id);
                abrirModalNavegable(eventosDelDia, index);
            }
        });
        
        calendar.render();
    });
