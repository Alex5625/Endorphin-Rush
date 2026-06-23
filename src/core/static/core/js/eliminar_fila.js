document.addEventListener('DOMContentLoaded', function() {
    const tabla = document.getElementById('tabla-ejercicios');

    if (!tabla) return;

    // Escuchamos los clics en toda la tabla (Delegación de eventos)
    // Esto asegura que funcione tanto para las filas iniciales como para las añadidas dinámicamente con el otro script
    tabla.addEventListener('click', function(e) {
        // Buscamos si el clic ocurrió en el botón de quitar o dentro de su ícono
        const botonQuitar = e.target.closest('.btn-quitar-ejercicio');
        
        if (!botonQuitar) return;

        // Buscamos la fila (<tr>) que contiene al botón presionado
        const fila = botonQuitar.closest('.fila-ejercicio');
        if (!fila) return;

        // Buscamos el checkbox oculto de Django que maneja la eliminación en esta fila
        const checkboxDelete = fila.querySelector('input[type="checkbox"][name$="-DELETE"]');

        if (checkboxDelete) {
            // Caso 1: La fila ya existe en la Base de Datos (Modo Edición)
            // Marcamos el checkbox verdadero para que Django sepa que debe borrarlo y ocultamos visualmente la fila
            checkboxDelete.checked = true;
            fila.style.transition = "all 0.3s ease";
            fila.style.opacity = "0";
            setTimeout(() => {
                fila.style.display = "none";
            }, 300);
        } else {
            // Caso 2: Es una fila nueva clonada dinámicamente que aún no se guarda en la BD
            // Podemos eliminarla directamente del DOM sin problemas
            fila.style.transition = "all 0.3s ease";
            fila.style.opacity = "0";
            setTimeout(() => {
                fila.remove();
                actualizarContadorFormset();
            }, 300);
        }
    });

    // Función auxiliar para actualizar el contador TOTAL_FORMS si eliminamos filas temporales
    function actualizarContadorFormset() {
        const totalFormsInput = document.querySelector('[id$="-TOTAL_FORMS"]');
        if (totalFormsInput) {
            const filasRestantes = document.querySelectorAll('.fila-ejercicio').length;
            totalFormsInput.value = filasRestantes;
        }
    }
});