/**
 * TERRAE — gallery.js
 * -----------------------------------------------------------------------
 * Dos responsabilidades:
 *  1. En index.html: puebla [data-fuente="api"] de la sección Colecciones
 *     con tarjetas de pieza desde TerraeAPI.obtenerCatalogo().
 *  2. En pieza.html: construye la galería de multimedia (foto/video/
 *     microscopía) a partir del evento 'terrae:pasaporte-cargado' emitido
 *     por passport.js, y controla el lightbox accesible.
 * -----------------------------------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  const grillaColecciones = document.querySelector('[data-componente="colecciones-grid"]');
  if (grillaColecciones) cargarColecciones(grillaColecciones);

  const visorPremium = document.querySelector('[data-componente="visor-premium"]');
  if (visorPremium) {
    document.addEventListener('terrae:pasaporte-cargado', (evento) => {
      inicializarVisorPremium(visorPremium, evento.detail);
    });
  }

  inicializarLightbox();
});

async function cargarColecciones(contenedor) {
  contenedor.setAttribute('aria-busy', 'true');
  try {
    const piezas = await TerraeAPI.obtenerCatalogo();
    contenedor.innerHTML = piezas.map(tarjetaPiezaHTML).join('');
  } catch (error) {
    contenedor.innerHTML = '<p role="alert">No fue posible cargar la colección en este momento.</p>';
    console.error('[gallery.js]', error);
  } finally {
    contenedor.setAttribute('aria-busy', 'false');
  }
}

function tarjetaPiezaHTML(pieza) {
  return `
    <a class="pieza-card card revelar" href="pieza.html?id=${encodeURIComponent(pieza.id)}">
      <div class="pieza-card__imagen-wrap">
        <img class="pieza-card__imagen" src="${pieza.imagen}" alt="${pieza.nombre}, ${pieza.tipo} Terrae" loading="lazy" width="480" height="600">
      </div>
      <div class="pieza-card__info">
        <span class="pieza-card__nombre">${pieza.nombre}</span>
        <span class="pieza-card__precio">${formatearCOP(pieza.precio)}</span>
      </div>
    </a>`;
}

function renderizarGaleria(contenedor, items) {
  contenedor.innerHTML = items.map((item, indice) => {
    if (item.tipo === 'video') {
      return `
        <div class="galeria__item" data-tipo="video" data-indice="${indice}" role="button" tabindex="0" aria-label="Reproducir video de la pieza">
          <video src="${item.url}" muted preload="metadata"></video>
          <span class="galeria__reproducir" aria-hidden="true">▶</span>
        </div>`;
    }
    const etiqueta = item.tipo === 'microscopia' ? 'Fotografía de microscopía de la esmeralda' : 'Fotografía de la pieza Terrae';
    return `
      <div class="galeria__item" data-tipo="${item.tipo}" data-indice="${indice}" role="button" tabindex="0" aria-label="Ampliar imagen: ${etiqueta}">
        <img src="${item.url}" alt="${etiqueta}" loading="lazy">
      </div>`;
  }).join('');

  contenedor.dataset.items = JSON.stringify(items);
  contenedor.querySelectorAll('.galeria__item').forEach((el) => {
    el.addEventListener('click', () => abrirLightboxEn(items, Number(el.dataset.indice)));
    el.addEventListener('keydown', (evento) => {
      if (evento.key === 'Enter' || evento.key === ' ') {
        evento.preventDefault();
        abrirLightboxEn(items, Number(el.dataset.indice));
      }
    });
  });
}

/* -------------------------------------------------------------------------
   LIGHTBOX
   ------------------------------------------------------------------------- */
let lightboxItems = [];
let lightboxIndiceActual = 0;

function inicializarLightbox() {
  const lightbox = document.querySelector('.lightbox');
  if (!lightbox) return;

  lightbox.querySelector('.lightbox__cerrar')?.addEventListener('click', cerrarLightbox);
  lightbox.querySelector('.lightbox__anterior')?.addEventListener('click', () => moverLightbox(-1));
  lightbox.querySelector('.lightbox__siguiente')?.addEventListener('click', () => moverLightbox(1));
  lightbox.addEventListener('click', (evento) => {
    if (evento.target === lightbox) cerrarLightbox();
  });
  document.addEventListener('keydown', (evento) => {
    if (!lightbox.classList.contains('esta-abierto')) return;
    if (evento.key === 'Escape') cerrarLightbox();
    if (evento.key === 'ArrowRight') moverLightbox(1);
    if (evento.key === 'ArrowLeft') moverLightbox(-1);
  });
}

function abrirLightboxEn(items, indice) {
  lightboxItems = items;
  lightboxIndiceActual = indice;
  const lightbox = document.querySelector('.lightbox');
  if (!lightbox) return;
  renderizarLightboxActual();
  lightbox.classList.add('esta-abierto');
  lightbox.querySelector('.lightbox__cerrar')?.focus();
}

function moverLightbox(delta) {
  lightboxIndiceActual = (lightboxIndiceActual + delta + lightboxItems.length) % lightboxItems.length;
  renderizarLightboxActual();
}

function renderizarLightboxActual() {
  const contenido = document.querySelector('.lightbox__contenido');
  const contador = document.querySelector('.lightbox__contador');
  const item = lightboxItems[lightboxIndiceActual];
  if (!contenido || !item) return;

  contenido.innerHTML = item.tipo === 'video'
    ? `<video src="${item.url}" controls autoplay></video>`
    : `<img src="${item.url}" alt="Vista ampliada, imagen ${lightboxIndiceActual + 1} de ${lightboxItems.length}">`;

  if (contador) contador.textContent = `${lightboxIndiceActual + 1} / ${lightboxItems.length}`;
}

function cerrarLightbox() {
  const lightbox = document.querySelector('.lightbox');
  if (!lightbox) return;
  lightbox.classList.remove('esta-abierto');
  const contenido = document.querySelector('.lightbox__contenido');
  if (contenido) contenido.innerHTML = '';
}

/* -------------------------------------------------------------------------
   VISOR PREMIUM (Fase 3) — imagen principal + miniaturas + zoom +
   pantalla completa + modos 360°/Modelo 3D preparados (no funcionales
   todavía: se muestra un placeholder explicando que llegarán en una
   fase futura, en vez de simular algo que no existe).
   ------------------------------------------------------------------------- */
let visorItemsActuales = [];
let visorIndiceActual = 0;

function inicializarVisorPremium(contenedor, pasaporte) {
  visorItemsActuales = pasaporte.galeria || [];
  visorIndiceActual = 0;

  contenedor.innerHTML = `
    <ul class="visor-premium__miniaturas" role="tablist" aria-label="Miniaturas de la pieza"></ul>
    <div class="visor-premium__principal" tabindex="0" role="img" aria-label="Fotografía principal de la pieza, clic para ampliar">
      <div class="visor-premium__360" hidden>
        <div class="visor-premium__360-placeholder">
          <span>Vista 360°</span>
          <span>Disponible próximamente para esta pieza</span>
        </div>
      </div>
      <div class="visor-premium__modelo-3d" hidden>
        <div class="visor-premium__modelo-3d-placeholder">
          <span>Modelo 3D</span>
          <span>Disponible próximamente para esta pieza</span>
        </div>
      </div>
      <div class="visor-premium__controles">
        <button class="visor-premium__control-boton" data-accion="pantalla-completa" aria-label="Ver en pantalla completa">⤢</button>
      </div>
      <div class="visor-premium__modo-tabs" role="tablist" aria-label="Modo de visualización">
        <button class="visor-premium__modo-boton" data-modo="foto" aria-pressed="true">Fotografía</button>
        <button class="visor-premium__modo-boton" data-modo="360" aria-pressed="false" ${pasaporte.modelo360Disponible ? '' : 'disabled'}>360°</button>
        <button class="visor-premium__modo-boton" data-modo="3d" aria-pressed="false" ${pasaporte.modelo3dDisponible ? '' : 'disabled'}>Modelo 3D</button>
      </div>
    </div>
  `;

  renderizarMiniaturas(contenedor);
  renderizarPrincipal(contenedor);

  contenedor.querySelectorAll('.visor-premium__modo-boton').forEach((boton) => {
    boton.addEventListener('click', () => cambiarModoVisor(contenedor, boton.dataset.modo));
  });

  contenedor.querySelector('[data-accion="pantalla-completa"]')?.addEventListener('click', () => {
    abrirLightboxEn(visorItemsActuales, visorIndiceActual);
  });

  const principal = contenedor.querySelector('.visor-premium__principal');
  principal.addEventListener('click', () => {
    if (principal.dataset.modo && principal.dataset.modo !== 'foto') return;
    principal.classList.toggle('esta-en-zoom');
    const img = principal.querySelector('img');
    if (img) img.style.transform = principal.classList.contains('esta-en-zoom') ? 'scale(1.8)' : 'scale(1)';
  });
}

function renderizarMiniaturas(contenedor) {
  const lista = contenedor.querySelector('.visor-premium__miniaturas');
  lista.innerHTML = visorItemsActuales
    .filter((item) => item.tipo !== 'microscopia')
    .map((item, indice) => `
      <li class="visor-premium__miniatura" data-indice="${indice}" role="tab" tabindex="0" aria-current="${indice === 0}" aria-label="Ver imagen ${indice + 1}">
        <img src="${item.url}" alt="" loading="lazy">
      </li>
    `).join('');

  lista.querySelectorAll('.visor-premium__miniatura').forEach((el) => {
    const seleccionar = () => {
      visorIndiceActual = Number(el.dataset.indice);
      lista.querySelectorAll('.visor-premium__miniatura').forEach((m) => m.setAttribute('aria-current', 'false'));
      el.setAttribute('aria-current', 'true');
      renderizarPrincipal(contenedor);
    };
    el.addEventListener('click', seleccionar);
    el.addEventListener('keydown', (evento) => {
      if (evento.key === 'Enter' || evento.key === ' ') { evento.preventDefault(); seleccionar(); }
    });
  });
}

function renderizarPrincipal(contenedor) {
  const principal = contenedor.querySelector('.visor-premium__principal');
  const item = visorItemsActuales[visorIndiceActual];
  if (!principal || !item) return;

  principal.querySelectorAll('img, video').forEach((el) => el.remove());
  const elemento = item.tipo === 'video'
    ? Object.assign(document.createElement('video'), { src: item.url, controls: true })
    : Object.assign(document.createElement('img'), { src: item.url, alt: 'Fotografía de la pieza Terrae' });
  principal.prepend(elemento);
  principal.classList.remove('esta-en-zoom');
}

function cambiarModoVisor(contenedor, modo) {
  const principal = contenedor.querySelector('.visor-premium__principal');
  principal.dataset.modo = modo;
  contenedor.querySelectorAll('.visor-premium__modo-boton').forEach((b) => {
    b.setAttribute('aria-pressed', String(b.dataset.modo === modo));
  });
  principal.querySelector('.visor-premium__360').hidden = modo !== '360';
  principal.querySelector('.visor-premium__modelo-3d').hidden = modo !== '3d';
  principal.querySelectorAll('img, video').forEach((el) => { el.style.display = modo === 'foto' ? '' : 'none'; });
}
