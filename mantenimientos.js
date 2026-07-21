/**
 * TERRAE — admin-modules/blockchain-admin.js
 * -----------------------------------------------------------------------
 * Módulo 7: Gestión Blockchain. Interfaz administrativa para registrar
 * manualmente los datos de anclaje (hash, wallet, smart contract, bloque,
 * gas) y consultar el estado. NO se conecta a Polygon real todavía — el
 * estado nunca pasa a "verificado" automáticamente, solo "pendiente"
 * hasta que exista integración real (ver docs/GUIA-INTEGRACION-API.md).
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('blockchain', {
  async montar(contenedor) {
    const joyas = await AdminAPI.joyas.listar();
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Gestión Blockchain</h1>
            <p class="bo-vista__subtitulo">Registro manual de anclaje. La conexión real a Polygon se habilita en una fase posterior.</p>
          </div>
        </div>
        <div class="bo-panel" style="margin-bottom:var(--space-3);">
          <div class="bo-panel__titulo">Registrar anclaje</div>
          <form id="bc-form" class="bo-form-grid">
            <div class="campo campo--ancho-completo">
              <label class="campo__label" for="bc-joya">Pieza</label>
              <select class="campo__select" id="bc-joya" name="joyaId" required>
                <option value="">Selecciona una pieza…</option>
                ${joyas.map((j) => `<option value="${j.id}">${BO.escapeHtml(j.id)} — ${BO.escapeHtml(j.nombre)}</option>`).join('')}
              </select>
            </div>
            <div class="campo"><label class="campo__label" for="bc-hash">Hash</label><input class="campo__input" id="bc-hash" name="hash" required></div>
            <div class="campo"><label class="campo__label" for="bc-wallet">Wallet</label><input class="campo__input" id="bc-wallet" name="wallet" required></div>
            <div class="campo"><label class="campo__label" for="bc-contrato">Smart Contract</label><input class="campo__input" id="bc-contrato" name="smartContract" required></div>
            <div class="campo"><label class="campo__label" for="bc-bloque">Bloque</label><input class="campo__input" id="bc-bloque" name="bloque"></div>
            <div class="campo campo--ancho-completo"><label class="campo__label" for="bc-gas">Gas</label><input class="campo__input" id="bc-gas" name="gas"></div>
            <div class="campo--ancho-completo" style="text-align:right;">
              <button class="boton boton--esmeralda" type="submit">Registrar</button>
            </div>
          </form>
        </div>
        <div id="bc-tabla"></div>
      </section>`;

    document.getElementById('bc-form').addEventListener('submit', async (evento) => {
      evento.preventDefault();
      const datos = Object.fromEntries(new FormData(evento.target).entries());
      if (!datos.joyaId) return BO.toast('Selecciona una pieza.', 'error');
      await AdminAPI.blockchain.registrar(datos.joyaId, datos);
      BO.toast('Registro blockchain guardado (estado: pendiente de verificación real).');
      evento.target.reset();
      recargarTablaBlockchain();
    });

    await recargarTablaBlockchain();
  },
});

async function recargarTablaBlockchain() {
  const contenedor = document.getElementById('bc-tabla');
  if (!contenedor) return;
  const registros = await AdminAPI.blockchain.listar();

  BO.renderizarTabla(contenedor, {
    filaVacia: 'Todavía no hay registros de anclaje.',
    columnas: [
      { clave: 'joyaId', titulo: 'Pieza', render: (r) => `<span class="dato-tecnico">${BO.escapeHtml(r.joyaId)}</span>` },
      { clave: 'hash', titulo: 'Hash', render: (r) => `<span class="dato-tecnico">${BO.escapeHtml(acortar(r.hash))}</span>` },
      { clave: 'wallet', titulo: 'Wallet', render: (r) => `<span class="dato-tecnico">${BO.escapeHtml(acortar(r.wallet))}</span>` },
      { clave: 'bloque', titulo: 'Bloque' },
      { clave: 'estado', titulo: 'Estado', render: (r) => `<span class="estado ${r.estado === 'verificado' ? 'estado--exito' : 'estado--alerta'}">${BO.escapeHtml(r.estado)}</span>` },
      {
        clave: 'acciones', titulo: '', render: (r) => `<div class="bo-tabla__acciones"><button class="bo-tabla__icono-boton" data-consultar="${r.joyaId}" type="button" title="Consultar estado">⟳</button></div>`,
      },
    ],
    filas: registros,
  });

  contenedor.querySelectorAll('[data-consultar]').forEach((b) => b.addEventListener('click', async () => {
    const resultado = await AdminAPI.blockchain.consultarEstado(b.dataset.consultar);
    BO.toast(`Estado consultado: ${resultado.estado}. La verificación real requiere la integración de Fase 5.`, 'alerta');
  }));
}

function acortar(valor) {
  if (!valor || valor.length <= 18) return valor || '—';
  return `${valor.slice(0, 10)}…${valor.slice(-6)}`;
}
