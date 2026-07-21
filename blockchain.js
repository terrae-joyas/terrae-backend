/**
 * TERRAE — microscopy.js
 * -----------------------------------------------------------------------
 * Renderiza la sección "La Huella Digital de tu Esmeralda": fotografía
 * microscópica con inclusiones señaladas manualmente por el gemólogo
 * (coordenadas x/y ya documentadas, ver PIEZAS_DEMO.microscopia en
 * app.js). No implementa análisis automático — solo prepara el punto
 * de integración para cuando EmeraldChain Core exponga detección de
 * inclusiones por IA (nota visible al usuario, ver componente
 * .huella-digital__ia-nota).
 * -----------------------------------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  const contenedor = document.querySelector('[data-componente="huella-digital"]');
  if (!contenedor) return;

  document.addEventListener('terrae:pasaporte-cargado', (evento) => {
    renderizarHuellaDigital(contenedor, evento.detail.microscopia);
  });
});

function renderizarHuellaDigital(contenedor, microscopia) {
  if (!microscopia) {
    contenedor.innerHTML = '<p>La microscopía de esta pieza se publicará cuando esté disponible.</p>';
    return;
  }

  const puntosHTML = (microscopia.inclusiones || [])
    .map((inclusion, indice) => `
      <button
        class="huella-digital__punto"
        style="--x:${inclusion.x}; --y:${inclusion.y};"
        data-indice="${indice}"
        aria-expanded="false"
        aria-label="Inclusión: ${inclusion.tipo}"
        type="button"
      >
        <span class="huella-digital__tooltip">${inclusion.tipo}</span>
      </button>`)
    .join('');

  contenedor.innerHTML = `
    <div class="huella-digital">
      <div class="huella-digital__visor">
        <img src="${microscopia.imagen}" alt="Fotografía microscópica de la esmeralda con inclusiones señaladas">
        ${puntosHTML}
      </div>
      <div class="huella-digital__info">
        <p>${microscopia.descripcionTecnica}</p>
        <ul class="huella-digital__lista">
          ${(microscopia.inclusiones || [])
            .map((inclusion) => `<li><span>${inclusion.tipo}</span><span>${inclusion.descripcion}</span></li>`)
            .join('')}
        </ul>
        <p class="huella-digital__ia-nota">La detección automática de inclusiones por inteligencia artificial (EmeraldChain Core) se habilitará en una fase posterior. Hoy, cada inclusión es documentada manualmente por un gemólogo certificado.</p>
      </div>
    </div>`;

  contenedor.querySelectorAll('.huella-digital__punto').forEach((boton) => {
    boton.addEventListener('click', () => {
      const yaAbierto = boton.getAttribute('aria-expanded') === 'true';
      contenedor.querySelectorAll('.huella-digital__punto').forEach((b) => b.setAttribute('aria-expanded', 'false'));
      boton.setAttribute('aria-expanded', String(!yaAbierto));
    });
  });
}
