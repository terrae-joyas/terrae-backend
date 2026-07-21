/* ==========================================================================
   TERRAE — gallery.css
   Galería de multimedia del Pasaporte Digital: fotografía editorial, video
   y microscopía. gallery.js controla el lightbox y la carga diferida.
   ========================================================================== */

.galeria {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 220px;
  gap: var(--space-1);
}

.galeria__item {
  position: relative;
  overflow: hidden;
  cursor: pointer;
  background: var(--terrae-nogal-900);
}
.galeria__item:first-child {
  grid-column: span 2;
  grid-row: span 2;
}

.galeria__item img,
.galeria__item video {
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform var(--duracion-lenta) var(--easing-terrae);
}
.galeria__item:hover img,
.galeria__item:hover video { transform: scale(1.05); }

.galeria__item[data-tipo="microscopia"]::after {
  content: 'Microscopía';
  position: absolute;
  left: var(--space-1); bottom: var(--space-1);
  font-size: 0.65rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--terrae-marfil-050);
  background: rgba(26,20,16,0.7);
  padding: 3px 8px;
}

.galeria__item[data-tipo="video"] .galeria__reproducir {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--terrae-marfil-050);
  background: rgba(26,20,16,0.25);
}

/* -------------------------------------------------------------------------
   LIGHTBOX
   ------------------------------------------------------------------------- */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(26, 20, 16, 0.96);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--duracion-estandar) var(--easing-terrae);
}
.lightbox.esta-abierto { opacity: 1; pointer-events: auto; }

.lightbox__contenido { max-width: 90vw; max-height: 85vh; }
.lightbox__contenido img,
.lightbox__contenido video { max-height: 85vh; width: auto; margin-inline: auto; }

.lightbox__cerrar,
.lightbox__anterior,
.lightbox__siguiente {
  position: absolute;
  background: none;
  border: 1px solid rgba(184,147,90,0.4);
  color: var(--terrae-marfil-100);
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
}
.lightbox__cerrar { top: var(--space-3); right: var(--space-3); }
.lightbox__anterior { left: var(--space-3); top: 50%; transform: translateY(-50%); }
.lightbox__siguiente { right: var(--space-3); top: 50%; transform: translateY(-50%); }

.lightbox__contador {
  position: absolute;
  bottom: var(--space-3);
  left: 50%;
  transform: translateX(-50%);
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: rgba(243, 237, 224, 0.6);
}

/* -------------------------------------------------------------------------
   GALERÍA PREMIUM — visor con miniaturas, zoom y modos adicionales
   (Fase 3: "Objetivo UX" — visor profesional, no una simple grilla)
   ------------------------------------------------------------------------- */
.visor-premium {
  display: grid;
  grid-template-columns: 88px 1fr;
  gap: var(--space-2);
  height: 520px;
}

.visor-premium__miniaturas {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  overflow-y: auto;
  list-style: none;
  margin: 0; padding: 0;
}
.visor-premium__miniatura {
  border: 1px solid transparent;
  cursor: pointer;
  overflow: hidden;
  aspect-ratio: 1;
  background: var(--terrae-nogal-900);
}
.visor-premium__miniatura img { width: 100%; height: 100%; object-fit: cover; }
.visor-premium__miniatura[aria-current="true"] { border-color: var(--terrae-oro-500); }

.visor-premium__principal {
  position: relative;
  overflow: hidden;
  border: var(--borde-oro);
  cursor: zoom-in;
  background: var(--terrae-nogal-900);
}
.visor-premium__principal img,
.visor-premium__principal video {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 250ms var(--easing-terrae);
}
.visor-premium__principal.esta-en-zoom img { cursor: zoom-out; }

.visor-premium__controles {
  position: absolute;
  top: var(--space-1); right: var(--space-1);
  display: flex; gap: 6px;
}
.visor-premium__control-boton {
  background: rgba(26,20,16,0.7);
  border: 1px solid rgba(184,147,90,0.4);
  color: var(--terrae-marfil-100);
  width: 32px; height: 32px;
  cursor: pointer;
}

/* Vista 360° — preparada, no funcional aún (Fase 4+) */
.visor-premium__360[hidden],
.visor-premium__modelo-3d[hidden] { display: none; }
.visor-premium__360-placeholder,
.visor-premium__modelo-3d-placeholder {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: var(--space-1);
  background: rgba(26,20,16,0.9);
  color: rgba(243,237,224,0.6);
  font-size: 0.8rem;
  text-align: center;
  padding: var(--space-3);
}

.visor-premium__modo-tabs {
  position: absolute;
  bottom: var(--space-1); left: 50%;
  transform: translateX(-50%);
  display: flex; gap: 4px;
  background: rgba(26,20,16,0.75);
  padding: 4px;
}
.visor-premium__modo-boton {
  background: none; border: none;
  color: rgba(243,237,224,0.6);
  font-size: 0.65rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 6px 10px;
  cursor: pointer;
}
.visor-premium__modo-boton[aria-pressed="true"] {
  background: var(--terrae-oro-500);
  color: var(--terrae-nogal-950);
}
