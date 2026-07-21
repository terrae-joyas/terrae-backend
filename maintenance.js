/**
 * TERRAE — admin-modules/mantenimientos.js
 * -----------------------------------------------------------------------
 * Módulo 10: Gestión de Mantenimientos. Vista global de todos los
 * servicios (no solo por pieza, a diferencia del panel del cliente en
 * la Fase 3) — útil para el taller que planifica across todo el
 * inventario.
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('mantenimientos', {
  async montar(contenedor) {
    const joyas = await AdminAPI.joyas.listar();
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Gestión de Mantenimientos</h1>
            <p class="bo-vista__subtitulo">Historial de servicios realizados sobre todas las piezas.</p>
          </div>
          <button class="boton boton--esmeralda" data-accion="nuevo-mantenimiento" type="button">Registrar servicio</button>
        </div>
        <div id="mant-tabla"></div>
      </section>`;

    contenedor.querySelector('[data-accion="nuevo-mantenimiento"]').addEventListener('click', () => abrirDrawerMantenimiento(joyas));
    await recargarTablaMantenimientos();
  },
});

async function recargarTablaMantenimientos() {
  const contenedor = document.getElementById('mant-tabla');
  if (!contenedor) return;
  const registros = await AdminAPI.mantenimientos.listarTodos();

  BO.renderizarTabla(contenedor, {
    filaVacia: 'No se han registrado servicios de mantenimiento todavía.',
    columnas: [
      { clave: 'fecha', titulo: 'Fecha', ordenable: true },
      { clave: 'joyaId', titulo: 'Pieza', render: (m) => `<span class="dato-tecnico">${BO.escapeHtml(m.joyaId)}</span>` },
      { clave: 'tipo', titulo: 'Servicio' },
      { clave: 'tecnico', titulo: 'Técnico' },
      { clave: 'comentarios', titulo: 'Observaciones' },
      { clave: 'documentos', titulo: 'Documentos', render: (m) => (m.documentos?.length ? `${m.documentos.length} archivo(s)` : '—') },
    ],
    filas: registros,
  });
}

function abrirDrawerMantenimiento(joyas) {
  const cuerpoHTML = `
    <div class="campo">
      <label class="campo__label" for="mf-joya">Pieza</label>
      <select class="campo__select" id="mf-joya" name="joyaId" required>
        <option value="">Selecciona una pieza…</option>
        ${joyas.map((j) => `<option value="${j.id}">${BO.escapeHtml(j.id)} — ${BO.escapeHtml(j.nombre)}</option>`).join('')}
      </select>
    </div>
    <div class="campo">
      <label class="campo__label" for="mf-tipo">Tipo de mantenimiento</label>
      <select class="campo__select" id="mf-tipo" name="tipo">
        <option value="Limpieza profesional">Limpieza profesional</option>
        <option value="Ajuste y reparación">Ajuste y reparación</option>
        <option value="Recertificación">Recertificación</option>
      </select>
    </div>
    <div class="campo"><label class="campo__label" for="mf-tecnico">Técnico responsable</label><input class="campo__input" id="mf-tecnico" name="tecnico" required></div>
    <div class="campo"><label class="campo__label" for="mf-comentarios">Comentarios</label><textarea class="campo__textarea" id="mf-comentarios" name="comentarios" rows="3"></textarea></div>
    <div class="campo">
      <span class="campo__label">Fotografías (antes / después) y documentos</span>
      <div id="mf-uploader"></div>
    </div>`;

  const { formulario, cerrar } = BO.abrirDrawer({
    titulo: 'Registrar mantenimiento',
    cuerpoHTML,
    async alGuardar(datos) {
      if (!datos.joyaId) return BO.toast('Selecciona una pieza.', 'error');
      if (!datos.tecnico) return BO.toast('Indica el técnico responsable.', 'error');
      await AdminAPI.mantenimientos.registrar(datos.joyaId, datos);
      BO.toast('Servicio de mantenimiento registrado.');
      cerrar();
      recargarTablaMantenimientos();
    },
  });

  BO.inicializarUploader(formulario.querySelector('#mf-uploader'), { tiposPermitidos: ['image/jpeg', 'image/png', 'application/pdf'], maxMB: 20 });
}
