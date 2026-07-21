/**
 * TERRAE — timeline.js (Fase 3)
 * -----------------------------------------------------------------------
 * Renderiza la línea de tiempo interactiva de trazabilidad. Cada evento
 * puede incluir fecha, lugar, responsable, fotografía/video, hash y
 * estado (completado / en-proceso). Aplica scroll reveal individual por
 * evento reutilizando el observer de app.js (clase .revelar).
 * -----------------------------------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  const contenedor = document.querySelector('[data-componente="timeline"]');
  if (!contenedor) return;

  document.addEventListener('terrae:pasaporte-cargado', (evento) => {
    renderizarTimeline(contenedor, evento.detail.timeline);
  });
});

function renderizarTimeline(contenedor, eventos) {
  if (!eventos || !eventos.length) {
    contenedor.innerHTML = '<p>Todavía no hay eventos registrados para esta pieza.</p>';
    return;
  }

  const ordenados = [...eventos].sort((a, b) => new Date(b.fecha) - new Date(a.fecha));

  contenedor.innerHTML = ordenados.map((evento) => `
    <li class="timeline__item revelar" data-tipo="${evento.tipo}">
      <span class="timeline__punto" aria-hidden="true"></span>
      <time class="timeline__fecha" datetime="${evento.fecha}">${formatearFechaTimeline(evento.fecha)}</time>
      <p class="timeline__titulo">${evento.titulo}</p>
      <p class="timeline__detalle">${evento.detalle}</p>
      ${(evento.lugar || evento.responsable) ? `
        <p class="timeline__lugar-responsable">
          ${evento.lugar ? `<span>📍 ${evento.lugar}</span>` : ''}
          ${evento.responsable ? `<span>👤 ${evento.responsable}</span>` : ''}
        </p>` : ''}
      ${evento.media ? `<div class="timeline__media"><img src="${evento.media}" alt="${evento.titulo}" loading="lazy"></div>` : ''}
      ${evento.hash ? `<p class="timeline__hash" title="${evento.hash}">Hash: ${evento.hash}</p>` : ''}
      <span class="timeline__estado-evento timeline__estado-evento--${evento.estado === 'en-proceso' ? 'en-proceso' : 'completado'}">
        ${evento.estado === 'en-proceso' ? 'En proceso' : 'Completado'}
      </span>
    </li>
  `).join('');

  // Re-observa los nuevos .revelar recién insertados (inyectados después
  // del DOMContentLoaded inicial, por lo que app.js no los vio todavía).
  const nuevosElementos = contenedor.querySelectorAll('.revelar');
  const prefiereMenosMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefiereMenosMovimiento) {
    nuevosElementos.forEach((el) => el.classList.add('esta-visible'));
    return;
  }
  const observador = new IntersectionObserver(
    (entradas) => {
      entradas.forEach((entrada) => {
        if (entrada.isIntersecting) {
          entrada.target.classList.add('esta-visible');
          observador.unobserve(entrada.target);
        }
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -60px 0px' }
  );
  nuevosElementos.forEach((el) => observador.observe(el));
}

function formatearFechaTimeline(iso) {
  return new Date(iso).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' });
}
