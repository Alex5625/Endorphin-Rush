document.addEventListener('DOMContentLoaded', function() {
    const btnAnadir = document.getElementById('btn-anadir-ejercicio');
    const tablaBody = document.querySelector('#tabla-ejercicios tbody');
    // 💡 Imprimimos en la consola para comprobar si los encuentra:
    console.log("Botón encontrado:", btnAnadir);
    console.log("Tabla encontrada:", tablaBody);

    // Buscamos el ID que genera Django para el TOTAL_FORMS
    // NOTA: Revisa en tu consola si tu management_form usa exactamente este ID
    const totalFormsInput = document.querySelector('[id$="-TOTAL_FORMS"]'); 
    console.log("Input total forms encontrado:", totalFormsInput);

    if (!btnAnadir || !tablaBody || !totalFormsInput) {
        console.error("Faltan elementos críticos en el DOM. El script no se activará.");
        return;
    }

    btnAnadir.addEventListener('click', function(e) {
        e.preventDefault(); // Evita cualquier comportamiento extraño del botón
        console.log("¡Click capturado exitosamente!");

        const filasActuales = document.querySelectorAll('.fila-ejercicio');
        const totalForms = filasActuales.length;

        if (totalForms === 0) return;

        const ultimaFila = filasActuales[totalForms - 1];
        const nuevaFila = ultimaFila.cloneNode(true);

        const regexIndice = new RegExp(`-${totalForms - 1}-`, 'g');

        nuevaFila.querySelectorAll('input, select, textarea').forEach(function(input) {
            if (input.name) {
                input.name = input.name.replace(regexIndice, `-${totalForms}-`);
            }
            if (input.id) {
                input.id = input.id.replace(regexIndice, `-${totalForms}-`);
            }
            
            if (input.tagName === 'SELECT') {
                input.selectedIndex = 0;
            } else if (input.type === 'number') {
                if (input.id.includes('orden')) {
                    input.value = totalForms + 1;
                } else {
                    input.value = input.getAttribute('value') || '1';
                }
            } else if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });

        nuevaFila.querySelectorAll('.text-danger').forEach(div => div.remove());

        tablaBody.appendChild(nuevaFila);

        totalFormsInput.value = totalForms + 1;
    });
});