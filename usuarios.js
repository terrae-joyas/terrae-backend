/**
 * TERRAE — admin-modules/garantias.js
 * -----------------------------------------------------------------------
 * Módulo 9: Gestión de Garantías. Activación, renovación y visualización
 * de estado por pieza.
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('garantias', {
  async montar(contenedor) {
    const joyas = await AdminAPI.joyas.listar();
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Gestión de Garantías</h1>
            <p class="bo-vista__subtitulo">Activación, renovación y vencimiento de la cobertura por pieza.</p>
          </div>
        </div>
        <div class="campo" style="max-width:420px;margin-bottom:var(--space-3);">
          <label class="campo__label" for="gar-joya">Selecciona una pieza</label>
          <select class="campo__select" id="gar-joya">
            <option value="">— Selecciona —</option>
            ${joyas.map((j) => `<option value="${j.id}">${BO.escapeHtml(j.id)} — ${BO.escapeHtml(j.nombre)}</option>`).join('')}
          </select>
        </div>
        <div id="gar-panel"></div>
      </section>`;

    document.getElementById('gar-joya').addEventListener('change', (evento) => cargarGarantia(evento.target.value));
  },
});

async function cargarGarantia(joyaId) {
  const panel = document.getElementById('gar-panel');
  if (!joyaId) { panel.innerHTML = ''; return; }

  const garantia = await AdminAPI.garantias.obtenerPorJoya(joyaId);

  if (!garantia) {
    panel.innerHTML = `
      <div class="bo-panel">
        <p>Esta pieza todavía no tiene garantía activada.</p>
        <button class="boton boton--esmeralda" data-accion="activar-garantia" type="button">Activar garantía</button>
      </div>`;
    panel.querySelector('[data-accion="activar-garantia"]').addEventListener('click', () => abrirDrawerGarantia(joyaId));
    return;
  }

  const vencida = new Date(garantia.fechaVencimiento) < new Date();
  panel.innerHTML = `
    <div class="garantia-card">
      <div class="garantia-card__item"><div class="garantia-card__valor">${BO.escapeHtml(garantia.fechaActivacion)}</div><div class="garantia-card__label">Activación</div></div>
      <div class="garantia-card__item"><div class="garantia-card__valor">${BO.escapeHtml(garantia.cobertura)}</div><div class="garantia-card__label">Cobertura</div></div>
      <div class="garantia-card__item"><div class="garantia-card__valor">${BO.escapeHtml(garantia.fechaVencimiento)}</div><div class="garantia-card__label">Vencimiento</div></div>
      <div class="garantia-card__item">
        <span class="estado ${vencida ? 'estado--error' : 'estado--exito'}">${vencida ? 'Vencida' : 'Vigente'}</span>
        <div class="garantia-card__label">Estado</div>
      </div>
    </div>
    <p style="margin-top:var(--space-2);">${BO.escapeHtml(garantia.observaciones || 'Sin observaciones.')}</p>
    <button class="boton boton--secundario" data-accion="renovar-garantia" type="button">Renovar garantía</button>
  `;
  panel.querySelector('[data-accion="renovar-garantia"]').addEventListener('click', () => abrirDrawerRenovacion(garantia));
}

function abrirDrawerGarantia(joyaId) {
  const cuerpoHTML = `
    <div class="campo"><label class="campo__label" for="gf-cobertura">Cobertura</label><input class="campo__input" id="gf-cobertura" name="cobertura" placeholder="Reparación y ajuste" required></div>
    <div class="campo"><label class="campo__label" for="gf-vencimiento">Fecha de vencimiento</label><input class="campo__input" id="gf-vencimiento" name="fechaVencimiento" type="date" required></div>
    <div class="campo"><label class="campo__label" for="gf-obs">Observaciones</label><textarea class="campo__textarea" id="gf-obs" name="observaciones" rows="3"></textarea></div>`;

  const { cerrar } = BO.abrirDrawer({
    titulo: `Activar garantía · ${joyaId}`,
    cuerpoHTML,
    async alGuardar(datos) {
      if (!datos.cobertura || !datos.fechaVencimiento) return BO.toast('Completa cobertura y fecha de vencimiento.', 'error');
      await AdminAPI.garantias.activar(joyaId, datos);
      BO.toast('Garantía activada.');
      cerrar();
      cargarGarantia(joyaId);
    },
  });
}

function abrirDrawerRenovacion(garantia) {
  const cuerpoHTML = `<div class="campo"><label class="campo__label" for="rf-vencimiento">Nueva fecha de vencimiento</label><input class="campo__input" id="rf-vencimiento" name="fechaVencimiento" type="date" value="${BO.escapeHtml(garantia.fechaVencimiento)}" required></div>`;
  const { cerrar } = BO.abrirDrawer({
    titulo: 'Renovar garantía',
    cuerpoHTML,
    textoGuardar: 'Renovar',
    async alGuardar(datos) {
      await AdminAPI.garantias.renovar(garantia.id, datos.fechaVencimiento);
      BO.toast('Garantía renovada.');
      cerrar();
      cargarGarantia(garantia.joyaId);
    },
  });
}
