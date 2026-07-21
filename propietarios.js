/**
 * TERRAE — admin-modules/joyas.js
 * -----------------------------------------------------------------------
 * Módulo 2: Gestión de Joyas. CRUD completo (crear, editar, consultar,
 * desactivar, archivar) con todos los campos mínimos del prompt. Al
 * crear, AdminAPI genera automáticamente el ID único y el QR (módulos
 * 4 y 5). El botón "Aprobar certificado" dispara la generación del
 * certificado simulado (módulo 6).
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('joyas', {
  async montar(contenedor) {
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Gestión de Joyas</h1>
            <p class="bo-vista__subtitulo">Ciclo de vida completo de cada pieza Terrae.</p>
          </div>
          <button class="boton boton--esmeralda" data-accion="nueva-joya" type="button">Registrar nueva pieza</button>
        </div>
        <div class="bo-toolbar">
          <div class="bo-toolbar__filtros">
            <input type="search" data-filtro="busqueda" placeholder="Buscar por ID o nombre…">
            <select data-filtro="estado">
              <option value="">Todos los estados</option>
              <option value="disponible">Disponible</option>
              <option value="vendida">Vendida</option>
              <option value="reservada">Reservada</option>
              <option value="desactivada">Desactivada</option>
              <option value="archivada">Archivada</option>
            </select>
          </div>
        </div>
        <div id="joyas-tabla"></div>
      </section>`;

    contenedor.querySelector('[data-accion="nueva-joya"]').addEventListener('click', () => abrirDrawerJoya());
    contenedor.querySelector('[data-filtro="busqueda"]').addEventListener('input', debounce(recargarTabla, 250));
    contenedor.querySelector('[data-filtro="estado"]').addEventListener('change', recargarTabla);

    await recargarTabla();
  },
});

async function recargarTabla() {
  const contenedor = document.getElementById('joyas-tabla');
  if (!contenedor) return;
  const busqueda = document.querySelector('[data-filtro="busqueda"]')?.value || '';
  const estado = document.querySelector('[data-filtro="estado"]')?.value || '';
  const joyas = await AdminAPI.joyas.listar({ busqueda, estado });

  BO.renderizarTabla(contenedor, {
    filaVacia: 'No hay piezas registradas con estos filtros.',
    columnas: [
      { clave: 'id', titulo: 'ID', ordenable: true, render: (j) => `<span class="dato-tecnico">${BO.escapeHtml(j.id)}</span>` },
      { clave: 'nombre', titulo: 'Pieza', ordenable: true },
      { clave: 'coleccion', titulo: 'Colección', ordenable: true },
      { clave: 'estado', titulo: 'Estado', render: (j) => badgeEstadoJoya(j.estado) },
      { clave: 'precio', titulo: 'Precio', ordenable: true, render: (j) => BO.formatearMoneda(j.precio, j.moneda) },
      {
        clave: 'certificadoId', titulo: 'Certificado',
        render: (j) => (j.certificadoId ? '<span class="estado estado--exito">Emitido</span>' : '<span class="estado estado--alerta">Pendiente</span>'),
      },
      {
        clave: 'acciones', titulo: '', render: (j) => `
        <div class="bo-tabla__acciones">
          <button class="bo-tabla__icono-boton" data-accion="ver" data-id="${j.id}" title="Ver detalle" type="button">👁</button>
          <button class="bo-tabla__icono-boton" data-accion="editar" data-id="${j.id}" title="Editar" type="button">✎</button>
          ${!j.certificadoId ? `<button class="bo-tabla__icono-boton" data-accion="aprobar" data-id="${j.id}" title="Aprobar certificado" type="button">✓</button>` : ''}
          ${j.estado !== 'archivada' ? `<button class="bo-tabla__icono-boton" data-accion="archivar" data-id="${j.id}" title="Archivar" type="button">🗄</button>` : ''}
        </div>`,
      },
    ],
    filas: joyas,
  });

  contenedor.querySelectorAll('[data-accion="ver"]').forEach((b) => b.addEventListener('click', () => abrirDrawerJoya(b.dataset.id, true)));
  contenedor.querySelectorAll('[data-accion="editar"]').forEach((b) => b.addEventListener('click', () => abrirDrawerJoya(b.dataset.id, false)));
  contenedor.querySelectorAll('[data-accion="aprobar"]').forEach((b) => b.addEventListener('click', () => aprobarCertificado(b.dataset.id)));
  contenedor.querySelectorAll('[data-accion="archivar"]').forEach((b) => b.addEventListener('click', () => archivarJoya(b.dataset.id)));
}

function badgeEstadoJoya(estado) {
  const mapa = {
    disponible: 'estado--exito', vendida: 'estado--alerta', reservada: 'estado--alerta',
    desactivada: 'estado--error', archivada: 'estado--error',
  };
  return `<span class="estado ${mapa[estado] || ''}">${BO.escapeHtml(estado)}</span>`;
}

async function abrirDrawerJoya(id = null, soloLectura = false) {
  const [joya, esmeraldas] = await Promise.all([
    id ? AdminAPI.joyas.obtener(id) : Promise.resolve(null),
    AdminAPI.esmeraldas.listar(),
  ]);

  const opcionesEsmeralda = esmeraldas
    .map((e) => `<option value="${e.id}" ${joya?.esmeraldaId === e.id ? 'selected' : ''}>${BO.escapeHtml(e.codigoInterno)} — ${BO.escapeHtml(e.mina)}</option>`)
    .join('');

  const v = (campo, porDefecto = '') => BO.escapeHtml(joya ? joya[campo] ?? porDefecto : porDefecto);
  const soloLecturaAttr = soloLectura ? 'disabled' : '';

  const cuerpoHTML = `
    <div class="bo-form-grid">
      <div class="campo campo--ancho-completo">
        <label class="campo__label" for="jf-nombre">Nombre de la pieza</label>
        <input class="campo__input" id="jf-nombre" name="nombre" value="${v('nombre')}" ${soloLecturaAttr} required>
      </div>
      <div class="campo">
        <label class="campo__label" for="jf-coleccion">Colección</label>
        <input class="campo__input" id="jf-coleccion" name="coleccion" value="${v('coleccion')}" ${soloLecturaAttr} required>
      </div>
      <div class="campo">
        <label class="campo__label" for="jf-tipo">Tipo de joya</label>
        <select class="campo__select" id="jf-tipo" name="tipoJoya" ${soloLecturaAttr}>
          ${['Anillo', 'Collar', 'Aretes', 'Pulsera'].map((t) => `<option ${joya?.tipoJoya === t ? 'selected' : ''}>${t}</option>`).join('')}
        </select>
      </div>
      <div class="campo">
        <label class="campo__label" for="jf-metal">Metal</label>
        <input class="campo__input" id="jf-metal" name="metal" value="${v('metal', 'Plata 925')}" ${soloLecturaAttr}>
      </div>
      <div class="campo">
        <label class="campo__label" for="jf-peso">Peso (gramos)</label>
        <input class="campo__input" id="jf-peso" name="pesoGramos" type="number" step="0.1" value="${v('pesoGramos')}" ${soloLecturaAttr} required>
      </div>
      <div class="campo">
        <label class="campo__label" for="jf-dimensiones">Dimensiones</label>
        <input class="campo__input" id="jf-dimensiones" name="dimensiones" value="${v('dimensiones')}" ${soloLecturaAttr}>
      </div>
      <div class="campo campo--ancho-completo">
        <label class="campo__label" for="jf-esmeralda">Esmeralda asociada</label>
        <select class="campo__select" id="jf-esmeralda" name="esmeraldaId" ${soloLecturaAttr}>
          <option value="">— Sin asociar —</option>
          ${opcionesEsmeralda}
        </select>
      </div>
      <div class="campo">
        <label class="campo__label" for="jf-precio">Precio</label>
        <input class="campo__input" id="jf-precio" name="precio" type="number" step="1000" value="${v('precio')}" ${soloLecturaAttr} required>
      </div>
      <div class="campo">
        <label class="campo__label" for="jf-moneda">Moneda</label>
        <select class="campo__select" id="jf-moneda" name="moneda" ${soloLecturaAttr}>
          ${['COP', 'USD'].map((m) => `<option ${(joya?.moneda || 'COP') === m ? 'selected' : ''}>${m}</option>`).join('')}
        </select>
      </div>
      <div class="campo campo--ancho-completo">
        <label class="campo__label" for="jf-descripcion">Descripción</label>
        <textarea class="campo__textarea" id="jf-descripcion" name="descripcion" rows="3" ${soloLecturaAttr}>${v('descripcion')}</textarea>
      </div>
      <div class="campo campo--ancho-completo">
        <label class="campo__label" for="jf-observaciones">Observaciones</label>
        <textarea class="campo__textarea" id="jf-observaciones" name="observaciones" rows="2" ${soloLecturaAttr}>${v('observaciones')}</textarea>
      </div>
      <div class="campo campo--ancho-completo">
        <span class="campo__label">Fotografías y videos</span>
        <div id="jf-uploader"></div>
      </div>
      ${joya?.qrId ? '<div class="campo campo--ancho-completo" id="jf-qr"></div>' : ''}
    </div>`;

  const { formulario, cerrar } = BO.abrirDrawer({
    titulo: joya ? (soloLectura ? `Detalle · ${joya.id}` : `Editar · ${joya.id}`) : 'Registrar nueva pieza',
    cuerpoHTML,
    textoGuardar: soloLectura ? 'Cerrar' : 'Guardar',
    async alGuardar(datos) {
      if (soloLectura) return cerrar();

      const { esValido, errores } = BO.validarFormulario(datos, {
        nombre: [BO.validadores.requerido, BO.validadores.longitudMaxima(120)],
        coleccion: [BO.validadores.requerido],
        pesoGramos: [BO.validadores.requerido, BO.validadores.numeroPositivo],
        precio: [BO.validadores.requerido, BO.validadores.numeroPositivo],
      });
      if (!esValido) {
        BO.toast(Object.values(errores)[0], 'error');
        return;
      }

      const payload = {
        ...datos,
        pesoGramos: Number(datos.pesoGramos),
        precio: Number(datos.precio),
        esmeraldaId: datos.esmeraldaId || null,
      };

      if (joya) {
        await AdminAPI.joyas.actualizar(joya.id, payload);
        BO.toast('Pieza actualizada correctamente.');
      } else {
        const nueva = await AdminAPI.joyas.crear(payload);
        BO.toast(`Pieza registrada con ID ${nueva.id}. QR generado automáticamente.`);
      }
      cerrar();
      recargarTabla();
    },
  });

  if (!soloLectura) {
    BO.inicializarUploader(formulario.querySelector('#jf-uploader'), { maxMB: 25 });
  }

  if (joya?.qrId) {
    const qr = await AdminAPI.qr.obtenerPorJoya(joya.id);
    if (qr) {
      formulario.querySelector('#jf-qr').innerHTML = `
        <span class="campo__label">Código QR (generado automáticamente)</span>
        <div class="bo-visor-qr">
          <img src="${qr.urlPng}" alt="QR de la pieza ${BO.escapeHtml(joya.id)}">
          <span class="dato-tecnico" style="font-size:0.7rem;word-break:break-all;">${BO.escapeHtml(qr.urlPublica)}</span>
          <div class="bo-visor-qr__acciones">
            <a class="boton boton--secundario boton--pequeno" href="${qr.urlPng}" download>Descargar PNG</a>
            <a class="boton boton--secundario boton--pequeno" href="${qr.urlSvg}" download>Descargar SVG</a>
          </div>
        </div>`;
    }
  }
}

async function aprobarCertificado(id) {
  const confirmado = await BO.confirmar({
    titulo: 'Aprobar certificado',
    texto: `Se generará automáticamente el certificado digital para la pieza ${id}, incluyendo hash y firma.`,
    textoConfirmar: 'Aprobar y generar',
  });
  if (!confirmado) return;
  await AdminAPI.joyas.aprobarCertificado(id);
  BO.toast('Certificado generado y asociado a la pieza.');
  recargarTabla();
}

async function archivarJoya(id) {
  const confirmado = await BO.confirmar({
    titulo: 'Archivar pieza',
    texto: `La pieza ${id} dejará de aparecer en el catálogo activo. Esta acción se puede revertir editando su estado.`,
    textoConfirmar: 'Archivar',
    peligroso: true,
  });
  if (!confirmado) return;
  await AdminAPI.joyas.cambiarEstado(id, 'archivada');
  BO.toast('Pieza archivada.', 'alerta');
  recargarTabla();
}

function debounce(fn, ms) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), ms);
  };
}
