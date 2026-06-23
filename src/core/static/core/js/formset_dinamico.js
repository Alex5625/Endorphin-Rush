document.addEventListener('DOMContentLoaded', function() {
    const btnAnadir = document.getElementById('btn-anadir-ejercicio');
    const tablaBody = document.querySelector('#tabla-ejercicios tbody');
    const totalFormsInput = document.querySelector('[id$="-TOTAL_FORMS"]'); 

    if (!btnAnadir || !tablaBody || !totalFormsInput) {
        console.error("Faltan elementos críticos en el DOM. El script no se activará.");
        return;
    }

    btnAnadir.addEventListener('click', function(e) {
        e.preventDefault();

        const filasActuales = document.querySelectorAll('.fila-ejercicio');
        const totalForms = filasActuales.length;

        if (totalForms === 0) return;

        const ultimaFila = filasActuales[totalForms - 1];
        const nuevaFila = ultimaFila.cloneNode(true);

        nuevaFila.querySelectorAll('.text-danger').forEach(div => div.remove());

        nuevaFila.querySelectorAll('input, select, textarea').forEach(function(input) {
            if (input.tagName === 'SELECT') {
                input.selectedIndex = 0;
            } else if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });

        tablaBody.appendChild(nuevaFila);

        window.recalcularIndicesYOrden();
    });

    window.recalcularIndicesYOrden = function() {
        const filas = document.querySelectorAll('.fila-ejercicio');
        
        filas.forEach(function(fila, index) {
            // Solo corregimos los prefijos de Django (-0-, -1-, -2-) correspondientes al Formset
            fila.querySelectorAll('input, select, textarea').forEach(function(input) {
                if (input.name) {
                    input.name = input.name.replace(/-\d+-/g, `-${index}-`);
                }
                if (input.id) {
                    input.id = input.id.replace(/-\d+-/g, `-${index}-`);
                }
            });
        });

        if (totalFormsInput) {
            totalFormsInput.value = filas.length;
        }
    };

    window.recalcularIndicesYOrden();
});