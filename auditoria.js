/**
 * TERRAE — admin-modules/esmeraldas.js
 * -----------------------------------------------------------------------
 * Módulo 3: Gestión de Esmeraldas. Registro independiente de la joya
 * (una esmeralda existe antes de engastarse) con todos los campos
 * gemológicos. El campo `informeSiegemId` queda preparado y visible en
 * el drawer, pero no editable todavía (integración futura).
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('esmeraldas', {
  async montar(contenedor) {
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Gestión de Esmeraldas</h1>
            <p class="bo-vista__subtitulo">Registro gemológico independiente, previo al engaste.</p>
          </div>
          <button class="boton boton--esmeralda" data-accion="nueva-esmeralda" type="button">Registrar esmeralda</button>
        </div>
        <div id="esmeraldas-tabla"></div>
      </section>`;

    contenedor.querySelector('[data-accion="nueva-esmeralda"]').addEventListener('click', () => abrirDrawerEsmeralda());
    await recargarTablaEsmeraldas();
  },
});

async function recargarTablaEsmeraldas() {
  const contenedor = document.getElementById('esmeraldas-tabla');
  if (!contenedor) return;
  const esmeraldas = await AdminAPI.esmeraldas.listar();

  BO.renderizarTabla(contenedor, {
    filaVacia: 'No hay esmeraldas registradas todavía.',
    columnas: [
      { clave: 'codigoInterno', titulo: 'Código', ordenable: true, render: (e) => `<span class="dato-tecnico">${BO.escapeHtml(e.codigoInterno)}</span>` },
      { clave: 'mina', titulo: 'Mina', ordenable: true },
      { clave: 'municipio', titulo: 'Origen', render: (e) => `${BO.escapeHtml(e.municipio)}, ${BO.escapeHtml(e.departamento)}` },
      { clave: 'pesoQuilates', titulo: 'Quilates', ordenable: true, render: (e) => `${e.pesoQuilates} ct` },
      { clave: 'color', titulo: 'Color' },
      { clave: 'estado', titulo: 'Estado', render: (e) => `<span class="estado ${e.estado === 'certificada' ? 'estado--exito' : 'estado--alerta'}">${BO.escapeHtml(e.estado)}</span>` },
      { clave: 'informeSiegemId', titulo: 'SIEGEM LAB', render: (e) => (e.informeSiegemId ? '<span class="estado estado--exito">Sincronizado</span>' : '<span class="campo__ayuda">No integrado</span>') },
      {
        clave: 'acciones', titulo: '', render: (e) => `
        <div class="bo-tabla__acciones">
          <button class="bo-tabla__icono-boton" data-accion="editar-esm" data-id="${e.id}" title="Editar" type="button">✎</button>
        </div>`,
      },
    ],
    filas: esmeraldas,
  });

  contenedor.querySelectorAll('[data-accion="editar-esm"]').forEach((b) => b.addEventListener('click', () => abrirDrawerEsmeralda(b.dataset.id)));
}

async function abrirDrawerEsmeralda(id = null) {
  const esmeralda = id ? await AdminAPI.esmeraldas.obtener(id) : null;
  const v = (campo, porDefecto = '') => BO.escapeHtml(esmeralda ? esmeralda[campo] ?? porDefecto : porDefecto);

  const cuerpoHTML = `
    <div class="bo-form-grid">
      <div class="campo">
        <label class="campo__label" for="ef-codigo">Código interno</label>
        <input class="campo__input" id="ef-codigo" name="codigoInterno" value="${v('codigoInterno')}" required>
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-mina">Mina</label>
        <input class="campo__input" id="ef-mina" name="mina" value="${v('mina')}" required>
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-municipio">Municipio</label>
        <input class="campo__input" id="ef-municipio" name="municipio" value="${v('municipio', 'Muzo')}" required>
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-departamento">Departamento</label>
        <input class="campo__input" id="ef-departamento" name="departamento" value="${v('departamento', 'Boyacá')}" required>
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-pais">País</label>
        <input class="campo__input" id="ef-pais" name="pais" value="${v('pais', 'Colombia')}" required>
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-peso">Peso (quilates)</label>
        <input class="campo__input" id="ef-peso" name="pesoQuilates" type="number" step="0.01" value="${v('pesoQuilates')}" required>
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-color">Color</label>
        <input class="campo__input" id="ef-color" name="color" value="${v('color')}" required>
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-claridad">Claridad</label>
        <input class="campo__input" id="ef-claridad" name="claridad" value="${v('claridad')}">
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-corte">Corte</label>
        <input class="campo__input" id="ef-corte" name="corte" value="${v('corte')}">
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-tratamientos">Tratamientos</label>
        <input class="campo__input" id="ef-tratamientos" name="tratamientos" value="${v('tratamientos', 'Ninguno')}">
      </div>
      <div class="campo campo--ancho-completo">
        <label class="campo__label" for="ef-inclusiones">Inclusiones</label>
        <textarea class="campo__textarea" id="ef-inclusiones" name="inclusiones" rows="2">${v('inclusiones')}</textarea>
      </div>
      <div class="campo">
        <label class="campo__label" for="ef-estado">Estado</label>
        <select class="campo__select" id="ef-estado" name="estado">
          ${['pendiente', 'en-analisis', 'certificada'].map((s) => `<option ${(esmeralda?.estado || 'pendiente') === s ? 'selected' : ''}>${s}</option>`).join('')}
        </select>
      </div>
      <div class="campo">
        <label class="campo__label">Informe SIEGEM LAB</label>
        <input class="campo__input" value="${esmeralda?.informeSiegemId ? BO.escapeHtml(esmeralda.informeSiegemId) : 'No sincronizado — integración futura'}" disabled>
      </div>
      <div class="campo campo--ancho-completo">
        <span class="campo__label">Fotografías microscópicas</span>
        <div id="ef-uploader"></div>
      </div>
    </div>`;

  const { formulario, cerrar } = BO.abrirDrawer({
    titulo: esmeralda ? `Editar · ${esmeralda.codigoInterno}` : 'Registrar esmeralda',
    cuerpoHTML,
    async alGuardar(datos) {
      const { esValido, errores } = BO.validarFormulario(datos, {
        codigoInterno: [BO.validadores.requerido],
        mina: [BO.validadores.requerido],
        pesoQuilates: [BO.validadores.requerido, BO.validadores.numeroPositivo],
        color: [BO.validadores.requerido],
      });
      if (!esValido) return BO.toast(Object.values(errores)[0], 'error');

      const existentes = await AdminAPI.esmeraldas.listar();
      if (!esmeralda) {
        const sinDuplicado = await BO.validadores.sinDuplicado(datos.codigoInterno, existentes, 'codigoInterno');
        if (sinDuplicado !== true) return BO.toast(sinDuplicado, 'error');
      }

      const payload = { ...datos, pesoQuilates: Number(datos.pesoQuilates) };
      if (esmeralda) await AdminAPI.esmeraldas.actualizar(esmeralda.id, payload);
      else await AdminAPI.esmeraldas.crear(payload);

      BO.toast('Esmeralda guardada correctamente.');
      cerrar();
      recargarTablaEsmeraldas();
    },
  });

  BO.inicializarUploader(formulario.querySelector('#ef-uploader'), { tiposPermitidos: ['image/jpeg', 'image/png'], maxMB: 15 });
}
