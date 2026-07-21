/* ==========================================================================
   TERRAE — style.css
   Base global: reset, design tokens, tipografía, componentes reutilizables.
   "Lo que la tierra esconde, Terrae lo revela"

   Este archivo se carga en TODAS las páginas antes que la hoja de estilos
   específica de cada vista (landing.css, passport.css, admin.css...).
   ========================================================================== */

/* -------------------------------------------------------------------------
   1. FUENTES
   Únicas fuentes permitidas en todo el ecosistema Terrae. Se cargan vía
   Google Fonts en el <head> de cada HTML; aquí solo se declaran las
   variables. Si en producción se auto-hospedan, colocar los .woff2 en
   assets/fonts/ y añadir @font-face aquí sin tocar el resto del sistema.
   ------------------------------------------------------------------------- */
:root {
  --font-display: 'Cormorant Garamond', Georgia, serif;
  --font-ui: 'Jost', 'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;

  /* -----------------------------------------------------------------------
     2. PALETA DE MARCA — extraída directamente del logotipo oficial Terrae.
     No se introduce ningún color fuera de esta paleta en ningún componente.
     ----------------------------------------------------------------------- */
  --terrae-verde-950: #0E3B2E;   /* Verde Terrae — color primario */
  --terrae-verde-800: #164F3D;
  --terrae-verde-700: #1D6249;

  --terrae-oro-500:   #B8935A;   /* Oro Satinado — color secundario */
  --terrae-oro-300:   #D4B685;
  --terrae-oro-700:   #8F7040;

  --terrae-nogal-950: #1A1410;   /* Nogal — color de fondo */
  --terrae-nogal-900: #241C16;
  --terrae-nogal-800: #2E251C;

  --terrae-marfil-100:#F3EDE0;   /* Marfil — color de texto sobre fondo oscuro */
  --terrae-marfil-050:#FAF7F0;

  --terrae-esmeralda-500: #0F9D63; /* Esmeralda — color de resaltado */
  --terrae-esmeralda-300: #3DBE85;

  /* Estados funcionales — derivados de la paleta, nunca colores externos */
  --estado-exito:  var(--terrae-esmeralda-500);
  --estado-alerta: #B8763A;
  --estado-error:  #7A2E2E;
  --estado-info:   var(--terrae-oro-500);

  /* -----------------------------------------------------------------------
     3. ESPACIADO — escala de 8px
     ----------------------------------------------------------------------- */
  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
  --space-5: 48px;
  --space-6: 64px;
  --space-7: 96px;
  --space-8: 128px;

  /* -----------------------------------------------------------------------
     4. TIPOGRAFÍA — escala
     ----------------------------------------------------------------------- */
  --text-display-xl: clamp(2.75rem, 5vw, 4rem);
  --text-display-l:  clamp(1.9rem, 3.2vw, 2.5rem);
  --text-title:      clamp(1.5rem, 2.2vw, 1.75rem);
  --text-body:       1rem;
  --text-body-sm:    0.875rem;
  --text-ui:         0.875rem;
  --text-mono:       0.8125rem;

  /* -----------------------------------------------------------------------
     5. BORDES, SOMBRAS Y MOVIMIENTO — "artesanal", nunca Material Design
     ----------------------------------------------------------------------- */
  --radius-sm: 2px;
  --radius-md: 4px;
  --borde-oro: 1px solid rgba(184, 147, 90, 0.35);
  --borde-oro-fuerte: 1px solid var(--terrae-oro-500);

  --sombra-suave: 0 4px 24px rgba(14, 59, 46, 0.18);
  --sombra-profunda: 0 12px 48px rgba(26, 20, 16, 0.35);

  --easing-terrae: cubic-bezier(0.4, 0, 0.2, 1);
  --duracion-rapida: 250ms;
  --duracion-estandar: 450ms;
  --duracion-lenta: 700ms;

  /* -----------------------------------------------------------------------
     6. LAYOUT
     ----------------------------------------------------------------------- */
  --ancho-maximo: 1240px;
  --ancho-lectura: 720px;
  --altura-navbar: 88px;
}

/* -------------------------------------------------------------------------
   7. RESET — mínimo, deliberado, no un "normalize" genérico completo
   ------------------------------------------------------------------------- */
*, *::before, *::after { box-sizing: border-box; }

html {
  scroll-behavior: smooth;
  -webkit-text-size-adjust: 100%;
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

body {
  margin: 0;
  background: var(--terrae-nogal-950);
  color: var(--terrae-marfil-100);
  font-family: var(--font-ui);
  font-size: var(--text-body);
  font-weight: 300;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}

img, video { max-width: 100%; display: block; }

a { color: inherit; text-decoration: none; }

h1, h2, h3, h4 {
  font-family: var(--font-display);
  font-weight: 500;
  line-height: 1.15;
  margin: 0 0 var(--space-2);
  color: var(--terrae-marfil-050);
}

h1 { font-size: var(--text-display-xl); font-weight: 300; }
h2 { font-size: var(--text-display-l); }
h3 { font-size: var(--text-title); }

p { margin: 0 0 var(--space-2); }

/* Dato técnico: hash, tx_hash, números de certificado, timestamps */
.dato-tecnico, code, .mono {
  font-family: var(--font-mono);
  font-size: var(--text-mono);
  letter-spacing: 0.01em;
  color: var(--terrae-oro-300);
}

/* -------------------------------------------------------------------------
   8. ACCESIBILIDAD — foco visible siempre, nunca outline:none sin reemplazo
   ------------------------------------------------------------------------- */
:focus-visible {
  outline: 2px solid var(--terrae-esmeralda-500);
  outline-offset: 3px;
}

.saltar-contenido {
  position: absolute;
  left: -999px;
  top: 0;
  background: var(--terrae-verde-950);
  color: var(--terrae-marfil-100);
  padding: var(--space-2) var(--space-3);
  z-index: 1000;
  border: var(--borde-oro-fuerte);
}
.saltar-contenido:focus {
  left: var(--space-2);
  top: var(--space-2);
}

.visualmente-oculto {
  position: absolute !important;
  width: 1px; height: 1px;
  padding: 0; margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* -------------------------------------------------------------------------
   9. LAYOUT UTILITARIO
   ------------------------------------------------------------------------- */
.contenedor {
  width: 100%;
  max-width: var(--ancho-maximo);
  margin-inline: auto;
  padding-inline: var(--space-3);
}

.seccion { padding-block: var(--space-7); }
.seccion--compacta { padding-block: var(--space-5); }

.eyebrow {
  font-family: var(--font-ui);
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--terrae-oro-500);
  margin-bottom: var(--space-2);
  display: inline-block;
}

.divisor {
  border: none;
  border-top: var(--borde-oro);
  margin-block: var(--space-4);
}

/* -------------------------------------------------------------------------
   10. NAVBAR (componente reutilizable — usado en todas las páginas)
   ------------------------------------------------------------------------- */
.navbar {
  position: fixed;
  inset-inline: 0;
  top: 0;
  height: var(--altura-navbar);
  display: flex;
  align-items: center;
  z-index: 100;
  background: linear-gradient(to bottom, rgba(26,20,16,0.92), rgba(26,20,16,0));
  transition: background var(--duracion-estandar) var(--easing-terrae);
}

.navbar.navbar--solida {
  background: rgba(26, 20, 16, 0.96);
  border-bottom: var(--borde-oro);
  backdrop-filter: blur(6px);
}

.navbar__inner {
  width: 100%;
  max-width: var(--ancho-maximo);
  margin-inline: auto;
  padding-inline: var(--space-3);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar__logo { display: flex; align-items: center; gap: var(--space-1); }
.navbar__logo img { height: 36px; width: auto; }
.navbar__logo-texto {
  font-family: var(--font-display);
  font-size: 1.35rem;
  letter-spacing: 0.12em;
  color: var(--terrae-marfil-050);
}

.navbar__links {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  list-style: none;
  margin: 0; padding: 0;
}

.navbar__links a {
  font-size: var(--text-ui);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-weight: 400;
  position: relative;
  padding-block: 4px;
}

.navbar__links a::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: -2px;
  height: 1px;
  background: var(--terrae-oro-500);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform var(--duracion-estandar) var(--easing-terrae);
}
.navbar__links a:hover::after,
.navbar__links a:focus-visible::after,
.navbar__links a[aria-current="page"]::after { transform: scaleX(1); }

.navbar__menu-toggle {
  display: none;
  background: none; border: none;
  color: var(--terrae-marfil-100);
  cursor: pointer;
  padding: var(--space-1);
}

/* -------------------------------------------------------------------------
   11. BOTONES
   ------------------------------------------------------------------------- */
.boton {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  font-family: var(--font-ui);
  font-size: var(--text-ui);
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 14px 32px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color var(--duracion-estandar) var(--easing-terrae),
              background-color var(--duracion-estandar) var(--easing-terrae),
              color var(--duracion-estandar) var(--easing-terrae);
  border: var(--borde-oro-fuerte);
  background: transparent;
}

.boton--primario {
  background: var(--terrae-verde-950);
  color: var(--terrae-marfil-100);
}
.boton--primario:hover, .boton--primario:focus-visible {
  border-color: var(--terrae-oro-300);
  background: var(--terrae-verde-800);
}

.boton--secundario {
  background: transparent;
  color: var(--terrae-marfil-100);
  border-color: rgba(184, 147, 90, 0.5);
}
.boton--secundario:hover, .boton--secundario:focus-visible {
  border-color: var(--terrae-oro-300);
  background: rgba(184, 147, 90, 0.08);
}

.boton--esmeralda {
  background: var(--terrae-esmeralda-500);
  color: var(--terrae-nogal-950);
  border-color: var(--terrae-esmeralda-500);
}
.boton--esmeralda:hover, .boton--esmeralda:focus-visible {
  background: var(--terrae-esmeralda-300);
}

.boton:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

.boton--pequeno { padding: 10px 22px; font-size: 0.75rem; }

/* -------------------------------------------------------------------------
   12. CARDS (genérica — landing.css/gallery.css extienden esto)
   ------------------------------------------------------------------------- */
.card {
  background: var(--terrae-nogal-900);
  border: var(--borde-oro);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color var(--duracion-estandar) var(--easing-terrae),
              transform var(--duracion-estandar) var(--easing-terrae);
}
.card:hover { border-color: var(--terrae-oro-300); }

/* -------------------------------------------------------------------------
   13. BADGES / ETIQUETAS / INDICADORES / ESTADOS
   ------------------------------------------------------------------------- */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid currentColor;
}

.badge--verificado { color: var(--terrae-esmeralda-500); }
.badge--pendiente { color: var(--terrae-oro-500); }
.badge--revocado { color: var(--estado-error); }

.badge__punto {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.etiqueta {
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--terrae-oro-500);
}

.estado {
  display: inline-block;
  font-size: 0.75rem;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}
.estado--exito { background: rgba(15, 157, 99, 0.12); color: var(--terrae-esmeralda-500); }
.estado--alerta { background: rgba(184, 118, 58, 0.12); color: var(--estado-alerta); }
.estado--error { background: rgba(122, 46, 46, 0.15); color: #C97F7F; }

/* -------------------------------------------------------------------------
   14. TABS
   ------------------------------------------------------------------------- */
.tabs { border-bottom: var(--borde-oro); display: flex; gap: var(--space-4); }
.tabs__boton {
  background: none; border: none;
  color: rgba(243, 237, 224, 0.6);
  font-family: var(--font-ui);
  font-size: var(--text-ui);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: var(--space-2) 0;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color var(--duracion-estandar) var(--easing-terrae);
}
.tabs__boton[aria-selected="true"] {
  color: var(--terrae-marfil-050);
  border-bottom-color: var(--terrae-oro-500);
}
.tabs__panel { padding-top: var(--space-4); }
.tabs__panel[hidden] { display: none; }

/* -------------------------------------------------------------------------
   15. TABLAS
   ------------------------------------------------------------------------- */
.tabla { width: 100%; border-collapse: collapse; font-size: var(--text-body-sm); }
.tabla th {
  text-align: left;
  font-family: var(--font-ui);
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  color: var(--terrae-nogal-950);
  background: var(--terrae-oro-300);
  padding: var(--space-2);
}
.tabla td {
  padding: var(--space-2);
  border-bottom: 1px solid rgba(184, 147, 90, 0.12);
}
.tabla tbody tr:hover { background: rgba(184, 147, 90, 0.04); }

/* -------------------------------------------------------------------------
   16. MODALES
   ------------------------------------------------------------------------- */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(26, 20, 16, 0.85);
  display: flex; align-items: center; justify-content: center;
  padding: var(--space-3);
  z-index: 200;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--duracion-estandar) var(--easing-terrae);
}
.modal-overlay.esta-abierto { opacity: 1; pointer-events: auto; }

.modal {
  background: var(--terrae-nogal-900);
  border: var(--borde-oro-fuerte);
  border-radius: var(--radius-md);
  max-width: 560px;
  width: 100%;
  padding: var(--space-4);
  box-shadow: var(--sombra-profunda);
  transform: translateY(12px);
  transition: transform var(--duracion-estandar) var(--easing-terrae);
}
.modal-overlay.esta-abierto .modal { transform: translateY(0); }

.modal__cerrar {
  position: absolute;
  top: var(--space-2); right: var(--space-2);
  background: none; border: none;
  color: var(--terrae-marfil-100);
  cursor: pointer;
}

/* -------------------------------------------------------------------------
   17. FORMULARIOS
   ------------------------------------------------------------------------- */
.campo { margin-bottom: var(--space-3); }
.campo__label {
  display: block;
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--terrae-oro-500);
  margin-bottom: var(--space-1);
}
.campo__input,
.campo__select,
.campo__textarea {
  width: 100%;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(184, 147, 90, 0.35);
  color: var(--terrae-marfil-100);
  font-family: var(--font-ui);
  font-size: var(--text-body);
  padding: var(--space-1) 2px;
  transition: border-color var(--duracion-rapida) var(--easing-terrae);
}
.campo__input:focus,
.campo__select:focus,
.campo__textarea:focus {
  outline: none;
  border-bottom-color: var(--terrae-esmeralda-500);
}
.campo__ayuda { font-size: 0.75rem; color: rgba(243, 237, 224, 0.55); margin-top: 4px; }
.campo__error { font-size: 0.75rem; color: #C97F7F; margin-top: 4px; }

/* -------------------------------------------------------------------------
   18. FOOTER
   ------------------------------------------------------------------------- */
.footer {
  border-top: var(--borde-oro);
  padding-block: var(--space-6) var(--space-4);
  background: var(--terrae-nogal-950);
}
.footer__grid {
  display: grid;
  grid-template-columns: 1.3fr 1fr 1fr 1fr;
  gap: var(--space-4);
}
.footer__marca { font-family: var(--font-display); font-size: 1.5rem; }
.footer__slogan {
  font-family: var(--font-display);
  font-style: italic;
  color: rgba(243, 237, 224, 0.6);
  margin-top: var(--space-1);
}
.footer__titulo {
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--terrae-oro-500);
  margin-bottom: var(--space-2);
}
.footer__links { list-style: none; margin: 0; padding: 0; }
.footer__links li { margin-bottom: var(--space-1); }
.footer__links a { font-size: var(--text-body-sm); color: rgba(243, 237, 224, 0.75); }
.footer__links a:hover { color: var(--terrae-oro-300); }
.footer__bottom {
  margin-top: var(--space-5);
  padding-top: var(--space-3);
  border-top: 1px solid rgba(184, 147, 90, 0.15);
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: rgba(243, 237, 224, 0.45);
}

/* -------------------------------------------------------------------------
   19. SCROLL REVEAL (clase que app.js activa vía IntersectionObserver)
   ------------------------------------------------------------------------- */
.revelar {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity var(--duracion-lenta) var(--easing-terrae),
              transform var(--duracion-lenta) var(--easing-terrae);
}
.revelar.esta-visible {
  opacity: 1;
  transform: translateY(0);
}

/* -------------------------------------------------------------------------
   20. LOADER / SKELETON (para datos que vendrán de la API en fases futuras)
   ------------------------------------------------------------------------- */
.skeleton {
  background: linear-gradient(90deg, var(--terrae-nogal-900) 25%, var(--terrae-nogal-800) 50%, var(--terrae-nogal-900) 75%);
  background-size: 200% 100%;
  animation: skeleton-pulso 1.6s ease-in-out infinite;
  border-radius: var(--radius-sm);
}
@keyframes skeleton-pulso {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
