/**
 * TERRAE — app.js
 * -----------------------------------------------------------------------
 * Núcleo de la aplicación: configuración global, datos de ejemplo (mocks)
 * y comportamiento común a todas las páginas (navbar, scroll reveal,
 * modales, tabs, año del footer). Se carga en TODAS las páginas, antes
 * que los scripts específicos de cada vista.
 * -----------------------------------------------------------------------
 */

/* -------------------------------------------------------------------------
   CONFIGURACIÓN GLOBAL — único lugar que se toca al conectar el backend real
   ------------------------------------------------------------------------- */
window.TERRAE_CONFIG = {
  apiBaseUrl: 'https://api.terrae.com/api/v1', // Reemplazar por la URL real de FastAPI en Railway
  useMock: true,                                // false cuando el backend de Fase 1 esté desplegado
  nftHabilitado: false,                         // se activa en Fase 6 sin tocar el HTML
  blockchainExplorerUrl: 'https://polygonscan.com/tx/',
};

/* -------------------------------------------------------------------------
   DATOS DE EJEMPLO (MOCKS) — Fase 3: contrato de datos enriquecido del
   Pasaporte Digital Inteligente. Cada clave de PIEZAS_DEMO representa un
   "id" válido por la URL (?id=... o /pieza/{id}), incluyendo los estados
   excepcionales exigidos (descontinuada, vendida, certificado pendiente),
   para poder probar cada pantalla de estado sin backend.
   ------------------------------------------------------------------------- */
const PIEZAS_DEMO = {
  'TR-2026-00842': {
    id: 'TR-2026-00842',
    sku: 'TRR-AN-001',
    nombre: 'Alma de Muzo',
    coleccion: 'Raíces',
    tipoPieza: 'Anillo',
    metal: 'Plata 925',
    pesoGramos: 6.4,
    estado: 'activa', // activa | descontinuada | vendida | certificado_pendiente
    imagenPrincipal: 'assets/img/placeholder-pieza-1.jpg',
    esmeralda: {
      origenPredicho: 'Muzo',
      confianzaIA: 0.94,
      colorGrado: 'Verde intenso vívido',
      tratamiento: 'Aceite de cedro (menor)',
      quilates: 1.12,
    },
    certificado: {
      numeroCertificado: 'TRR-CERT-2026-000142',
      hashSha256: 'a1f4e9c2b7d3f6a08e1c4b5d9f2a7e3c6b1d8f4a9c2e7b5d1f3a6c9e2b7d4f1a',
      urlPdf: '#',
      estado: 'VERIFICADO',
      emitidoEn: '2026-05-12T10:30:00Z',
      fecha: '12 de mayo de 2026',
    },
    blockchainCliente: {
      registrado: true,
      integridadVerificada: true,
      fechaRegistro: '2026-05-12',
      red: 'Polygon',
    },
    blockchainTecnico: {
      wallet: '0x9F2a...C4e1',
      smartContract: '0x4B7d...A2f9',
      hash: 'a1f4e9c2b7d3f6a08e1c4b5d9f2a7e3c6b1d8f4a9c2e7b5d1f3a6c9e2b7d4f1a',
      token: '#000142',
      bloque: '58234110',
      gas: '0.0021 MATIC',
      transaccion: '0x4f2a8c1e9b7d3f6a08e1c4b5d9f2a7e3c6b1d8f4a9c2e7b5d1f3a6c9e2b7d4f1',
      ipfs: 'bafybeigdyrztt5o3s6demo000142',
    },
    galeria: [
      { tipo: 'foto', url: 'assets/img/placeholder-pieza-1.jpg' },
      { tipo: 'foto', url: 'assets/img/placeholder-detalle-1.jpg' },
      { tipo: 'foto', url: 'assets/img/placeholder-detalle-2.jpg' },
      { tipo: 'video', url: 'assets/video/placeholder-pieza.mp4' },
    ],
    modelo360Disponible: false,
    modelo3dDisponible: false,
    microscopia: {
      imagen: 'assets/img/placeholder-microscopia-1.jpg',
      inclusiones: [
        { x: '32%', y: '40%', tipo: 'Trifásica', descripcion: 'Inclusión trifásica: líquido salino, burbuja de CO₂ y cristal de halita.' },
        { x: '58%', y: '62%', tipo: 'Cristal huésped', descripcion: 'Micro-cristal de pirita asociado a la formación hidrotermal.' },
      ],
      descripcionTecnica: 'Patrón de inclusiones consistente con yacimientos de veta hidrotermal tipo Muzo.',
    },
    historia: [
      { titulo: 'Formación geológica', texto: 'Hace millones de años, fluidos hidrotermales cargados de berilio y cromo cristalizaron en las vetas de Muzo.', media: 'assets/img/placeholder-detalle-1.jpg' },
      { titulo: 'Región de origen', texto: 'Extraída de la veta occidental de Muzo, Boyacá — la región esmeraldera más reconocida del mundo.', media: null },
      { titulo: 'Extracción responsable', texto: 'Minería a pequeña escala, con trazabilidad documentada desde el primer día de extracción.', media: null },
      { titulo: 'Clasificación', texto: 'Analizada por el motor de IA de EmeraldChain: color, transparencia, inclusiones y origen.', media: null },
      { titulo: 'Selección', texto: 'Solo una fracción mínima de la producción alcanza el estándar gemológico Terrae.', media: null },
      { titulo: 'Diseño', texto: 'Boceto y modelado en plata 925, respetando la forma natural de la gema.', media: 'assets/img/placeholder-detalle-2.jpg' },
      { titulo: 'Fabricación artesanal', texto: 'Engastada a mano por maestros joyeros colombianos en el taller de Cali.', media: null },
      { titulo: 'Control de calidad', texto: 'Verificación gemológica final y aprobación por auditor certificado COPNIA.', media: null },
      { titulo: 'Entrega', texto: 'Pieza certificada, anclada en blockchain y lista para su Pasaporte Digital.', media: null },
    ],
    timeline: [
      { tipo: 'certificacion', fecha: '2026-05-12', lugar: 'Cali, Colombia', responsable: 'Terrae Gemological Board', hash: 'a1f4e9c2b7d3…e2b7d4f1a', estado: 'completado', titulo: 'Certificado emitido', detalle: 'Aprobado por auditor gemológico COPNIA.', media: null },
      { tipo: 'blockchain', fecha: '2026-05-12', lugar: 'Red Polygon', responsable: 'Sistema Terrae', hash: '0x4f2a8c1e9b7d…b7d4f1', estado: 'completado', titulo: 'Anclado en blockchain', detalle: 'Registro verificado en Polygon Mainnet.', media: null },
      { tipo: 'propietario', fecha: '2026-05-20', lugar: 'Bogotá, Colombia', responsable: 'Boutique Terrae', hash: null, estado: 'completado', titulo: 'Cambio de propietario', detalle: 'Compra registrada en tienda Bogotá.', media: null },
      { tipo: 'mantenimiento', fecha: '2026-11-03', lugar: 'Taller Terrae, Cali', responsable: 'Técnico J. Ramírez', hash: null, estado: 'completado', titulo: 'Limpieza profesional', detalle: 'Servicio realizado en taller autorizado Terrae.', media: null },
    ],
    garantia: { fechaCompra: '2026-05-20', cobertura: 'Reparación y ajuste', vigencia: '3 años', estado: 'vigente', fechaFin: '2029-05-20' },
    propietario: { registradoPublicamente: false },
    nft: null, // null = esta pieza no tiene NFT; la sección permanece oculta
  },

  'TR-2026-00910-descontinuada': {
    id: 'TR-2026-00910-descontinuada',
    nombre: 'Vestigio',
    estado: 'descontinuada',
  },

  'TR-2026-00777-vendida': {
    id: 'TR-2026-00777-vendida',
    nombre: 'Umbral',
    estado: 'vendida',
  },

  'TR-2026-01055-pendiente': {
    id: 'TR-2026-01055-pendiente',
    sku: 'TRR-CO-030',
    nombre: 'Semilla',
    coleccion: 'Raíces',
    tipoPieza: 'Collar',
    metal: 'Plata 925',
    pesoGramos: 9.1,
    estado: 'certificado_pendiente',
    imagenPrincipal: 'assets/img/placeholder-pieza-2.jpg',
    esmeralda: { origenPredicho: 'Chivor (preliminar)', confianzaIA: 0.81, colorGrado: 'Por confirmar', tratamiento: 'Por confirmar', quilates: 0.95 },
    certificado: null,
    blockchainCliente: null,
    blockchainTecnico: null,
    galeria: [{ tipo: 'foto', url: 'assets/img/placeholder-pieza-2.jpg' }],
    microscopia: null,
    historia: [],
    timeline: [
      { tipo: 'certificacion', fecha: '2026-06-01', lugar: 'Cali, Colombia', responsable: 'EmeraldChain Core', hash: null, estado: 'en-proceso', titulo: 'En análisis gemológico', detalle: 'Pendiente de validación por auditor.', media: null },
    ],
    garantia: null,
    propietario: { registradoPublicamente: false },
    nft: null,
  },
};

const TerraeMocks = {
  catalogo: [
    { sku: 'TRR-AN-001', nombre: 'Alma de Muzo', tipo: 'Anillo', precio: 8900000, imagen: 'assets/img/placeholder-pieza-1.jpg', id: 'TR-2026-00842' },
    { sku: 'TRR-CO-014', nombre: 'Vertiente', tipo: 'Collar', precio: 15400000, imagen: 'assets/img/placeholder-pieza-2.jpg', id: 'TR-2026-00842' },
    { sku: 'TRR-AR-007', nombre: 'Trifásica', tipo: 'Aretes', precio: 6200000, imagen: 'assets/img/placeholder-pieza-3.jpg', id: 'TR-2026-00842' },
  ],

  pasaporte(id) {
    const pieza = PIEZAS_DEMO[id];
    if (!pieza) {
      const error = new Error('Pieza no encontrada');
      error.status = 404;
      throw error;
    }
    return pieza;
  },

  estadoBlockchain(id) {
    const pieza = PIEZAS_DEMO[id];
    if (!pieza || !pieza.blockchainCliente) return { registrado: false };
    return pieza.blockchainCliente;
  },

  detalleTecnicoBlockchain(id) {
    const pieza = PIEZAS_DEMO[id];
    return (pieza && pieza.blockchainTecnico) || null;
  },

  historialMantenimiento(id) {
    return [
      { fecha: '2026-11-03', servicio: 'Limpieza profesional', tecnico: 'J. Ramírez', observaciones: 'Sin novedades. Engaste firme.', documento: '#' },
    ];
  },

  login(email) {
    return { access_token: 'demo.jwt.token', usuario: { email, rol: 'OPERADOR' } };
  },

  joyaCreada(datos) {
    return { id: 'demo-id', ...datos, estado: 'PENDIENTE_CERTIFICACION' };
  },

  certificadoAprobado(joyaId) {
    return { id: 'demo-cert-id', joyaId, estado: 'EN_PROCESO' };
  },

  propietarioRegistrado(joyaId, datos) {
    return { id: 'demo-prop-id', joyaId, ...datos };
  },

  mantenimientoRegistrado(joyaId, datos) {
    return { id: 'demo-mant-id', joyaId, ...datos };
  },
};

/* -------------------------------------------------------------------------
   INICIALIZACIÓN COMÚN
   ------------------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
  inicializarNavbar();
  inicializarScrollReveal();
  inicializarModales();
  inicializarTabs();
  inicializarAnioFooter();
});

/** Navbar: fondo sólido al hacer scroll + menú hamburguesa en mobile */
function inicializarNavbar() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  const alScrollear = () => {
    navbar.classList.toggle('navbar--solida', window.scrollY > 40);
  };
  alScrollear();
  window.addEventListener('scroll', alScrollear, { passive: true });

  const toggle = navbar.querySelector('.navbar__menu-toggle');
  const links = navbar.querySelector('.navbar__links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      const abierto = links.classList.toggle('esta-abierto');
      toggle.setAttribute('aria-expanded', String(abierto));
    });
  }
}

/** Scroll Reveal — IntersectionObserver, respeta prefers-reduced-motion */
function inicializarScrollReveal() {
  const elementos = document.querySelectorAll('.revelar');
  if (!elementos.length) return;

  const prefiereMenosMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefiereMenosMovimiento) {
    elementos.forEach((el) => el.classList.add('esta-visible'));
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

  elementos.forEach((el) => observador.observe(el));
}

/** Modales genéricos: [data-modal-abrir="id"] / [data-modal-cerrar] */
function inicializarModales() {
  document.querySelectorAll('[data-modal-abrir]').forEach((boton) => {
    boton.addEventListener('click', () => {
      const modal = document.getElementById(boton.dataset.modalAbrir);
      if (modal) abrirModal(modal);
    });
  });

  document.querySelectorAll('.modal-overlay').forEach((overlay) => {
    overlay.addEventListener('click', (evento) => {
      if (evento.target === overlay) cerrarModal(overlay);
    });
    overlay.querySelectorAll('[data-modal-cerrar]').forEach((boton) => {
      boton.addEventListener('click', () => cerrarModal(overlay));
    });
  });

  document.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.esta-abierto').forEach(cerrarModal);
    }
  });
}

function abrirModal(overlay) {
  overlay.classList.add('esta-abierto');
  overlay.setAttribute('aria-hidden', 'false');
  const primerFocable = overlay.querySelector('button, a, input, select, textarea');
  if (primerFocable) primerFocable.focus();
}

function cerrarModal(overlay) {
  overlay.classList.remove('esta-abierto');
  overlay.setAttribute('aria-hidden', 'true');
}

/** Tabs accesibles (ARIA tablist/tab/tabpanel) */
function inicializarTabs() {
  document.querySelectorAll('.tabs').forEach((grupo) => {
    const botones = Array.from(grupo.querySelectorAll('.tabs__boton'));
    botones.forEach((boton) => {
      boton.addEventListener('click', () => activarTab(grupo, boton));
      boton.addEventListener('keydown', (evento) => {
        const indice = botones.indexOf(boton);
        if (evento.key === 'ArrowRight') botones[(indice + 1) % botones.length].focus();
        if (evento.key === 'ArrowLeft') botones[(indice - 1 + botones.length) % botones.length].focus();
      });
    });
  });
}

function activarTab(grupo, botonActivo) {
  const contenedorPaneles = grupo.parentElement;
  grupo.querySelectorAll('.tabs__boton').forEach((boton) => {
    boton.setAttribute('aria-selected', String(boton === botonActivo));
  });
  contenedorPaneles.querySelectorAll('.tabs__panel').forEach((panel) => {
    panel.hidden = panel.id !== botonActivo.getAttribute('aria-controls');
  });
}

function inicializarAnioFooter() {
  const el = document.querySelector('[data-anio-actual]');
  if (el) el.textContent = new Date().getFullYear();
}

/** Utilidad compartida de formato de moneda COP */
function formatearCOP(valor) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor);
}
