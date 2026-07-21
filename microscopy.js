/**
 * TERRAE — admin-modules/auditoria.js
 * -----------------------------------------------------------------------
 * Módulo 13: Auditoría. Vista de solo lectura del log append-only que
 * AdminAPI genera automáticamente en cada mutación (usuario, acción,
 * fecha/hora, entidad, cambios). El campo IP queda documentado como
 * "—" hasta que exista backend real, que es el único que puede
 * capturarlo de forma confiable (nunca desde el cliente).
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('auditoria', {
  async montar(contenedor) {
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Auditoría</h1>
            <p class="bo-vista__subtitulo">Registro inmutable de toda acción realizada en el Centro de Operaciones.</p>
          </div>
        </div>
        <div class="bo-toolbar">
          <div class="bo-toolbar__filtros">
            <select id="aud-filtro-entidad">
              <option value="">Todas las entidades</option>
              <option>Joya</option><option>Esmeralda</option><option>Certificado</option>
              <option>Blockchain</option><option>Propietario</option><option>Garantia</option>
              <option>Mantenimiento</option><option>Usuario</option><option>Configuracion</option>
            </select>
          </div>
        </div>
        <div id="aud-tabla"></div>
      </section>`;

    document.getElementById('aud-filtro-entidad').addEventListener('change', recargarTablaAuditoria);
    await recargarTablaAuditoria();
  },
});

async function recargarTablaAuditoria() {
  const contenedor = document.getElementById('aud-tabla');
  if (!contenedor) return;
  const filtroEntidad = document.getElementById('aud-filtro-entidad')?.value || '';
  let eventos = await AdminAPI.auditoria.listar({ limite: 500 });
  if (filtroEntidad) eventos = eventos.filter((e) => e.entidad === filtroEntidad);

  BO.renderizarTabla(contenedor, {
    filaVacia: 'Sin eventos de auditoría todavía.',
    porPagina: 15,
    columnas: [
      { clave: 'fecha', titulo: 'Fecha y hora', ordenable: true, render: (e) => `<span class="dato-tecnico">${BO.formatearFechaHora(e.fecha)}</span>` },
      { clave: 'usuario', titulo: 'Usuario', ordenable: true },
      { clave: 'accion', titulo: 'Acción', render: (e) => `<span class="etiqueta">${BO.escapeHtml(e.accion)}</span>` },
      { clave: 'entidad', titulo: 'Entidad' },
      { clave: 'entidadId', titulo: 'ID', render: (e) => `<span class="dato-tecnico">${BO.escapeHtml(String(e.entidadId).slice(0, 18))}</span>` },
      { clave: 'ip', titulo: 'IP', render: () => '<span class="campo__ayuda">Disponible con backend real</span>' },
    ],
    filas: eventos,
  });
}
