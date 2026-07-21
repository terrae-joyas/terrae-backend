/* ==========================================================================
   TERRAE — timeline.css
   Línea de tiempo del Pasaporte Digital: cadena de custodia (propietarios)
   e historial de mantenimiento. Un único componente visual para ambos,
   diferenciado por el color del punto (Esmeralda = evento certificado /
   blockchain, Oro = mantenimiento).
   ========================================================================== */

.timeline {
  position: relative;
  padding-left: var(--space-5);
  list-style: none;
  margin: 0;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 6px;
  bottom: 6px;
  width: 1px;
  background: linear-gradient(to bottom, var(--terrae-oro-500), rgba(184,147,90,0.15));
}

.timeline__item {
  position: relative;
  padding-bottom: var(--space-4);
}
.timeline__item:last-child { padding-bottom: 0; }

.timeline__punto {
  position: absolute;
  left: -29px;
  top: 4px;
  width: 12px; height: 12px;
  border-radius: 50%;
  background: var(--terrae-oro-500);
  border: 2px solid var(--terrae-nogal-950);
  box-shadow: 0 0 0 1px rgba(184,147,90,0.4);
}
.timeline__item[data-tipo="certificacion"] .timeline__punto,
.timeline__item[data-tipo="blockchain"] .timeline__punto {
  background: var(--terrae-esmeralda-500);
  box-shadow: 0 0 0 1px rgba(15,157,99,0.4);
}

.timeline__fecha {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: rgba(243, 237, 224, 0.5);
  display: block;
  margin-bottom: 2px;
}

.timeline__titulo {
  font-family: var(--font-ui);
  font-weight: 500;
  font-size: var(--text-body-sm);
  color: var(--terrae-marfil-050);
  margin-bottom: 2px;
}

.timeline__detalle {
  font-size: var(--text-body-sm);
  color: rgba(243, 237, 224, 0.7);
}

.timeline__meta {
  font-size: 0.7rem;
  color: var(--terrae-oro-500);
  margin-top: 4px;
}

/* Estado de carga mientras timeline.js resuelve fetch() al backend */
.timeline--cargando .timeline__item { }
.timeline__skeleton-item {
  height: 52px;
  margin-bottom: var(--space-2);
}

/* -------------------------------------------------------------------------
   TIMELINE ENRIQUECIDO (Fase 3) — cada evento puede mostrar lugar,
   responsable, fotografía/video, hash y estado, con scroll reveal propio.
   ------------------------------------------------------------------------- */
.timeline__item.revelar { padding-bottom: var(--space-5); }

.timeline__lugar-responsable {
  display: flex;
  gap: var(--space-2);
  font-size: 0.75rem;
  color: rgba(243, 237, 224, 0.55);
  margin-top: 4px;
}
.timeline__lugar-responsable span { display: inline-flex; align-items: center; gap: 4px; }

.timeline__media {
  margin-top: var(--space-2);
  width: 160px;
  aspect-ratio: 4/3;
  overflow: hidden;
  border: var(--borde-oro);
}
.timeline__media img,
.timeline__media video { width: 100%; height: 100%; object-fit: cover; }

.timeline__hash {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--terrae-oro-300);
  margin-top: 4px;
  word-break: break-all;
}

.timeline__estado-evento {
  display: inline-block;
  margin-top: 4px;
  font-size: 0.65rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}
.timeline__estado-evento--completado { background: rgba(15,157,99,0.12); color: var(--terrae-esmeralda-500); }
.timeline__estado-evento--en-proceso { background: rgba(184,118,58,0.12); color: var(--estado-alerta); }
