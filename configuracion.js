/**
 * TERRAE — admin-modules/propietarios.js
 * -----------------------------------------------------------------------
 * Módulo 8: Gestión de Propietarios. Muestra, por pieza seleccionada, el
 * historial completo de titularidad y permite registrar una nueva
 * transferencia. Los datos personales SOLO son visibles aquí (back
 * office autenticado) — nunca se exponen en el Pasaporte Digital público
 * (ver Fase 3, docs/FLUJO-DE-DATOS.md, regla de privacidad).
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('propietarios', {
  async montar(contenedor) {
    const joyas = await AdminAPI.joyas.listar();
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Gestión de Propietarios</h1>
            <p class="bo-vista__subtitulo">Historial de titularidad y transferencias. Información sensible — solo visible en este panel.</p>
          </div>
        </div>
        <div class="campo" style="max-width:420px;margin-bottom:var(--space-3);">
          <label class="campo__label" for="prop-joya">Selecciona una pieza</label>
          <select class="campo__select" id="prop-joya">
            <option value="">— Selecciona —</option>
            ${joyas.map((j) => `<option value="${j.id}">${BO.escapeHtml(j.id)} — ${BO.escapeHtml(j.nombre)}</option>`).join('')}
          </select>
        </div>
        <div id="prop-panel"></div>
      </section>`;

    document.getElementById('prop-joya').addEventListener('change', (evento) => cargarPropietarios(evento.target.value));
  },
});

async function cargarPropietarios(joyaId) {
  const panel = document.getElementById('prop-panel');
  if (!joyaId) { panel.innerHTML = ''; return; }

  const historial = await AdminAPI.propietarios.listarPorJoya(joyaId);
  panel.innerHTML = `
    <div class="bo-panel" style="margin-bottom:var(--space-3);">
      <div class="bo-panel__titulo">Registrar nueva titularidad<button class="boton boton--esmeralda boton--pequeno" data-accion="nueva-transferencia" type="button">Nueva transferencia</button></div>
      <p class="campo__ayuda">Cierra automáticamente el registro vigente anterior y crea uno nuevo.</p>
    </div>
    <div class="bo-tabla-wrap">
      <table class="bo-tabla">
        <thead><tr><th>Propietario</th><th>País / Ciudad</th><th>Adquisición</th><th>Desde</th><th>Hasta</th></tr></thead>
        <tbody>
          ${historial.length ? historial.map((p) => `
            <tr>
              <td>${BO.escapeHtml(p.nombre || '—')}</td>
              <td>${BO.escapeHtml(p.pais || '—')}, ${BO.escapeHtml(p.ciudad || '—')}</td>
              <td>${BO.escapeHtml(p.tipoAdquisicion || '—')}</td>
              <td>${BO.escapeHtml(p.fechaInicio)}</td>
              <td>${p.fechaFin ? BO.escapeHtml(p.fechaFin) : '<span class="estado estado--exito">Vigente</span>'}</td>
            </tr>`).join('') : '<tr><td colspan="5" class="bo-tabla__vacio">Esta pieza no tiene propietarios registrados todavía.</td></tr>'}
        </tbody>
      </table>
    </div>`;

  panel.querySelector('[data-accion="nueva-transferencia"]').addEventListener('click', () => abrirDrawerPropietario(joyaId));
}

function abrirDrawerPropietario(joyaId) {
  const cuerpoHTML = `
    <div class="bo-form-grid">
      <div class="campo campo--ancho-completo"><label class="campo__label" for="pf-nombre">Nombre completo</label><input class="campo__input" id="pf-nombre" name="nombre" required></div>
      <div class="campo"><label class="campo__label" for="pf-pais">País</label><input class="campo__input" id="pf-pais" name="pais" required></div>
      <div class="campo"><label class="campo__label" for="pf-ciudad">Ciudad</label><input class="campo__input" id="pf-ciudad" name="ciudad" required></div>
      <div class="campo"><label class="campo__label" for="pf-fecha">Fecha de compra</label><input class="campo__input" id="pf-fecha" name="fechaCompra" type="date" required></div>
      <div class="campo">
        <label class="campo__label" for="pf-tipo">Tipo de adquisición</label>
        <select class="campo__select" id="pf-tipo" name="tipoAdquisicion">
          <option value="compra">Compra</option><option value="herencia">Herencia</option><option value="transferencia">Transferencia</option>
        </select>
      </div>
    </div>`;

  const { cerrar } = BO.abrirDrawer({
    titulo: `Registrar propietario · ${joyaId}`,
    cuerpoHTML,
    async alGuardar(datos) {
      const { esValido, errores } = BO.validarFormulario(datos, {
        nombre: [BO.validadores.requerido],
        pais: [BO.validadores.requerido],
        ciudad: [BO.validadores.requerido],
      });
      if (!esValido) return BO.toast(Object.values(errores)[0], 'error');

      await AdminAPI.propietarios.registrar(joyaId, datos);
      BO.toast('Propietario registrado. Registro anterior cerrado automáticamente.');
      cerrar();
      cargarPropietarios(joyaId);
    },
  });
}
