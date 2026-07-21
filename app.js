/**
 * TERRAE — owner.js (Fase 3)
 * -----------------------------------------------------------------------
 * Controla el bloque .propietario-panel: SECCIÓN PRIVADA de pieza.html.
 * Ninguna información personal del propietario se muestra públicamente
 * (regla explícita de la Fase 3) — este panel solo expone acciones
 * (reclamar titularidad / transferir) y mensajes de estado, nunca datos
 * personales de terceros. Sin backend real todavía, simula dos estados
 * con data-estado="sin-sesion" | "autenticado" en el propio HTML.
 * -----------------------------------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  const panel = document.querySelector('.propietario-panel');
  if (!panel) return;

  panel.dataset.joyaId = TerraeAPI.resolverIdDesdeUrl() || panel.dataset.joyaId;
  actualizarEstadoPanel(panel);

  const formulario = panel.querySelector('[data-form="registrar-propietario"]');
  if (formulario) {
    formulario.addEventListener('submit', (evento) => manejarEnvioPropietario(evento, panel));
  }

  const botonReclamar = panel.querySelector('[data-accion="reclamar-pieza"]');
  if (botonReclamar) {
    botonReclamar.addEventListener('click', () => {
      // Punto de integración futuro: redirigir a login.html con returnTo=pieza actual.
      const destino = new URL('login.html', window.location.href);
      destino.searchParams.set('returnTo', window.location.href);
      window.location.href = destino.toString();
    });
  }
});

function actualizarEstadoPanel(panel) {
  const haySesion = Boolean(TerraeAPI.getAccessToken());
  panel.dataset.estado = haySesion ? 'autenticado' : 'sin-sesion';
}

async function manejarEnvioPropietario(evento, panel) {
  evento.preventDefault();
  const formulario = evento.target;
  const boton = formulario.querySelector('button[type="submit"]');
  const joyaId = panel.dataset.joyaId || 'demo-id';

  const datos = {
    nombreCompleto: formulario.nombreCompleto.value,
    tipoAdquisicion: formulario.tipoAdquisicion.value,
  };

  boton.disabled = true;
  boton.textContent = 'Registrando…';

  try {
    await TerraeAPI.registrarPropietario(joyaId, datos);
    mostrarMensajePanel(panel, 'Titularidad registrada correctamente.', 'exito');
    formulario.reset();
  } catch (error) {
    mostrarMensajePanel(panel, 'No fue posible registrar la titularidad. Intenta de nuevo.', 'error');
    console.error('[owner.js]', error);
  } finally {
    boton.disabled = false;
    boton.textContent = 'Registrar titularidad';
  }
}

function mostrarMensajePanel(panel, texto, tipo) {
  const contenedorMensaje = panel.querySelector('[data-mensaje]');
  if (!contenedorMensaje) return;
  contenedorMensaje.textContent = texto;
  contenedorMensaje.className = `estado estado--${tipo}`;
  contenedorMensaje.hidden = false;
}
