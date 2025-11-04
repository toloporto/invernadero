// scripts.js

// --- CONFIGURACIÓN ---
const API_BASE_URL = 'http://127.0.0.1:5000/api/v1/cultivos';
const tableBody = document.getElementById('cultivoList');
const form = document.getElementById('cultivoForm');
const submitButton = document.getElementById('submitButton');
const originalNameInput = document.getElementById('cultivoNombreOriginal');
const loadingMessage = document.getElementById('loading-message');
const searchInput = document.getElementById('cultivoSearch'); // <-- NUEVO: Input de búsqueda

let modoEdicion = false; 
let cultivosData = []; // <-- NUEVO: Almacenar los datos cargados de la API

// --- FUNCIONES DE MANEJO DE LA API (CRUD) ---

/**
 * 1. GET (Leer): Carga y renderiza todos los cultivos.
 */
async function cargarCultivos() {
    loadingMessage.textContent = 'Cargando datos de la API...';
    try {
        const response = await fetch(API_BASE_URL);
        const cultivos = await response.json();
        
        cultivosData = cultivos; // <-- GUARDAR los datos globalmente
        
        loadingMessage.style.display = 'none'; // Ocultar mensaje de carga
        renderizarTabla(cultivosData); // Renderizar todos al inicio

    } catch (error) {
        console.error('Error al cargar cultivos:', error);
        loadingMessage.textContent = 'ERROR: No se pudo conectar con el servidor Flask. Asegúrate de que esté corriendo en http://127.0.0.1:5000.';
        loadingMessage.style.color = 'var(--color-danger)';
    }
}

/**
 * 2. POST / PUT (Crear / Actualizar): Envía datos del formulario a la API.
 */
async function manejarEnvioFormulario(event) {
    event.preventDefault(); // Detener el envío por defecto

    const datosCultivo = obtenerDatosFormulario();

    if (!datosCultivo.nombre || !datosCultivo.fecha_siembra || !datosCultivo.fecha_cosecha) {
        alert('Por favor, rellena el nombre, la fecha de siembra y la fecha de cosecha.');
        return;
    }

    const nombreOriginal = originalNameInput.value;
    let url = API_BASE_URL;
    let method = 'POST';
    
    // Si estamos en modo edición, cambiamos el método y la URL
    if (modoEdicion) {
        url = `${API_BASE_URL}/${nombreOriginal}`;
        method = 'PUT';
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datosCultivo),
        });

        const resultado = await response.json();

        if (response.ok) {
            alert(resultado.mensaje || (modoEdicion ? 'Cultivo actualizado.' : 'Cultivo añadido.'));
            resetFormulario();
            cargarCultivos(); // Recargar la tabla
        } else {
            alert(`Error ${response.status}: ${resultado.error || 'Algo salió mal en el servidor.'}`);
        }
    } catch (error) {
        console.error('Error al enviar el formulario:', error);
        alert('Error de conexión con la API.');
    }
}

/**
 * 3. DELETE (Eliminar): Elimina un cultivo por nombre.
 */
async function eliminarCultivo(nombreCultivo) {
    if (!confirm(`¿Estás seguro de que deseas eliminar el cultivo: ${nombreCultivo}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/${nombreCultivo}`, {
            method: 'DELETE',
        });

        const resultado = await response.json();

        if (response.ok) {
            alert(resultado.mensaje || 'Cultivo eliminado.');
            cargarCultivos(); // Recargar la tabla
        } else {
            alert(`Error ${response.status}: ${resultado.error || 'No se pudo eliminar el cultivo.'}`);
        }
    } catch (error) {
        console.error('Error al eliminar:', error);
        alert('Error de conexión con la API.');
    }
}

/**
 * 4. FILTRAR: Filtra los cultivos mostrados en la tabla basándose en el texto de búsqueda.
 */
function filtrarCultivos() {
    const textoBusqueda = searchInput.value.toLowerCase().trim();
    
    if (textoBusqueda === '') {
        // Si no hay texto, mostrar todo
        renderizarTabla(cultivosData);
        return;
    }
    
    const cultivosFiltrados = cultivosData.filter(cultivo => {
        // Concatenar campos relevantes y buscar el texto en ellos
        const contenido = (
            (cultivo.nombre || '') + 
            (cultivo.zona || '') + 
            (cultivo.notas || '') + 
            (cultivo.fecha_cosecha || '')
        ).toLowerCase();
        
        return contenido.includes(textoBusqueda);
    });
    
    renderizarTabla(cultivosFiltrados);
}


// --- FUNCIONES DE UTILIDAD Y RENDERIZADO ---

/**
 * Recopila los datos del formulario.
 */
function obtenerDatosFormulario() {
    return {
        nombre: document.getElementById('nombre').value.trim(),
        zona: document.getElementById('zona').value.trim(),
        fecha_siembra: document.getElementById('fecha_siembra').value,
        fecha_cosecha: document.getElementById('fecha_cosecha').value,
        precio_compra: parseFloat(document.getElementById('precio_compra').value) || 0.0,
        precio_venta: parseFloat(document.getElementById('precio_venta').value) || 0.0,
        dias_alerta: parseInt(document.getElementById('dias_alerta').value) || 0,
        notas: document.getElementById('notas').value.trim(),
    };
}

/**
 * Pinta la tabla HTML con los datos pasados.
 */
function renderizarTabla(cultivos) {
    tableBody.innerHTML = '';
    
    if (cultivos.length === 0) {
        const row = tableBody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 7;
        cell.textContent = 'No se encontraron cultivos que coincidan con la búsqueda.';
        cell.style.textAlign = 'center';
        return;
    }

    cultivos.forEach(cultivo => {
        const row = tableBody.insertRow();
        let claseCosecha = 'cosecha-futura';
        
        // Determinar la clase CSS según el estado de días_restantes
        if (cultivo.dias_restantes && cultivo.dias_restantes.includes('COSECHA HOY')) {
            claseCosecha = 'cosecha-hoy';
        } else if (cultivo.dias_restantes && cultivo.dias_restantes.includes('Cosechado hace')) {
            claseCosecha = 'cosecha-pasada';
        }
        
        // Calcular margen potencial
        const margen = (cultivo.precio_venta - cultivo.precio_compra).toFixed(2);
        
        // Renderizado de las celdas
        row.insertCell().textContent = cultivo.nombre;
        row.insertCell().textContent = cultivo.zona;
        row.insertCell().textContent = cultivo.fecha_siembra;
        row.insertCell().textContent = cultivo.fecha_cosecha;
        
        const cellFaltan = row.insertCell();
        cellFaltan.textContent = cultivo.dias_restantes;
        cellFaltan.classList.add(claseCosecha);
        
        row.insertCell().textContent = `€${margen}`;

        // Celda de Acciones (Botones)
        const cellAcciones = row.insertCell();
        cellAcciones.classList.add('action-buttons');
        
        const btnEditar = document.createElement('button');
        btnEditar.textContent = 'Editar';
        btnEditar.classList.add('edit-btn');
        btnEditar.onclick = () => cargarParaEdicion(cultivo);
        
        const btnEliminar = document.createElement('button');
        btnEliminar.textContent = 'Eliminar';
        btnEliminar.classList.add('delete-btn');
        btnEliminar.onclick = () => eliminarCultivo(cultivo.nombre);
        
        cellAcciones.appendChild(btnEditar);
        cellAcciones.appendChild(btnEliminar);
    });
}

/**
 * Carga los datos de un cultivo seleccionado al formulario para su edición.
 */
function cargarParaEdicion(cultivo) {
    // 1. Cargar datos al formulario
    document.getElementById('nombre').value = cultivo.nombre;
    document.getElementById('zona').value = cultivo.zona;
    document.getElementById('fecha_siembra').value = cultivo.fecha_siembra;
    document.getElementById('fecha_cosecha').value = cultivo.fecha_cosecha;
    document.getElementById('precio_compra').value = cultivo.precio_compra.toFixed(2);
    document.getElementById('precio_venta').value = cultivo.precio_venta.toFixed(2);
    document.getElementById('dias_alerta').value = cultivo.dias_alerta;
    document.getElementById('notas').value = cultivo.notas;
    
    // 2. Configurar el modo edición
    modoEdicion = true;
    originalNameInput.value = cultivo.nombre; // Guardar el nombre original para la URL PUT/DELETE
    submitButton.textContent = `Guardar Cambios de ${cultivo.nombre}`;
    submitButton.classList.add('edit-btn');
    submitButton.classList.remove('delete-btn');
    
    // Opcional: Desplazar la vista al formulario 
    document.getElementById('form-section').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Limpia el formulario y vuelve al modo Añadir.
 */
function resetFormulario() {
    form.reset();
    modoEdicion = false;
    originalNameInput.value = '';
    submitButton.textContent = 'Añadir Cultivo';
    submitButton.classList.remove('edit-btn');
    submitButton.classList.remove('delete-btn');
    // Asegurar valores por defecto después del reset()
    document.getElementById('precio_compra').value = '0.00';
    document.getElementById('precio_venta').value = '0.00';
    document.getElementById('dias_alerta').value = '7';
}


// --- INICIALIZACIÓN ---

// Escucha el evento de envío del formulario
form.addEventListener('submit', manejarEnvioFormulario);

// Escucha el evento 'input' en la barra de búsqueda para filtrar dinámicamente
searchInput.addEventListener('input', filtrarCultivos); // <-- LISTENER DE BÚSQUEDA

// Botón de Cancelar Edición
const btnCancelar = document.createElement('button');
btnCancelar.textContent = 'Limpiar / Cancelar Edición';
btnCancelar.classList.add('delete-btn');
btnCancelar.type = 'button'; 
btnCancelar.onclick = resetFormulario;
form.appendChild(btnCancelar);

// Carga los cultivos al iniciar la página
document.addEventListener('DOMContentLoaded', cargarCultivos);
