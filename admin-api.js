/**
 * TERRAE — blockchain.js (Fase 3)
 * -----------------------------------------------------------------------
 * Dos vistas del bloque de verificación blockchain:
 *  - Vista Cliente: sello tranquilizador, sin jerga técnica (Registrado
 *    en Blockchain / Integridad Verificada / Fecha / Red).
 *  - Vista Técnica: wallet, smart contract, hash, token, bloque, gas,
 *    transacción, IPFS — accesible mediante el botón "Ver información
 *    técnica" de la vista Cliente.
 * También controla la visibilidad de la sección NFT (oculta salvo que
 * la pieza tenga NFT asociado).
 * -----------------------------------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  const bloque = document.querySelector('[data-componente="blockchain-vistas"]');
  if (bloque) {
    document.addEventListener('terrae:pasaporte-cargado', (evento) => {
      renderizarVistaCliente(bloque, evento.detail);
    });

    bloque.addEventListener('click', (evento) => {
      if (evento.target.matches('[data-accion="ver-vista-tecnica"]')) {
        mostrarVista(bloque, 'tecnica');
        renderizarVistaTecnica(bloque, ultimoPasaporteCargado);
      }
      if (evento.target.matches('[data-accion="volver-vista-cliente"]')) {
        mostrarVista(bloque, 'cliente');
      }
    });
  }
});

let ultimoPasaporteCargado = null;

function mostrarVista(bloque, nombreVista) {
  bloque.querySelectorAll('.blockchain-vistas__panel').forEach((panel) => {
    panel.hidden = panel.dataset.vistaBlockchain !== nombreVista;
  });
}

function renderizarVistaCliente(bloque, pasaporte) {
  ultimoPasaporteCargado = pasaporte;
  const info = pasaporte.blockchainCliente;
  const panel = bloque.querySelector('[data-vista-blockchain="cliente"]');
  if (!panel) return;

  if (!info || !info.registrado) {
    panel.innerHTML = `
      <div class="blockchain-cliente">
        <p class="estado estado--alerta">Esta pieza aún no ha sido anclada en blockchain. Este bloque se actualizará automáticamente cuando el proceso concluya.</p>
      </div>`;
    return;
  }

  panel.innerHTML = `
    <div class="blockchain-cliente">
      <svg class="blockchain-cliente__icono" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 2 3 6v6c0 5 4 8.5 9 10 5-1.5 9-5 9-10V6l-9-4Z" stroke="currentColor" stroke-width="1.3"/><path d="m8 12 3 3 5-6" stroke="currentColor" stroke-width="1.3"/></svg>
      <h3 class="blockchain-cliente__titulo">Registrado en Blockchain</h3>
      <p class="blockchain-cliente__fecha">Integridad verificada · ${formatearFechaBlockchain(info.fechaRegistro)} · Red ${info.red}</p>
      <button class="boton boton--secundario boton--pequeno blockchain-cliente__detalle-boton" data-accion="ver-vista-tecnica" type="button">Ver información técnica</button>
    </div>`;

  // La sección NFT solo se revela si la pieza tiene NFT asociado.
  const seccionNFT = document.querySelector('.seccion-nft');
  if (seccionNFT && pasaporte.nft) {
    seccionNFT.hidden = false;
    document.dispatchEvent(new CustomEvent('terrae:nft-detectado', { detail: pasaporte.nft }));
  }
}

async function renderizarVistaTecnica(bloque, pasaporte) {
  const panel = bloque.querySelector('[data-vista-blockchain="tecnica"]');
  if (!panel) return;
  panel.innerHTML = '<div class="loader" role="status" aria-label="Cargando detalle técnico"></div>';

  try {
    const detalle = pasaporte.blockchainTecnico || (await TerraeAPI.obtenerDetalleTecnicoBlockchain(pasaporte.id));
    if (!detalle) {
      panel.innerHTML = '<p>No hay información técnica disponible todavía.</p>';
      return;
    }
    panel.innerHTML = `
      <div class="blockchain-tecnica">
        <div class="blockchain-tecnica__campo"><span class="etiqueta">Wallet</span><p class="dato-tecnico">${detalle.wallet}</p></div>
        <div class="blockchain-tecnica__campo"><span class="etiqueta">Smart Contract</span><p class="dato-tecnico">${detalle.smartContract}</p></div>
        <div class="blockchain-tecnica__campo"><span class="etiqueta">Hash</span><p class="dato-tecnico">${detalle.hash}</p></div>
        <div class="blockchain-tecnica__campo"><span class="etiqueta">Token</span><p class="dato-tecnico">${detalle.token}</p></div>
        <div class="blockchain-tecnica__campo"><span class="etiqueta">Bloque</span><p class="dato-tecnico">${detalle.bloque}</p></div>
        <div class="blockchain-tecnica__campo"><span class="etiqueta">Gas</span><p class="dato-tecnico">${detalle.gas}</p></div>
        <div class="blockchain-tecnica__campo"><span class="etiqueta">Transacción</span><p class="dato-tecnico">${detalle.transaccion}</p></div>
        <div class="blockchain-tecnica__campo"><span class="etiqueta">IPFS</span><p class="dato-tecnico">${detalle.ipfs}</p></div>
        <div class="blockchain-tecnica__volver">
          <button class="boton boton--secundario boton--pequeno" data-accion="volver-vista-cliente" type="button">Volver</button>
        </div>
      </div>`;
  } catch (error) {
    panel.innerHTML = '<p role="alert">No fue posible cargar el detalle técnico.</p>';
    console.error('[blockchain.js]', error);
  }
}

function formatearFechaBlockchain(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' });
}
