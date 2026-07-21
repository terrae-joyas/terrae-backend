/**
 * TERRAE — admin-app.js (Fase 4 — Centro de Operaciones Terrae)
 * -----------------------------------------------------------------------
 * Shell de la aplicación: registro de módulos, enrutamiento por hash
 * (#/joyas, #/esmeraldas...), sidebar, buscador global, y la librería de
 * componentes reutilizables que todos los módulos comparten (BO.*):
 * Toast, Drawer (formulario lateral), Confirm, DataTable, Uploader,
 * escapeHtml (protección XSS) y validadores comunes.
 * -----------------------------------------------------------------------
 */

const BO = (() => {
  const modulosRegistrados = {};
  let vistaActual = null;

  /* -----------------------------------------------------------------------
     REGISTRO Y ENRUTAMIENTO DE MÓDULOS
     ----------------------------------------------------------------------- */
  function registrarModulo(clave, definicion) {
    modulosRegistrados[clave] = definicion; // { montar(contenedor), desmontar?() }
  }

  function irA(clave) {
    window.location.hash = `#/${clave}`;
  }

  function resolverRutaActual() {
    const hash = window.location.hash.replace('#/', '') || 'dashboard';
    return modulosRegistrados[hash] ? hash : 'dashboard';
  }

  async function renderizarRuta() {
    const clave = resolverRutaActual();
    if (vistaActual && modulosRegistrados[vistaActual]?.desmontar) {
      modulosRegistrados[vistaActual].desmontar();
    }
    vistaActual = clave;

    document.querySelectorAll('.bo-nav__link').forEach((link) => {
      link.setAttribute('aria-current', String(link.dataset.modulo === clave));
    });

    const contenedor = document.getElementById('bo-contenido-vista');
    contenedor.setAttribute('aria-busy', 'true');
    try {
      await modulosRegistrados[clave].montar(contenedor);
    } catch (error) {
      contenedor.innerHTML = `<p role="alert">No fue posible cargar este módulo. ${escapeHtml(error.message || '')}</p>`;
      console.error('[BO]', error);
    } finally {
      contenedor.setAttribute('aria-busy', 'false');
    }
  }

  function inicializarRouter() {
    window.addEventListener('hashchange', renderizarRuta);
    renderizarRuta();
  }

  /* -----------------------------------------------------------------------
     SANITIZACIÓN — protección XSS obligatoria antes de insertar cualquier
     dato en innerHTML. Todo módulo debe pasar por aquí cualquier campo
     que provenga de un formulario o de AdminAPI antes de imprimirlo.
     ----------------------------------------------------------------------- */
  function escapeHtml(valor) {
    if (valor === null || valor === undefined) return '';
    return String(valor)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  /* -----------------------------------------------------------------------
     TOASTS
     ----------------------------------------------------------------------- */
  function toast(mensaje, tipo = 'exito') {
    const contenedor = document.getElementById('bo-toasts');
    const el = document.createElement('div');
    el.className = `bo-toast bo-toast--${tipo}`;
    el.setAttribute('role', 'status');
    el.textContent = mensaje;
    contenedor.appendChild(el);
    setTimeout(() => el.remove(), 4500);
  }

  /* -----------------------------------------------------------------------
     CONFIRM — reemplaza confirm() nativo con un modal de marca
     ----------------------------------------------------------------------- */
  function confirmar({ titulo, texto, textoConfirmar = 'Confirmar', peligroso = false }) {
    return new Promise((resolve) => {
      const overlay = document.getElementById('bo-confirm-overlay');
      overlay.innerHTML = `
        <div class="modal" role="alertdialog" aria-modal="true" aria-labelledby="bo-confirm-titulo">
          <h2 id="bo-confirm-titulo">${escapeHtml(titulo)}</h2>
          <p>${escapeHtml(texto)}</p>
          <div class="bo-confirm__acciones">
            <button class="boton boton--secundario" data-accion="cancelar" type="button">Cancelar</button>
            <button class="boton ${peligroso ? 'boton--secundario' : 'boton--esmeralda'}" data-accion="confirmar" type="button">${escapeHtml(textoConfirmar)}</button>
          </div>
        </div>`;
      overlay.classList.add('esta-abierto');

      const cerrar = (resultado) => {
        overlay.classList.remove('esta-abierto');
        overlay.innerHTML = '';
        resolve(resultado);
      };
      overlay.querySelector('[data-accion="cancelar"]').addEventListener('click', () => cerrar(false));
      overlay.querySelector('[data-accion="confirmar"]').addEventListener('click', () => cerrar(true));
    });
  }

  /* -----------------------------------------------------------------------
     DRAWER — panel lateral reutilizable para crear/editar registros
     ----------------------------------------------------------------------- */
  function abrirDrawer({ titulo, cuerpoHTML, alGuardar, textoGuardar = 'Guardar' }) {
    const overlay = document.getElementById('bo-drawer-overlay');
    overlay.innerHTML = `
      <div class="bo-drawer" role="dialog" aria-modal="true" aria-labelledby="bo-drawer-titulo">
        <div class="bo-drawer__cabecera">
          <h2 id="bo-drawer-titulo" style="margin:0;font-size:1.1rem;">${escapeHtml(titulo)}</h2>
          <button class="modal__cerrar" data-accion="cerrar-drawer" type="button" aria-label="Cerrar" style="position:static;">✕</button>
        </div>
        <div class="bo-drawer__cuerpo">
          <form id="bo-drawer-form">${cuerpoHTML}</form>
        </div>
        <div class="bo-drawer__pie">
          <button class="boton boton--secundario" data-accion="cerrar-drawer" type="button">Cancelar</button>
          <button class="boton boton--esmeralda" data-accion="guardar-drawer" type="submit" form="bo-drawer-form">${escapeHtml(textoGuardar)}</button>
        </div>
      </div>`;
    overlay.classList.add('esta-abierto');

    const cerrar = () => {
      overlay.classList.remove('esta-abierto');
      overlay.innerHTML = '';
    };
    overlay.querySelectorAll('[data-accion="cerrar-drawer"]').forEach((b) => b.addEventListener('click', cerrar));

    const formulario = overlay.querySelector('#bo-drawer-form');
    formulario.addEventListener('submit', async (evento) => {
      evento.preventDefault();
      const boton = overlay.querySelector('[data-accion="guardar-drawer"]');
      boton.disabled = true;
      const textoOriginal = boton.textContent;
      boton.textContent = 'Guardando…';
      try {
        const datos = Object.fromEntries(new FormData(formulario).entries());
        await alGuardar(datos, cerrar);
      } catch (error) {
        toast(error.message || 'Ocurrió un error al guardar.', 'error');
      } finally {
        boton.disabled = false;
        boton.textContent = textoOriginal;
      }
    });

    return { cerrar, formulario };
  }

  /* -----------------------------------------------------------------------
     DATATABLE — tabla con búsqueda/orden/paginación mínima reutilizable
     ----------------------------------------------------------------------- */
  function renderizarTabla(contenedor, { columnas, filas, filaVacia = 'Sin resultados', porPagina = 10 }) {
    let paginaActual = 1;
    let ordenColumna = null;
    let ordenAsc = true;

    function filasOrdenadas() {
      if (!ordenColumna) return filas;
      const copia = [...filas];
      copia.sort((a, b) => {
        const va = a[ordenColumna];
        const vb = b[ordenColumna];
        if (va === vb) return 0;
        return (va > vb ? 1 : -1) * (ordenAsc ? 1 : -1);
      });
      return copia;
    }

    function pintar() {
      const datos = filasOrdenadas();
      const totalPaginas = Math.max(1, Math.ceil(datos.length / porPagina));
      paginaActual = Math.min(paginaActual, totalPaginas);
      const inicio = (paginaActual - 1) * porPagina;
      const pagina = datos.slice(inicio, inicio + porPagina);

      const encabezados = columnas.map((col) => `
        <th data-clave="${col.clave}" ${col.ordenable ? `aria-sort="${ordenColumna === col.clave ? (ordenAsc ? 'ascending' : 'descending') : 'none'}"` : ''}>${escapeHtml(col.titulo)}</th>
      `).join('');

      const cuerpo = pagina.length
        ? pagina.map((fila) => `<tr>${columnas.map((col) => `<td>${col.render ? col.render(fila) : escapeHtml(fila[col.clave])}</td>`).join('')}</tr>`).join('')
        : `<tr><td colspan="${columnas.length}" class="bo-tabla__vacio">${escapeHtml(filaVacia)}</td></tr>`;

      contenedor.innerHTML = `
        <div class="bo-tabla-wrap">
          <table class="bo-tabla">
            <thead><tr>${encabezados}</tr></thead>
            <tbody>${cuerpo}</tbody>
          </table>
          <div class="bo-paginacion">
            <span>${datos.length} registro${datos.length === 1 ? '' : 's'}</span>
            <div class="bo-paginacion__botones">
              <button class="bo-tabla__icono-boton" data-pagina="anterior" ${paginaActual === 1 ? 'disabled' : ''} aria-label="Página anterior">‹</button>
              <span>${paginaActual} / ${totalPaginas}</span>
              <button class="bo-tabla__icono-boton" data-pagina="siguiente" ${paginaActual === totalPaginas ? 'disabled' : ''} aria-label="Página siguiente">›</button>
            </div>
          </div>
        </div>`;

      contenedor.querySelectorAll('th[data-clave]').forEach((th) => {
        const columna = columnas.find((c) => c.clave === th.dataset.clave);
        if (!columna?.ordenable) return;
        th.addEventListener('click', () => {
          if (ordenColumna === columna.clave) ordenAsc = !ordenAsc;
          else { ordenColumna = columna.clave; ordenAsc = true; }
          pintar();
        });
      });
      contenedor.querySelector('[data-pagina="anterior"]')?.addEventListener('click', () => { paginaActual -= 1; pintar(); });
      contenedor.querySelector('[data-pagina="siguiente"]')?.addEventListener('click', () => { paginaActual += 1; pintar(); });

      if (typeof renderizarTabla.alPintar === 'function') renderizarTabla.alPintar(contenedor, pagina);
    }

    pintar();
  }

  /* -----------------------------------------------------------------------
     VALIDADORES COMUNES (cliente) — módulo "Validaciones" del prompt
     ----------------------------------------------------------------------- */
  const validadores = {
    requerido: (valor) => (valor !== undefined && valor !== null && String(valor).trim() !== '') || 'Este campo es obligatorio.',
    numeroPositivo: (valor) => (Number(valor) > 0) || 'Debe ser un número mayor a cero.',
    longitudMaxima: (max) => (valor) => (String(valor || '').length <= max) || `Máximo ${max} caracteres.`,
    email: (valor) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor) || 'Correo electrónico inválido.',
    tipoArchivoPermitido: (archivo, tiposPermitidos) => tiposPermitidos.includes(archivo.type) || 'Tipo de archivo no permitido.',
    tamanoMaximoMB: (archivo, maxMB) => archivo.size <= maxMB * 1024 * 1024 || `El archivo supera los ${maxMB}MB permitidos.`,
    async sinDuplicado(valor, listaExistente, campo) {
      return !listaExistente.some((item) => item[campo] === valor) || 'Ya existe un registro con este valor.';
    },
  };

  function validarFormulario(datos, reglas) {
    const errores = {};
    Object.entries(reglas).forEach(([campo, listaValidadores]) => {
      for (const validar of listaValidadores) {
        const resultado = validar(datos[campo]);
        if (resultado !== true) {
          errores[campo] = resultado;
          break;
        }
      }
    });
    return { esValido: Object.keys(errores).length === 0, errores };
  }

  /* -----------------------------------------------------------------------
     UPLOADER — carga de archivos con validación de tipo/tamaño
     ----------------------------------------------------------------------- */
  function inicializarUploader(contenedor, { tiposPermitidos = ['image/jpeg', 'image/png', 'video/mp4'], maxMB = 20, onCambio } = {}) {
    const archivos = [];
    contenedor.innerHTML = `
      <label class="bo-uploader" tabindex="0">
        <input type="file" multiple accept="${tiposPermitidos.join(',')}">
        <span>Arrastra archivos aquí o haz clic para seleccionar</span>
        <span style="display:block;font-size:0.7rem;margin-top:4px;">Fotografías, video · máx. ${maxMB}MB por archivo</span>
      </label>
      <ul class="bo-uploader__lista"></ul>`;

    const input = contenedor.querySelector('input[type="file"]');
    const lista = contenedor.querySelector('.bo-uploader__lista');
    const label = contenedor.querySelector('.bo-uploader');

    function pintarLista() {
      lista.innerHTML = archivos.map((archivo, indice) => `
        <li><span>${escapeHtml(archivo.name)} (${(archivo.size / 1024).toFixed(0)} KB)</span><button type="button" class="bo-uploader__quitar" data-indice="${indice}">Quitar</button></li>
      `).join('');
      lista.querySelectorAll('.bo-uploader__quitar').forEach((boton) => {
        boton.addEventListener('click', () => {
          archivos.splice(Number(boton.dataset.indice), 1);
          pintarLista();
          onCambio?.(archivos);
        });
      });
    }

    function procesarArchivos(listaArchivos) {
      Array.from(listaArchivos).forEach((archivo) => {
        const validoTipo = validadores.tipoArchivoPermitido(archivo, tiposPermitidos);
        const validoTamano = validadores.tamanoMaximoMB(archivo, maxMB);
        if (validoTipo !== true) return toast(validoTipo, 'error');
        if (validoTamano !== true) return toast(validoTamano, 'error');
        archivos.push(archivo);
      });
      pintarLista();
      onCambio?.(archivos);
    }

    input.addEventListener('change', (evento) => procesarArchivos(evento.target.files));
    ['dragover', 'dragleave', 'drop'].forEach((evt) => {
      label.addEventListener(evt, (evento) => {
        evento.preventDefault();
        label.classList.toggle('esta-en-arrastre', evt === 'dragover');
      });
    });
    label.addEventListener('drop', (evento) => procesarArchivos(evento.dataTransfer.files));

    return { obtenerArchivos: () => archivos };
  }

  /* -----------------------------------------------------------------------
     FORMATO
     ----------------------------------------------------------------------- */
  function formatearMoneda(valor, moneda = 'COP') {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: moneda, maximumFractionDigits: 0 }).format(valor || 0);
  }
  function formatearFechaHora(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' });
  }

  return {
    registrarModulo,
    irA,
    inicializarRouter,
    escapeHtml,
    toast,
    confirmar,
    abrirDrawer,
    renderizarTabla,
    validadores,
    validarFormulario,
    inicializarUploader,
    formatearMoneda,
    formatearFechaHora,
  };
})();

/* ---------------------------------------------------------------------------
   INICIALIZACIÓN DEL SHELL
   ------------------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
  const raiz = document.querySelector('[data-pagina="backoffice"]');
  if (!raiz) return;

  const nombreEl = document.getElementById('bo-usuario-nombre');
  const rolEl = document.getElementById('bo-usuario-rol');
  if (nombreEl) nombreEl.textContent = AdminAPI.usuarioSesion.nombre;
  if (rolEl) rolEl.textContent = AdminAPI.usuarioSesion.rol.replace('_', ' ');

  document.querySelectorAll('.bo-nav__link').forEach((link) => {
    link.addEventListener('click', () => BO.irA(link.dataset.modulo));
  });

  const togglesSidebar = document.querySelectorAll('[data-accion="toggle-bo-sidebar"]');
  const sidebar = document.querySelector('.bo-sidebar');
  togglesSidebar.forEach((boton) => boton.addEventListener('click', () => sidebar.classList.toggle('esta-abierto')));

  const buscadorGlobal = document.querySelector('#bo-buscador-global-input');
  if (buscadorGlobal) {
    buscadorGlobal.addEventListener('keydown', (evento) => {
      if (evento.key === 'Enter' && buscadorGlobal.value.trim()) {
        BO.irA('joyas');
        setTimeout(() => {
          const inputBusquedaJoyas = document.querySelector('[data-filtro="busqueda"]');
          if (inputBusquedaJoyas) {
            inputBusquedaJoyas.value = buscadorGlobal.value.trim();
            inputBusquedaJoyas.dispatchEvent(new Event('input'));
          }
        }, 50);
      }
    });
  }

  BO.inicializarRouter();
});
