/**
 * TERRAE — admin-api.js (Fase 4 — Centro de Operaciones Terrae)
 * -----------------------------------------------------------------------
 * Capa de servicios del Back Office. Hoy persiste en localStorage (el
 * navegador hace de "base de datos" para la demo); cuando exista FastAPI
 * real, cada método de AdminAPI se reemplaza por un fetch() equivalente
 * sin tocar ningún módulo que lo consuma — ver docs/GUIA-INTEGRACION-API.md,
 * sección "Back Office".
 *
 * Todas las mutaciones registran automáticamente un evento de auditoría
 * (usuario, acción, fecha/hora, cambios) — ver AdminAPI.auditoria.
 * -----------------------------------------------------------------------
 */

const AdminAPI = (() => {
  const CLAVE_STORE = 'terrae_backoffice_v1';

  const usuarioSesionSimulado = { id: 'u-admin-1', nombre: 'Camila Torres', email: 'camila@terrae.com', rol: 'ADMIN' };

  /* -----------------------------------------------------------------------
     PERSISTENCIA
     ----------------------------------------------------------------------- */
  function leerStore() {
    try {
      const crudo = localStorage.getItem(CLAVE_STORE);
      return crudo ? JSON.parse(crudo) : null;
    } catch {
      return null;
    }
  }

  function guardarStore(store) {
    try {
      localStorage.setItem(CLAVE_STORE, JSON.stringify(store));
    } catch (error) {
      console.error('[AdminAPI] No fue posible persistir el store', error);
    }
  }

  function idUnico(prefijo) {
    return `${prefijo}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
  }

  function ahoraISO() {
    return new Date().toISOString();
  }

  /* -----------------------------------------------------------------------
     SEED — datos de ejemplo, solo se cargan la primera vez
     ----------------------------------------------------------------------- */
  function construirSeed() {
    const esmeraldaAlmaDeMuzo = {
      id: idUnico('esm'),
      codigoInterno: 'ESM-2026-0142',
      mina: 'La Pita',
      municipio: 'Muzo',
      departamento: 'Boyacá',
      pais: 'Colombia',
      pesoQuilates: 1.12,
      color: 'Verde intenso vívido',
      claridad: 'VS (ligeras inclusiones)',
      corte: 'Esmeralda (rectangular escalonado)',
      tratamientos: 'Aceite de cedro (menor)',
      inclusiones: 'Trifásica (líquido salino, CO₂, halita)',
      fotosMicroscopicas: ['assets/img/placeholder-microscopia-1.jpg'],
      estado: 'certificada',
      informeSiegemId: null,
    };

    const joyaAlmaDeMuzo = {
      id: 'TR-2026-00842',
      coleccion: 'Raíces',
      nombre: 'Alma de Muzo',
      descripcion: 'Anillo en plata 925 con esmeralda colombiana de Muzo, corte esmeralda.',
      tipoJoya: 'Anillo',
      metal: 'Plata 925',
      pesoGramos: 6.4,
      dimensiones: '18mm de diámetro interior',
      esmeraldaId: esmeraldaAlmaDeMuzo.id,
      estado: 'disponible', // disponible | vendida | reservada | desactivada | archivada
      precio: 8900000,
      moneda: 'COP',
      fotografias: ['assets/img/placeholder-pieza-1.jpg', 'assets/img/placeholder-detalle-1.jpg'],
      videos: [],
      observaciones: 'Pieza insignia de la colección Raíces.',
      certificadoId: null,
      qrId: null,
      blockchainId: null,
      creadoEn: ahoraISO(),
      actualizadoEn: ahoraISO(),
    };

    return {
      joyas: [joyaAlmaDeMuzo],
      esmeraldas: [esmeraldaAlmaDeMuzo],
      certificados: [],
      qrs: [],
      blockchainRegistros: [],
      propietarios: [],
      garantias: [],
      mantenimientos: [],
      usuarios: [
        { id: 'u-admin-1', nombre: 'Camila Torres', email: 'camila@terrae.com', rol: 'ADMIN', activo: true },
        { id: 'u-gem-1', nombre: 'Andrés Peña', email: 'andres@terrae.com', rol: 'GEMOLOGO', activo: true },
        { id: 'u-op-1', nombre: 'Laura Gómez', email: 'laura@terrae.com', rol: 'OPERADOR', activo: true },
        { id: 'u-aud-1', nombre: 'Julián Ríos', email: 'julian@terrae.com', rol: 'AUDITOR', activo: true },
      ],
      auditoria: [],
      configuracion: {
        numeracion: { prefijo: 'TR', formato: '{prefijo}-{anio}-{secuencial:5}', secuencialActual: 843 },
        certificados: { plantilla: 'clasica-verde', idiomasHabilitados: ['es', 'en'] },
        qr: { formato: ['png', 'svg'], resolucionAlta: true },
        blockchain: { redPredeterminada: 'Polygon', habilitado: false },
        idiomas: ['es', 'en'],
        monedas: ['COP', 'USD'],
        impuestos: { ivaPorcentaje: 19 },
      },
    };
  }

  function obtenerStore() {
    let store = leerStore();
    if (!store) {
      store = construirSeed();
      guardarStore(store);
    }
    return store;
  }

  function registrarAuditoria(store, accion, entidad, entidadId, cambios = {}) {
    store.auditoria.unshift({
      id: idUnico('aud'),
      usuario: usuarioSesionSimulado.nombre,
      usuarioId: usuarioSesionSimulado.id,
      accion,
      entidad,
      entidadId,
      cambios,
      fecha: ahoraISO(),
      ip: '—', // Solo disponible cuando exista backend real (ver docs)
    });
  }

  function simularLatencia(resultado, ms = 220) {
    return new Promise((resolve) => setTimeout(() => resolve(resultado), ms));
  }

  /* -----------------------------------------------------------------------
     GENERACIÓN AUTOMÁTICA DE ID (módulo 4 del prompt)
     ----------------------------------------------------------------------- */
  function generarIdJoya(store) {
    const config = store.configuracion.numeracion;
    const anio = new Date().getFullYear();
    let intento = config.secuencialActual + 1;
    let candidato;
    do {
      candidato = config.formato
        .replace('{prefijo}', config.prefijo)
        .replace('{anio}', anio)
        .replace(/\{secuencial:(\d+)\}/, (_, digitos) => String(intento).padStart(Number(digitos), '0'));
      intento += 1;
    } while (store.joyas.some((j) => j.id === candidato)); // garantiza no-duplicados
    config.secuencialActual = intento - 1;
    return candidato;
  }

  /* -----------------------------------------------------------------------
     GENERADORES AUTOMÁTICOS: QR y Certificado (simulados client-side;
     ver docs/GUIA-INTEGRACION-API.md para el reemplazo real con
     backend + qrcode + ReportLab)
     ----------------------------------------------------------------------- */
  function generarQRSimulado(joyaId) {
    const urlPublica = `${window.location.origin}${window.location.pathname.replace('admin.html', '')}pieza.html?id=${encodeURIComponent(joyaId)}`;
    return {
      id: idUnico('qr'),
      joyaId,
      urlPublica,
      urlPng: 'assets/icons/qr-placeholder.svg',
      urlSvg: 'assets/icons/qr-placeholder.svg',
      urlAltaResolucion: 'assets/icons/qr-placeholder.svg',
      creadoEn: ahoraISO(),
    };
  }

  function hashSimulado(semilla) {
    let h = 0;
    const texto = JSON.stringify(semilla);
    for (let i = 0; i < texto.length; i += 1) {
      h = (Math.imul(31, h) + texto.charCodeAt(i)) | 0;
    }
    return `sha256-sim-${Math.abs(h).toString(16).padStart(12, '0')}${Math.abs(h * 7).toString(16).padStart(12, '0')}`;
  }

  function generarCertificadoSimulado(joya, esmeralda, numeroSecuencial) {
    return {
      id: idUnico('cert'),
      joyaId: joya.id,
      numeroCertificado: `TRR-CERT-${new Date().getFullYear()}-${String(numeroSecuencial).padStart(6, '0')}`,
      hashSha256: hashSimulado({ joyaId: joya.id, esmeralda }),
      firmaDigital: 'Terrae Gemological Board',
      idioma: 'es',
      estado: 'EN_PROCESO',
      urlPdf: null, // Se completa cuando exista el generador ReportLab real
      emitidoEn: ahoraISO(),
    };
  }

  /* -----------------------------------------------------------------------
     API PÚBLICA — organizada por entidad
     ----------------------------------------------------------------------- */
  return {
    usuarioSesion: usuarioSesionSimulado,

    // ---------------- JOYAS ----------------
    joyas: {
      async listar({ busqueda = '', estado = '', coleccion = '' } = {}) {
        const store = obtenerStore();
        let resultado = [...store.joyas];
        if (busqueda) {
          const q = busqueda.toLowerCase();
          resultado = resultado.filter((j) => j.id.toLowerCase().includes(q) || j.nombre.toLowerCase().includes(q));
        }
        if (estado) resultado = resultado.filter((j) => j.estado === estado);
        if (coleccion) resultado = resultado.filter((j) => j.coleccion === coleccion);
        return simularLatencia(resultado);
      },
      async obtener(id) {
        const store = obtenerStore();
        return simularLatencia(store.joyas.find((j) => j.id === id) || null);
      },
      async crear(datos) {
        const store = obtenerStore();
        const id = generarIdJoya(store);
        const joya = {
          id,
          estado: 'disponible',
          fotografias: [],
          videos: [],
          certificadoId: null,
          qrId: null,
          blockchainId: null,
          creadoEn: ahoraISO(),
          actualizadoEn: ahoraISO(),
          ...datos,
        };
        store.joyas.push(joya);

        // Generación automática de QR al guardar (módulo 5 del prompt)
        const qr = generarQRSimulado(joya.id);
        store.qrs.push(qr);
        joya.qrId = qr.id;

        registrarAuditoria(store, 'CREAR', 'Joya', id, { nombre: joya.nombre });
        guardarStore(store);
        return simularLatencia(joya);
      },
      async actualizar(id, cambios) {
        const store = obtenerStore();
        const joya = store.joyas.find((j) => j.id === id);
        if (!joya) throw new Error('Joya no encontrada.');
        Object.assign(joya, cambios, { actualizadoEn: ahoraISO() });
        registrarAuditoria(store, 'EDITAR', 'Joya', id, cambios);
        guardarStore(store);
        return simularLatencia(joya);
      },
      async cambiarEstado(id, nuevoEstado) {
        return this.actualizar(id, { estado: nuevoEstado });
      },
      async aprobarCertificado(id) {
        const store = obtenerStore();
        const joya = store.joyas.find((j) => j.id === id);
        if (!joya) throw new Error('Joya no encontrada.');
        const esmeralda = store.esmeraldas.find((e) => e.id === joya.esmeraldaId);

        const certificado = generarCertificadoSimulado(joya, esmeralda, store.certificados.length + 1);
        store.certificados.push(certificado);
        joya.certificadoId = certificado.id;
        joya.estado = 'disponible';

        registrarAuditoria(store, 'APROBAR_CERTIFICADO', 'Certificado', certificado.id, { joyaId: id });
        guardarStore(store);
        return simularLatencia({ joya, certificado });
      },
    },

    // ---------------- ESMERALDAS ----------------
    esmeraldas: {
      async listar() {
        const store = obtenerStore();
        return simularLatencia([...store.esmeraldas]);
      },
      async obtener(id) {
        const store = obtenerStore();
        return simularLatencia(store.esmeraldas.find((e) => e.id === id) || null);
      },
      async crear(datos) {
        const store = obtenerStore();
        const esmeralda = { id: idUnico('esm'), estado: 'pendiente', fotosMicroscopicas: [], informeSiegemId: null, ...datos };
        store.esmeraldas.push(esmeralda);
        registrarAuditoria(store, 'CREAR', 'Esmeralda', esmeralda.id, { codigoInterno: esmeralda.codigoInterno });
        guardarStore(store);
        return simularLatencia(esmeralda);
      },
      async actualizar(id, cambios) {
        const store = obtenerStore();
        const esmeralda = store.esmeraldas.find((e) => e.id === id);
        if (!esmeralda) throw new Error('Esmeralda no encontrada.');
        Object.assign(esmeralda, cambios);
        registrarAuditoria(store, 'EDITAR', 'Esmeralda', id, cambios);
        guardarStore(store);
        return simularLatencia(esmeralda);
      },
    },

    // ---------------- CERTIFICADOS / QR ----------------
    certificados: {
      async listar() {
        const store = obtenerStore();
        return simularLatencia([...store.certificados]);
      },
      async obtenerPorJoya(joyaId) {
        const store = obtenerStore();
        return simularLatencia(store.certificados.find((c) => c.joyaId === joyaId) || null);
      },
    },
    qr: {
      async obtenerPorJoya(joyaId) {
        const store = obtenerStore();
        return simularLatencia(store.qrs.find((q) => q.joyaId === joyaId) || null);
      },
    },

    // ---------------- BLOCKCHAIN (interfaz preparada, sin conexión real) ----------------
    blockchain: {
      async listar() {
        const store = obtenerStore();
        return simularLatencia([...store.blockchainRegistros]);
      },
      async obtenerPorJoya(joyaId) {
        const store = obtenerStore();
        return simularLatencia(store.blockchainRegistros.find((b) => b.joyaId === joyaId) || null);
      },
      async registrar(joyaId, datos) {
        const store = obtenerStore();
        const registro = {
          id: idUnico('bch'),
          joyaId,
          hash: datos.hash || '',
          wallet: datos.wallet || '',
          smartContract: datos.smartContract || '',
          bloque: datos.bloque || '',
          gas: datos.gas || '',
          estado: 'pendiente', // pendiente | verificado — nunca se marca verificado sin conexión real
          registradoEn: ahoraISO(),
        };
        store.blockchainRegistros.push(registro);
        const joya = store.joyas.find((j) => j.id === joyaId);
        if (joya) joya.blockchainId = registro.id;
        registrarAuditoria(store, 'REGISTRAR', 'Blockchain', registro.id, datos);
        guardarStore(store);
        return simularLatencia(registro);
      },
      async consultarEstado(joyaId) {
        // Simulado: en Fase 5+ esto llama al RPC real de Polygon.
        const store = obtenerStore();
        const registro = store.blockchainRegistros.find((b) => b.joyaId === joyaId);
        if (!registro) return simularLatencia({ estado: 'no-registrado' });
        return simularLatencia({ estado: registro.estado, ultimaConsulta: ahoraISO() });
      },
    },

    // ---------------- PROPIETARIOS ----------------
    propietarios: {
      async listarPorJoya(joyaId) {
        const store = obtenerStore();
        return simularLatencia(store.propietarios.filter((p) => p.joyaId === joyaId));
      },
      async registrar(joyaId, datos) {
        const store = obtenerStore();
        store.propietarios.forEach((p) => {
          if (p.joyaId === joyaId && !p.fechaFin) p.fechaFin = ahoraISO().slice(0, 10);
        });
        const propietario = {
          id: idUnico('prop'),
          joyaId,
          fechaInicio: ahoraISO().slice(0, 10),
          fechaFin: null,
          ...datos, // nombre, pais, ciudad, fechaCompra — protegido por rol en el backend real
        };
        store.propietarios.push(propietario);
        const joya = store.joyas.find((j) => j.id === joyaId);
        if (joya) joya.estado = 'vendida';
        registrarAuditoria(store, 'REGISTRAR', 'Propietario', propietario.id, { joyaId, tipo: datos.tipoAdquisicion });
        guardarStore(store);
        return simularLatencia(propietario);
      },
    },

    // ---------------- GARANTÍAS ----------------
    garantias: {
      async obtenerPorJoya(joyaId) {
        const store = obtenerStore();
        return simularLatencia(store.garantias.find((g) => g.joyaId === joyaId) || null);
      },
      async activar(joyaId, datos) {
        const store = obtenerStore();
        const garantia = {
          id: idUnico('gar'),
          joyaId,
          estado: 'activa',
          fechaActivacion: ahoraISO().slice(0, 10),
          fechaVencimiento: datos.fechaVencimiento,
          cobertura: datos.cobertura,
          observaciones: datos.observaciones || '',
        };
        store.garantias.push(garantia);
        registrarAuditoria(store, 'ACTIVAR', 'Garantia', garantia.id, { joyaId });
        guardarStore(store);
        return simularLatencia(garantia);
      },
      async renovar(garantiaId, nuevaFechaVencimiento) {
        const store = obtenerStore();
        const garantia = store.garantias.find((g) => g.id === garantiaId);
        if (!garantia) throw new Error('Garantía no encontrada.');
        garantia.fechaVencimiento = nuevaFechaVencimiento;
        garantia.estado = 'activa';
        registrarAuditoria(store, 'RENOVAR', 'Garantia', garantiaId, { nuevaFechaVencimiento });
        guardarStore(store);
        return simularLatencia(garantia);
      },
    },

    // ---------------- MANTENIMIENTOS ----------------
    mantenimientos: {
      async listarPorJoya(joyaId) {
        const store = obtenerStore();
        return simularLatencia(store.mantenimientos.filter((m) => m.joyaId === joyaId));
      },
      async listarTodos() {
        const store = obtenerStore();
        return simularLatencia([...store.mantenimientos]);
      },
      async registrar(joyaId, datos) {
        const store = obtenerStore();
        const registro = {
          id: idUnico('mant'),
          joyaId,
          fecha: ahoraISO().slice(0, 10),
          tipo: datos.tipo,
          tecnico: datos.tecnico,
          fotosAntes: datos.fotosAntes || [],
          fotosDespues: datos.fotosDespues || [],
          comentarios: datos.comentarios || '',
          documentos: datos.documentos || [],
        };
        store.mantenimientos.push(registro);
        registrarAuditoria(store, 'REGISTRAR', 'Mantenimiento', registro.id, { joyaId, tipo: datos.tipo });
        guardarStore(store);
        return simularLatencia(registro);
      },
    },

    // ---------------- USUARIOS Y ROLES ----------------
    usuarios: {
      async listar() {
        const store = obtenerStore();
        return simularLatencia([...store.usuarios]);
      },
      async crear(datos) {
        const store = obtenerStore();
        const usuario = { id: idUnico('u'), activo: true, ...datos };
        store.usuarios.push(usuario);
        registrarAuditoria(store, 'CREAR', 'Usuario', usuario.id, { email: usuario.email, rol: usuario.rol });
        guardarStore(store);
        return simularLatencia(usuario);
      },
      async actualizarRol(id, rol) {
        const store = obtenerStore();
        const usuario = store.usuarios.find((u) => u.id === id);
        if (!usuario) throw new Error('Usuario no encontrado.');
        const rolAnterior = usuario.rol;
        usuario.rol = rol;
        registrarAuditoria(store, 'CAMBIAR_ROL', 'Usuario', id, { de: rolAnterior, a: rol });
        guardarStore(store);
        return simularLatencia(usuario);
      },
      async alternarActivo(id) {
        const store = obtenerStore();
        const usuario = store.usuarios.find((u) => u.id === id);
        if (!usuario) throw new Error('Usuario no encontrado.');
        usuario.activo = !usuario.activo;
        registrarAuditoria(store, usuario.activo ? 'ACTIVAR' : 'DESACTIVAR', 'Usuario', id, {});
        guardarStore(store);
        return simularLatencia(usuario);
      },
    },

    // ---------------- AUDITORÍA ----------------
    auditoria: {
      async listar({ limite = 100 } = {}) {
        const store = obtenerStore();
        return simularLatencia(store.auditoria.slice(0, limite));
      },
    },

    // ---------------- CONFIGURACIÓN ----------------
    configuracion: {
      async obtener() {
        const store = obtenerStore();
        return simularLatencia(store.configuracion);
      },
      async actualizar(seccion, valores) {
        const store = obtenerStore();
        store.configuracion[seccion] = { ...store.configuracion[seccion], ...valores };
        registrarAuditoria(store, 'ACTUALIZAR_CONFIGURACION', 'Configuracion', seccion, valores);
        guardarStore(store);
        return simularLatencia(store.configuracion);
      },
    },

    // ---------------- DASHBOARD ----------------
    dashboard: {
      async obtenerIndicadores() {
        const store = obtenerStore();
        const joyas = store.joyas;
        const valorInventario = joyas
          .filter((j) => j.estado === 'disponible')
          .reduce((total, j) => total + (j.precio || 0), 0);

        return simularLatencia({
          totalJoyas: joyas.length,
          joyasDisponibles: joyas.filter((j) => j.estado === 'disponible').length,
          joyasVendidas: joyas.filter((j) => j.estado === 'vendida').length,
          certificadosEmitidos: store.certificados.length,
          qrGenerados: store.qrs.length,
          registrosBlockchain: store.blockchainRegistros.length,
          garantiasActivas: store.garantias.filter((g) => g.estado === 'activa').length,
          mantenimientosRealizados: store.mantenimientos.length,
          pendientesCertificacion: joyas.filter((j) => !j.certificadoId).length,
          valorInventario,
          actividadReciente: store.auditoria.slice(0, 8),
        });
      },
    },

    // Utilidad expuesta para módulos que necesiten resetear la demo
    _resetearDemo() {
      localStorage.removeItem(CLAVE_STORE);
    },
  };
})();
