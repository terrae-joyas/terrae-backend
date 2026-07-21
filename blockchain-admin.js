/**
 * TERRAE — admin-modules/configuracion.js
 * -----------------------------------------------------------------------
 * Módulo 14: Configuración. Administra las reglas que gobiernan la
 * generación automática de ID (módulo 4), certificados, QR y blockchain,
 * además de idiomas/monedas/impuestos. La sección de identidad visual es
 * de solo lectura: los tokens de marca (Fase 0) no se editan desde aquí,
 * solo se documentan como referencia.
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('configuracion', {
  async montar(contenedor) {
    const config = await AdminAPI.configuracion.obtener();
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Configuración</h1>
            <p class="bo-vista__subtitulo">Reglas del sistema. Los cambios aquí afectan a toda la operación.</p>
          </div>
        </div>

        <div class="bo-panel" style="margin-bottom:var(--space-3);">
          <div class="bo-panel__titulo">Numeración de joyas</div>
          <form id="cfg-numeracion" class="bo-form-grid">
            <div class="campo"><label class="campo__label" for="cn-prefijo">Prefijo</label><input class="campo__input" id="cn-prefijo" name="prefijo" value="${BO.escapeHtml(config.numeracion.prefijo)}"></div>
            <div class="campo"><label class="campo__label" for="cn-secuencial">Secuencial actual</label><input class="campo__input" id="cn-secuencial" name="secuencialActual" type="number" value="${config.numeracion.secuencialActual}"></div>
            <div class="campo campo--ancho-completo">
              <label class="campo__label" for="cn-formato">Formato (usa {prefijo}, {anio}, {secuencial:N})</label>
              <input class="campo__input" id="cn-formato" name="formato" value="${BO.escapeHtml(config.numeracion.formato)}">
            </div>
            <div class="campo--ancho-completo" style="text-align:right;"><button class="boton boton--esmeralda boton--pequeno" type="submit">Guardar</button></div>
          </form>
        </div>

        <div class="bo-panel" style="margin-bottom:var(--space-3);">
          <div class="bo-panel__titulo">Certificados</div>
          <form id="cfg-certificados" class="bo-form-grid">
            <div class="campo">
              <label class="campo__label" for="cc-plantilla">Plantilla</label>
              <select class="campo__select" id="cc-plantilla" name="plantilla">
                <option value="clasica-verde" ${config.certificados.plantilla === 'clasica-verde' ? 'selected' : ''}>Clásica Verde Terrae</option>
                <option value="edicion-oscura" ${config.certificados.plantilla === 'edicion-oscura' ? 'selected' : ''}>Edición oscura (colección especial)</option>
              </select>
            </div>
            <div class="campo">
              <label class="campo__label">Idiomas habilitados</label>
              <div style="display:flex;gap:12px;padding-top:8px;">
                <label><input type="checkbox" name="idioma_es" ${config.certificados.idiomasHabilitados.includes('es') ? 'checked' : ''}> Español</label>
                <label><input type="checkbox" name="idioma_en" ${config.certificados.idiomasHabilitados.includes('en') ? 'checked' : ''}> Inglés</label>
              </div>
            </div>
            <div class="campo--ancho-completo" style="text-align:right;"><button class="boton boton--esmeralda boton--pequeno" type="submit">Guardar</button></div>
          </form>
        </div>

        <div class="bo-panel" style="margin-bottom:var(--space-3);">
          <div class="bo-panel__titulo">Código QR</div>
          <p class="campo__ayuda">Formatos generados automáticamente: PNG, SVG y alta resolución. Configuración de tamaño y nivel de corrección de errores disponible cuando el generador real (backend, librería <code>qrcode</code>) esté conectado.</p>
        </div>

        <div class="bo-panel" style="margin-bottom:var(--space-3);">
          <div class="bo-panel__titulo">Blockchain</div>
          <form id="cfg-blockchain" class="bo-form-grid">
            <div class="campo">
              <label class="campo__label" for="cb-red">Red predeterminada</label>
              <input class="campo__input" id="cb-red" name="redPredeterminada" value="${BO.escapeHtml(config.blockchain.redPredeterminada)}">
            </div>
            <div class="campo">
              <label class="campo__label">Conexión real</label>
              <p class="campo__ayuda" style="padding-top:8px;">${config.blockchain.habilitado ? 'Habilitada' : 'Deshabilitada — solo registro manual (Fase 4)'}</p>
            </div>
            <div class="campo--ancho-completo" style="text-align:right;"><button class="boton boton--esmeralda boton--pequeno" type="submit">Guardar</button></div>
          </form>
        </div>

        <div class="bo-panel" style="margin-bottom:var(--space-3);">
          <div class="bo-panel__titulo">Idiomas, monedas e impuestos</div>
          <div class="bo-form-grid">
            <div class="campo"><span class="campo__label">Idiomas</span><p>${config.idiomas.join(', ')}</p></div>
            <div class="campo"><span class="campo__label">Monedas</span><p>${config.monedas.join(', ')}</p></div>
            <div class="campo"><span class="campo__label">IVA</span><p>${config.impuestos.ivaPorcentaje}%</p></div>
          </div>
        </div>

        <div class="bo-panel">
          <div class="bo-panel__titulo">Identidad visual (solo lectura)</div>
          <p class="campo__ayuda">Definida en la Fase 0. No editable desde este panel para preservar la consistencia de marca.</p>
          <div style="display:flex;gap:8px;margin-top:8px;">
            ${['--terrae-verde-950', '--terrae-oro-500', '--terrae-nogal-950', '--terrae-marfil-100', '--terrae-esmeralda-500']
              .map((v) => `<div style="width:32px;height:32px;border-radius:4px;background:var(${v});border:1px solid var(--bo-borde-fuerte);" title="${v}"></div>`).join('')}
          </div>
        </div>
      </section>`;

    document.getElementById('cfg-numeracion').addEventListener('submit', (e) => guardarSeccion(e, 'numeracion', (d) => ({ ...d, secuencialActual: Number(d.secuencialActual) })));
    document.getElementById('cfg-certificados').addEventListener('submit', (e) => guardarSeccion(e, 'certificados', (d) => ({
      plantilla: d.plantilla,
      idiomasHabilitados: [d.idioma_es ? 'es' : null, d.idioma_en ? 'en' : null].filter(Boolean),
    })));
    document.getElementById('cfg-blockchain').addEventListener('submit', (e) => guardarSeccion(e, 'blockchain', (d) => ({ redPredeterminada: d.redPredeterminada })));
  },
});

async function guardarSeccion(evento, seccion, transformar) {
  evento.preventDefault();
  const datos = Object.fromEntries(new FormData(evento.target).entries());
  await AdminAPI.configuracion.actualizar(seccion, transformar(datos));
  BO.toast('Configuración actualizada.');
}
