/**
 * TERRAE — passport.js (Fase 3 — Pasaporte Digital Inteligente)
 * -----------------------------------------------------------------------
 * Orquesta pieza.html: resuelve el ID desde la URL (?id=... o /pieza/{id}),
 * solicita el pasaporte a TerraeAPI y gestiona los 6 estados exigidos:
 * cargando, error, no encontrada, descontinuada, vendida, certificado
 * pendiente. Solo cuando el estado es "activa" (o "certificado_pendiente"
 * con datos parciales) se rellena el resto del DOM y se notifica a los
 * demás módulos (gallery.js, timeline.js, blockchain.js, microscopy.js,
 * maintenance.js, owner.js, nft.js) vía el evento 'terrae:pasaporte-cargado'.
 * -----------------------------------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  const raiz = document.querySelector('[data-pagina="pasaporte"]');
  if (!raiz) return;

  const id = TerraeAPI.resolverIdDesdeUrl();
  if (!id) {
    mostrarEstado('no-encontrada', { titulo: 'Falta el identificador de la pieza', texto: 'Verifica el enlace o el código QR e inténtalo de nuevo.' });
    return;
  }

  cargarPasaporte(id);
  inicializarAccionesCertificado();
});

function inicializarAccionesCertificado() {
  document.querySelector('[data-accion="imprimir-certificado"]')?.addEventListener('click', () => window.print());

  document.querySelector('[data-accion="compartir-certificado"]')?.addEventListener('click', async () => {
    const datosCompartir = {
      title: 'Pasaporte Digital Terrae',
      text: 'Verifica la autenticidad de esta joya Terrae.',
      url: window.location.href,
    };
    if (navigator.share) {
      try { await navigator.share(datosCompartir); } catch { /* el usuario canceló, no es un error */ }
    } else {
      await navigator.clipboard.writeText(window.location.href);
      alert('Enlace copiado al portapapeles.');
    }
  });
}

async function cargarPasaporte(id) {
  mostrarEstado('cargando');
  try {
    const pasaporte = await TerraeAPI.obtenerPasaportePorId(id);

    switch (pasaporte.estado) {
      case 'descontinuada':
        mostrarEstado('descontinuada', {
          titulo: pasaporte.nombre ? `"${pasaporte.nombre}" ya no forma parte de la colección activa` : 'Esta pieza fue descontinuada',
          texto: 'Su historia y certificación permanecen documentadas, pero ya no está disponible en catálogo.',
        });
        return;
      case 'vendida':
        mostrarEstado('vendida', {
          titulo: pasaporte.nombre ? `"${pasaporte.nombre}" ya tiene un propietario` : 'Esta pieza ya fue vendida',
          texto: 'El Pasaporte Digital de esta joya pertenece ahora a su propietario registrado.',
        });
        return;
      case 'certificado_pendiente':
        mostrarEstado('listo');
        mostrarAvisoCertificadoPendiente();
        renderizarContenido(pasaporte, id);
        return;
      default:
        mostrarEstado('listo');
        renderizarContenido(pasaporte, id);
    }
  } catch (error) {
    if (error.status === 404) {
      mostrarEstado('no-encontrada', {
        titulo: 'No encontramos esta pieza',
        texto: 'Revisa el código ingresado o el QR escaneado. Si el problema persiste, contáctanos.',
      });
    } else {
      mostrarEstado('error', {
        titulo: 'No fue posible cargar el Pasaporte Digital',
        texto: 'Ocurrió un problema al consultar la información. Intenta de nuevo en unos minutos.',
      });
    }
    console.error('[passport.js]', error);
  }
}

/* -------------------------------------------------------------------------
   MÁQUINA DE ESTADOS DE PANTALLA
   ------------------------------------------------------------------------- */
function mostrarEstado(nombreEstado, contenido) {
  document.querySelectorAll('[data-estado-pasaporte]').forEach((el) => {
    el.classList.toggle('esta-activo', el.dataset.estadoPasaporte === nombreEstado);
  });

  if (contenido) {
    const contenedor = document.querySelector(`[data-estado-pasaporte="${nombreEstado}"] .estado-pantalla__titulo`);
    const texto = document.querySelector(`[data-estado-pasaporte="${nombreEstado}"] .estado-pantalla__texto`);
    if (contenedor) contenedor.textContent = contenido.titulo;
    if (texto) texto.textContent = contenido.texto;
  }
}

function mostrarAvisoCertificadoPendiente() {
  const aviso = document.querySelector('[data-aviso-certificado-pendiente]');
  if (aviso) aviso.hidden = false;
}

/* -------------------------------------------------------------------------
   RENDERIZADO DEL CONTENIDO PRINCIPAL
   ------------------------------------------------------------------------- */
function renderizarContenido(pasaporte, id) {
  renderizarHero(pasaporte, id);
  renderizarHistoria(pasaporte.historia);
  renderizarCertificado(pasaporte);
  renderizarGarantia(pasaporte.garantia);

  document.dispatchEvent(new CustomEvent('terrae:pasaporte-cargado', { detail: { ...pasaporte, id } }));
}

function renderizarHero(pasaporte, id) {
  setTexto('[data-campo="id-pieza"]', id);
  setTexto('[data-campo="nombre"]', pasaporte.nombre);
  setTexto('[data-campo="coleccion"]', pasaporte.coleccion || '—');
  setTexto('[data-campo="metal"]', pasaporte.metal || '—');
  setTexto('[data-campo="peso"]', pasaporte.pesoGramos ? `${pasaporte.pesoGramos} g` : '—');

  if (pasaporte.esmeralda) {
    setTexto('[data-campo="origen"]', pasaporte.esmeralda.origenPredicho);
    setTexto('[data-campo="quilates"]', `${pasaporte.esmeralda.quilates} ct`);
    setTexto('[data-campo="color-grado"]', pasaporte.esmeralda.colorGrado);
    setTexto('[data-campo="tratamiento"]', pasaporte.esmeralda.tratamiento);
  }

  const imagenHero = document.querySelector('[data-campo="imagen-principal"]');
  if (imagenHero && pasaporte.imagenPrincipal) imagenHero.src = pasaporte.imagenPrincipal;

  const badgeEstado = document.querySelector('[data-campo="badge-estado"]');
  if (badgeEstado) {
    const mapaEstados = {
      activa: ['Certificada', 'badge--verificado'],
      certificado_pendiente: ['Certificación en proceso', 'badge--pendiente'],
    };
    const [texto, clase] = mapaEstados[pasaporte.estado] || ['—', 'badge--pendiente'];
    badgeEstado.textContent = texto;
    badgeEstado.className = `badge ${clase}`;
  }
}

function renderizarHistoria(etapas) {
  const contenedor = document.querySelector('[data-componente="historia-esmeralda"]');
  if (!contenedor) return;
  if (!etapas || !etapas.length) {
    contenedor.innerHTML = '<p>La historia detallada de esta pieza se publicará próximamente.</p>';
    return;
  }
  contenedor.innerHTML = etapas.map((etapa, indice) => `
    <article class="etapa revelar">
      <span class="etapa__numero" aria-hidden="true">${String(indice + 1).padStart(2, '0')}</span>
      <div>
        <h3 class="etapa__titulo">${etapa.titulo}</h3>
        <p>${etapa.texto}</p>
        ${etapa.media ? `<div class="etapa__media"><img src="${etapa.media}" alt="${etapa.titulo}" loading="lazy"></div>` : ''}
      </div>
    </article>
  `).join('');
}

function renderizarCertificado(pasaporte) {
  const certificado = pasaporte.certificado;
  const contenedor = document.querySelector('[data-componente="certificado"]');
  if (!contenedor) return;

  if (!certificado) {
    contenedor.innerHTML = '<p class="estado estado--alerta">El certificado de esta pieza está en proceso de emisión. Esta sección se actualizará automáticamente cuando esté disponible.</p>';
    return;
  }

  setTexto('[data-campo="numero-certificado"]', certificado.numeroCertificado);
  setTexto('[data-campo="hash-certificado"]', certificado.hashSha256);
  setTexto('[data-campo="fecha-emision"]', certificado.fecha);

  const enlacePdf = document.querySelector('[data-campo="descargar-pdf"]');
  if (enlacePdf) enlacePdf.href = certificado.urlPdf || '#';
}

function renderizarGarantia(garantia) {
  const contenedor = document.querySelector('[data-componente="garantia"]');
  if (!contenedor) return;
  if (!garantia) {
    contenedor.innerHTML = '<p>La garantía se activa una vez confirmada la compra de la pieza.</p>';
    return;
  }
  setTexto('[data-campo="garantia-compra"]', formatearFecha(garantia.fechaCompra));
  setTexto('[data-campo="garantia-cobertura"]', garantia.cobertura);
  setTexto('[data-campo="garantia-vigencia"]', garantia.vigencia);
  const estadoEl = document.querySelector('[data-campo="garantia-estado"]');
  if (estadoEl) {
    estadoEl.textContent = garantia.estado === 'vigente' ? 'Vigente' : 'Vencida';
    estadoEl.className = `estado ${garantia.estado === 'vigente' ? 'estado--exito' : 'estado--alerta'}`;
  }
}

/* -------------------------------------------------------------------------
   UTILIDADES COMPARTIDAS
   ------------------------------------------------------------------------- */
function setTexto(selector, valor) {
  const el = document.querySelector(selector);
  if (el && valor !== undefined && valor !== null) el.textContent = valor;
}

function formatearFecha(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' });
}
