/**
 * TERRAE — nft.js
 * -----------------------------------------------------------------------
 * La sección NFT permanece con `hidden` en pieza.html por defecto. Se
 * revela ÚNICAMENTE cuando blockchain.js detecta que pasaporte.nft no es
 * null (ver evento 'terrae:nft-detectado'), y solo entonces se rellena
 * con Token ID, imagen, red, marketplace y wallet — tal como pide la
 * Fase 3: "Preparar una sección oculta. Mostrar únicamente si la joya
 * posee NFT."
 * -----------------------------------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  const seccion = document.querySelector('.seccion-nft');
  if (!seccion) return;

  document.addEventListener('terrae:nft-detectado', (evento) => {
    renderizarNFT(seccion, evento.detail);
  });
});

function renderizarNFT(seccion, nft) {
  if (!nft) return;
  seccion.innerHTML = `
    <div class="contenedor" style="text-align:center;">
      <span class="eyebrow">Edición digital</span>
      <h2>NFT de esta pieza</h2>
      <div class="bloque-blockchain" style="margin-top: var(--space-3);">
        <div class="bloque-blockchain__campo"><span class="etiqueta">Token ID</span><p class="dato-tecnico">${nft.tokenId}</p></div>
        <div class="bloque-blockchain__campo"><span class="etiqueta">Red</span><p>${nft.red}</p></div>
        <div class="bloque-blockchain__campo"><span class="etiqueta">Marketplace</span><p><a href="${nft.marketplaceUrl || '#'}" target="_blank" rel="noopener">${nft.marketplace || '—'}</a></p></div>
      </div>
      ${nft.imagen ? `<img src="${nft.imagen}" alt="Representación digital NFT de la pieza" style="max-width:280px;margin:var(--space-3) auto 0;border:1px solid var(--terrae-oro-500);">` : ''}
      <p class="dato-tecnico" style="margin-top:var(--space-2);">Wallet: ${nft.wallet || '—'}</p>
    </div>`;
}
