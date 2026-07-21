/**
 * TERRAE — maintenance.js
 * -----------------------------------------------------------------------
 * Renderiza el historial de mantenimiento (tabla dinámica: fecha,
 * servicio, técnico, observaciones, documento) y gestiona el botón
 * "Registrar mantenimiento" enlazado desde la sección Garantía.
 * -----------------------------------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  const tabla = document.querySelector('[data-componente="tabla-mantenimiento"]');
  if (tabla) {
    document.addEventListener('terrae:pasaporte-cargado', async (evento) => {
      await cargarHistorialMantenimiento(tabla, evento.detail.id);
    });
  }

  const formulario = document.querySelector('[data-form="registrar-mantenimiento"]');
  if (formulario) {
    formulario.addEventListener('submit', manejarRegistroMantenimiento);
  }
});

async function cargarHistorialMantenimiento(tabla, id) {
  const cuerpo = tabla.querySelector('tbody');
  cuerpo.innerHTML = '<tr><td colspan="5"><div class="loader" role="status" aria-label="Cargando historial"></div></td></tr>';

  try {
    const historial = await TerraeAPI.obtenerHistorialMantenimiento(id);
    if (!historial.length) {
      cuerpo.innerHTML = '<tr><td colspan="5">Todavía no hay servicios registrados para esta pieza.</td></tr>';
      return;
    }
    cuerpo.innerHTML = historial.map((registro) => `
      <tr>
        <td class="dato-tecnico">${formatearFechaMantenimiento(registro.fecha)}</td>
        <td>${registro.servicio}</td>
        <td>${registro.tecnico}</td>
        <td>${registro.observaciones}</td>
        <td>${registro.documento ? `<a href="${registro.documento}" target="_blank" rel="noopener">Ver documento</a>` : '—'}</td>
      </tr>
    `).join('');
  } catch (error) {
    cuerpo.innerHTML = '<tr><td colspan="5" role="alert">No fue posible cargar el historial de mantenimiento.</td></tr>';
    console.error('[maintenance.js]', error);
  }
}

async function manejarRegistroMantenimiento(evento) {
  evento.preventDefault();
  const formulario = evento.target;
  const boton = formulario.querySelector('button[type="submit"]');
  const id = formulario.dataset.joyaId || TerraeAPI.resolverIdDesdeUrl();

  boton.disabled = true;
  boton.textContent = 'Registrando…';

  try {
    await TerraeAPI.registrarMantenimiento(id, {
      tipo_servicio: formulario.tipoServicio.value,
      detalle: formulario.detalle.value,
    });
    mostrarAlerta(formulario, 'Servicio registrado correctamente. Aparecerá en el historial en unos instantes.', 'exito');
    formulario.reset();
    document.querySelector('[data-modal-cerrar]')?.click();
  } catch (error) {
    mostrarAlerta(formulario, 'No fue posible registrar el servicio. Intenta de nuevo.', 'error');
    console.error('[maintenance.js]', error);
  } finally {
    boton.disabled = false;
    boton.textContent = 'Registrar servicio';
  }
}

function mostrarAlerta(formulario, texto, tipo) {
  const contenedor = formulario.querySelector('[data-mensaje]');
  if (!contenedor) return;
  contenedor.textContent = texto;
  contenedor.className = `estado estado--${tipo}`;
  contenedor.hidden = false;
}

function formatearFechaMantenimiento(iso) {
  return new Date(iso).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' });
}
