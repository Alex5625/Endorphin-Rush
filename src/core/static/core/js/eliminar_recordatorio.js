// static/core/js/eliminar_recordatorio.js

// 1. Función para abrir el modal e inyectar los datos
function abrirModalEliminar(rutinaId, rutinaNombre) {
    document.getElementById('hidden-rutina-id').value = rutinaId;
    document.getElementById('lbl-eliminar-nombre').innerText = rutinaNombre;
    
    const modal = new bootstrap.Modal(document.getElementById('modalEliminarRecordatorio'));
    modal.show();
}

// 2. Función para ejecutar la petición silenciosa (AJAX) a Django
function procesarEliminacion(tipo) {
    const rutinaId = document.getElementById('hidden-rutina-id').value;
    
    // Leemos el token CSRF desde el input oculto que generó Django en el HTML
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    
    const url = `/exercise_plans/rutina/${rutinaId}/eliminar-recordatorios/`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ tipo: tipo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Cerramos el modal
            const modalEl = document.getElementById('modalEliminarRecordatorio');
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            modalInstance.hide();
            
            // Recarga rápida para actualizar la interfaz limpia
            window.location.reload(); 
        } else {
            alert("Hubo un error: " + data.mensaje);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Error de conexión al intentar eliminar el recordatorio.");
    });
}