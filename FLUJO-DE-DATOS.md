/* ==========================================================================
   TERRAE — landing.css
   Estilos exclusivos de index.html: hero cinematográfico, storytelling,
   colecciones y filosofía. Depende de style.css (tokens + componentes base).
   ========================================================================== */

/* -------------------------------------------------------------------------
   HERO — pantalla completa, video de fondo, revelado lento del logo
   ------------------------------------------------------------------------- */
.hero {
  position: relative;
  height: 100svh;
  min-height: 640px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  isolation: isolate;
}

.hero__video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -2;
}

/* Overlay Nogal para garantizar contraste con el texto Marfil (WCAG AA) */
.hero__overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(26,20,16,0.55) 0%, rgba(26,20,16,0.35) 45%, rgba(26,20,16,0.85) 100%);
  z-index: -1;
}

.hero__contenido {
  text-align: center;
  max-width: 720px;
  padding-inline: var(--space-3);
  animation: hero-revelado 1.4s var(--easing-terrae) both;
}

@keyframes hero-revelado {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: translateY(0); }
}

.hero__isotipo {
  width: 96px;
  height: auto;
  margin-inline: auto;
  margin-bottom: var(--space-3);
  opacity: 0.95;
}

.hero__marca {
  font-family: var(--font-display);
  font-weight: 300;
  font-size: clamp(2.75rem, 8vw, 5rem);
  letter-spacing: 0.14em;
  color: var(--terrae-marfil-050);
  margin: 0;
}

.hero__slogan {
  font-family: var(--font-display);
  font-style: italic;
  font-size: clamp(1.05rem, 2vw, 1.35rem);
  color: var(--terrae-oro-300);
  margin-top: var(--space-2);
  margin-bottom: var(--space-5);
}

.hero__acciones {
  display: flex;
  gap: var(--space-2);
  justify-content: center;
  flex-wrap: wrap;
}

.hero__scroll-indicador {
  position: absolute;
  bottom: var(--space-4);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  color: rgba(243, 237, 224, 0.6);
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.hero__scroll-linea {
  width: 1px;
  height: 36px;
  background: linear-gradient(to bottom, var(--terrae-oro-500), transparent);
  animation: linea-pulso 2.2s ease-in-out infinite;
}

@keyframes linea-pulso {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* -------------------------------------------------------------------------
   HISTORIA — storytelling en 5 actos (geología, selección, artesanía,
   certificación, legado). Layout editorial, no una grilla de "features".
   ------------------------------------------------------------------------- */
.historia__intro {
  max-width: var(--ancho-lectura);
  margin-inline: auto;
  text-align: center;
  margin-bottom: var(--space-7);
}

.historia__actos {
  display: flex;
  flex-direction: column;
  gap: var(--space-7);
}

.acto {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: var(--space-4);
  align-items: start;
}

.acto:nth-child(even) { direction: rtl; }
.acto:nth-child(even) > * { direction: ltr; }

.acto__numero {
  font-family: var(--font-display);
  font-size: 3.5rem;
  font-weight: 300;
  color: transparent;
  -webkit-text-stroke: 1px var(--terrae-oro-500);
  line-height: 1;
}

.acto__titulo {
  font-family: var(--font-display);
  font-size: var(--text-title);
  color: var(--terrae-marfil-050);
  margin-bottom: var(--space-1);
}

.acto__texto {
  max-width: var(--ancho-lectura);
  color: rgba(243, 237, 224, 0.8);
}

/* -------------------------------------------------------------------------
   COLECCIONES — tarjetas premium (preparadas para carga dinámica vía API)
   ------------------------------------------------------------------------- */
.colecciones__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
  /* data-fuente="api" en el HTML indica a gallery.js que este contenedor
     debe repoblarse con fetch() cuando exista el endpoint /catalogo */
}

.pieza-card {
  position: relative;
  aspect-ratio: 3 / 4;
}

.pieza-card__imagen-wrap {
  height: 78%;
  overflow: hidden;
}

.pieza-card__imagen {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--duracion-lenta) var(--easing-terrae);
}
.pieza-card:hover .pieza-card__imagen { transform: scale(1.045); }

.pieza-card__info {
  padding: var(--space-2);
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.pieza-card__nombre {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 1.05rem;
}

.pieza-card__precio {
  font-family: var(--font-ui);
  font-size: 0.85rem;
  color: var(--terrae-oro-300);
}

/* -------------------------------------------------------------------------
   FILOSOFÍA — sostenibilidad, minería responsable, artesanía, innovación
   ------------------------------------------------------------------------- */
.filosofia { background: var(--terrae-nogal-900); }

.filosofia__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.filosofia__item { border-top: var(--borde-oro); padding-top: var(--space-2); }

.filosofia__icono {
  width: 32px; height: 32px;
  margin-bottom: var(--space-2);
  color: var(--terrae-esmeralda-500);
}

.filosofia__titulo {
  font-family: var(--font-display);
  font-size: 1.15rem;
  margin-bottom: 6px;
}

.filosofia__texto {
  font-size: var(--text-body-sm);
  color: rgba(243, 237, 224, 0.7);
}

/* -------------------------------------------------------------------------
   BLOQUE "VERIFICAR UNA JOYA" — puente hacia pieza.html
   ------------------------------------------------------------------------- */
.verificacion-cta {
  text-align: center;
  border-top: var(--borde-oro);
  border-bottom: var(--borde-oro);
}

.verificacion-cta__form {
  display: flex;
  gap: var(--space-1);
  max-width: 420px;
  margin: var(--space-3) auto 0;
}

.verificacion-cta__form .campo__input {
  border: var(--borde-oro);
  padding: 12px var(--space-2);
  text-align: center;
  letter-spacing: 0.05em;
}
