/**
 * TERRAE — admin-modules/multimedia.js
 * -----------------------------------------------------------------------
 * Módulo 11: Gestión Multimedia. Vista centralizada de todo lo subido
 * por pieza (fotografías, videos, certificados, documentos). En esta
 * fase, la carga real ya sucede dentro de cada módulo (Joyas, Esmeraldas,
 * Mantenimientos) vía BO.inicializarUploader — este módulo es el
 * "explorador" de lo ya organizado por joya, preparado para apuntar a
 * Object Storage (local hoy, S3/R2 cuando exista backend).
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('multimedia', {
  async montar(contenedor) {
    const joyas = await AdminAPI.joyas.listar();
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Gestión Multimedia</h1>
            <p class="bo-vista__subtitulo">Archivos organizados automáticamente por pieza. Almacenamiento local hoy; preparado para la nube (Object Storage) en la Fase 5.</p>
          </div>
        </div>
        <div class="bo-tabla-wrap">
          <table class="bo-tabla">
            <thead><tr><th>Pieza</th><th>Fotografías</th><th>Videos</th><th>Certificado</th><th>QR</th></tr></thead>
            <tbody>
              ${joyas.map((j) => `
                <tr>
                  <td class="dato-tecnico">${BO.escapeHtml(j.id)} — ${BO.escapeHtml(j.nombre)}</td>
                  <td>${j.fotografias?.length || 0} archivo(s)</td>
                  <td>${j.videos?.length || 0} archivo(s)</td>
                  <td>${j.certificadoId ? '<span class="estado estado--exito">Disponible</span>' : '<span class="campo__ayuda">Pendiente</span>'}</td>
                  <td>${j.qrId ? '<span class="estado estado--exito">Generado</span>' : '—'}</td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>
        <p class="campo__ayuda" style="margin-top:var(--space-2);">Para subir nuevo material, hazlo desde el registro/edición de la pieza correspondiente en el módulo <em>Gestión de Joyas</em> — mantiene la organización automática por ID de pieza.</p>
      </section>`;
  },
});
