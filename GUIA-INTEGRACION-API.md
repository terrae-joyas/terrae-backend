/* ==========================================================================
   TERRAE — passport.css
   Estilos del Pasaporte Digital (pieza.html). Orquesta las secciones que
   certificate.css, timeline.css y gallery.css estilizan en detalle.
   ========================================================================== */

.pasaporte-hero {
  padding-top: calc(var(--altura-navbar) + var(--space-6));
  padding-bottom: var(--space-6);
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: var(--space-6);
  align-items: center;
}

.pasaporte-hero__imagen {
  aspect-ratio: 4 / 5;
  overflow: hidden;
  border: var(--borde-oro);
}
.pasaporte-hero__imagen img { width: 100%; height: 100%; object-fit: cover; }

.pasaporte-hero__sku {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: rgba(243, 237, 224, 0.5);
  margin-bottom: var(--space-1);
}

.pasaporte-hero__nombre { font-size: var(--text-display-l); }

.pasaporte-hero__esmeralda {
  display: flex;
  gap: var(--space-4);
  margin-block: var(--space-3);
  padding: var(--space-2) 0;
  border-top: var(--borde-oro);
  border-bottom: var(--borde-oro);
}

.pasaporte-hero__dato { display: flex; flex-direction: column; gap: 2px; }
.pasaporte-hero__dato-label {
  font-size: 0.65rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--terrae-oro-500);
}
.pasaporte-hero__dato-valor { font-family: var(--font-mono); font-size: 0.85rem; }

.pasaporte-hero__badges { display: flex; gap: var(--space-1); margin-bottom: var(--space-3); }

.pasaporte-hero__acciones { display: flex; gap: var(--space-2); flex-wrap: wrap; }

/* -------------------------------------------------------------------------
   NAVEGACIÓN INTERNA DEL PASAPORTE (ancla a cada sección)
   ------------------------------------------------------------------------- */
.pasaporte-nav {
  position: sticky;
  top: var(--altura-navbar);
  z-index: 50;
  background: rgba(26, 20, 16, 0.96);
  border-bottom: var(--borde-oro);
  backdrop-filter: blur(6px);
  overflow-x: auto;
}
.pasaporte-nav__lista {
  display: flex;
  gap: var(--space-4);
  list-style: none;
  margin: 0; padding: var(--space-2) var(--space-3);
  white-space: nowrap;
}
.pasaporte-nav__lista a {
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(243, 237, 224, 0.6);
}
.pasaporte-nav__lista a:hover,
.pasaporte-nav__lista a:focus-visible { color: var(--terrae-oro-300); }

/* -------------------------------------------------------------------------
   SECCIÓN: HISTORIA DE LA PIEZA
   ------------------------------------------------------------------------- */
.pasaporte-historia { max-width: var(--ancho-lectura); margin-inline: auto; text-align: center; }

/* -------------------------------------------------------------------------
   SECCIÓN: GARANTÍA
   ------------------------------------------------------------------------- */
.garantia-card {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  padding: var(--space-4);
  border: var(--borde-oro);
}
.garantia-card__item { text-align: center; }
.garantia-card__valor {
  font-family: var(--font-display);
  font-size: 1.75rem;
  color: var(--terrae-esmeralda-500);
}
.garantia-card__label {
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(243, 237, 224, 0.6);
}

/* -------------------------------------------------------------------------
   SECCIÓN: REGISTRO DEL PROPIETARIO
   Punto de integración: owner.js rellenará este bloque con la sesión
   autenticada del cliente cuando exista JWT (Fase 3).
   ------------------------------------------------------------------------- */
.propietario-panel {
  border: var(--borde-oro);
  padding: var(--space-4);
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: var(--space-3);
}
.propietario-panel__texto { max-width: 480px; }
.propietario-panel[data-estado="sin-sesion"] .propietario-panel__solo-autenticado { display: none; }
.propietario-panel[data-estado="autenticado"] .propietario-panel__solo-anonimo { display: none; }

/* -------------------------------------------------------------------------
   SECCIÓN: SERVICIOS / MANTENIMIENTO — CTA hacia agendar servicio
   ------------------------------------------------------------------------- */
.servicios-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}
.servicio-card { padding: var(--space-3); text-align: center; }
.servicio-card__icono { width: 28px; height: 28px; margin: 0 auto var(--space-2); color: var(--terrae-oro-500); }

/* -------------------------------------------------------------------------
   SECCIÓN NFT — oculta hasta que el negocio la habilite (Fase 6).
   blockchain.js revisa window.TERRAE_CONFIG.nftHabilitado antes de
   remover el atributo hidden; nunca se elimina por CSS solamente,
   así el contenido no vive en el DOM renderizado si está desactivado.
   ------------------------------------------------------------------------- */
.seccion-nft[hidden] { display: none; }
.seccion-nft {
  border: 1px dashed rgba(184, 147, 90, 0.4);
  padding: var(--space-4);
  text-align: center;
}

/* -------------------------------------------------------------------------
   ESTADOS DEL PASAPORTE (Fase 3) — cargando / error / no encontrada /
   descontinuada / vendida / certificado pendiente. Un único contenedor
   [data-estado-pasaporte] visible según el estado que passport.js determine;
   el contenido principal permanece oculto mientras no sea "listo".
   ------------------------------------------------------------------------- */
[data-estado-pasaporte] { display: none; }
[data-estado-pasaporte].esta-activo { display: block; }

.estado-pantalla {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--space-6) var(--space-3);
  gap: var(--space-2);
}

.estado-pantalla__icono {
  width: 48px; height: 48px;
  color: var(--terrae-oro-500);
  margin-bottom: var(--space-2);
}
.estado-pantalla[data-tipo="error"] .estado-pantalla__icono,
.estado-pantalla[data-tipo="no-encontrada"] .estado-pantalla__icono { color: #C97F7F; }
.estado-pantalla[data-tipo="vendida"] .estado-pantalla__icono,
.estado-pantalla[data-tipo="descontinuada"] .estado-pantalla__icono { color: rgba(243,237,224,0.4); }

.estado-pantalla__titulo { font-family: var(--font-display); font-size: 1.75rem; }
.estado-pantalla__texto { max-width: 420px; color: rgba(243, 237, 224, 0.65); }

/* Loader genérico reutilizable (spinner discreto, no un "cargando..." de app) */
.loader {
  width: 28px; height: 28px;
  border: 2px solid rgba(184, 147, 90, 0.25);
  border-top-color: var(--terrae-oro-500);
  border-radius: 50%;
  animation: loader-girar 900ms linear infinite;
}
@keyframes loader-girar { to { transform: rotate(360deg); } }

/* Aviso de certificado pendiente — banner no bloqueante sobre el hero */
.aviso-certificado-pendiente {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  border: 1px solid var(--terrae-oro-500);
  background: rgba(184, 147, 90, 0.08);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-body-sm);
  margin-bottom: var(--space-3);
}

/* -------------------------------------------------------------------------
   HISTORIA DE LA ESMERALDA — 9 etapas narrativas (Fase 3), cada una
   soporta texto + fotografía/video/documento; se reutiliza .acto de
   landing.css con una variante compacta para el contexto del pasaporte.
   ------------------------------------------------------------------------- */
.historia-esmeralda__etapas {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}
.etapa {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: var(--space-2);
}
.etapa__numero {
  font-family: var(--font-display);
  font-size: 2rem;
  color: transparent;
  -webkit-text-stroke: 1px var(--terrae-oro-500);
}
.etapa__titulo { font-family: var(--font-display); font-size: 1.2rem; margin-bottom: 4px; }
.etapa__media {
  margin-top: var(--space-2);
  max-width: 320px;
  aspect-ratio: 16/10;
  overflow: hidden;
  border: var(--borde-oro);
}
.etapa__media img, .etapa__media video { width: 100%; height: 100%; object-fit: cover; }
.etapa__documento {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: var(--space-1);
  font-size: 0.8rem;
  color: var(--terrae-oro-300);
}

/* -------------------------------------------------------------------------
   HISTORIAL DE MANTENIMIENTO — tabla dinámica
   ------------------------------------------------------------------------- */
.mantenimiento-panel { display: flex; flex-direction: column; gap: var(--space-3); }
.mantenimiento-panel__acciones { display: flex; justify-content: flex-end; }
