/**
 * TERRAE — admin-modules/usuarios.js
 * -----------------------------------------------------------------------
 * Módulo 12: Usuarios y Roles. Los 7 roles del prompt (Super Admin,
 * Admin, Gemólogo, Diseñador, Operador, Consultor, Auditor) con una
 * matriz de permisos explícita — separación de funciones documentada
 * visualmente, coherente con la regla "un operador nunca audita su
 * propia pieza" ya aplicada en el backend de la Fase 1.
 * -----------------------------------------------------------------------
 */

const ROLES_TERRAE = ['SUPER_ADMIN', 'ADMIN', 'GEMOLOGO', 'DISENADOR', 'OPERADOR', 'CONSULTOR', 'AUDITOR'];

const MATRIZ_PERMISOS = {
  'Gestión de Joyas (crear/editar)': { SUPER_ADMIN: true, ADMIN: true, GEMOLOGO: false, DISENADOR: false, OPERADOR: true, CONSULTOR: false, AUDITOR: false },
  'Aprobar certificados': { SUPER_ADMIN: true, ADMIN: false, GEMOLOGO: true, DISENADOR: false, OPERADOR: false, CONSULTOR: false, AUDITOR: true },
  'Gestión de Esmeraldas': { SUPER_ADMIN: true, ADMIN: true, GEMOLOGO: true, DISENADOR: false, OPERADOR: false, CONSULTOR: false, AUDITOR: false },
  'Registrar propietarios': { SUPER_ADMIN: true, ADMIN: true, GEMOLOGO: false, DISENADOR: false, OPERADOR: true, CONSULTOR: false, AUDITOR: false },
  'Ver auditoría': { SUPER_ADMIN: true, ADMIN: true, GEMOLOGO: false, DISENADOR: false, OPERADOR: false, CONSULTOR: false, AUDITOR: true },
  'Configuración del sistema': { SUPER_ADMIN: true, ADMIN: false, GEMOLOGO: false, DISENADOR: false, OPERADOR: false, CONSULTOR: false, AUDITOR: false },
  'Solo lectura / reportes': { SUPER_ADMIN: true, ADMIN: true, GEMOLOGO: true, DISENADOR: true, OPERADOR: true, CONSULTOR: true, AUDITOR: true },
};

BO.registrarModulo('usuarios', {
  async montar(contenedor) {
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Usuarios y Roles</h1>
            <p class="bo-vista__subtitulo">Gestión de accesos y matriz de permisos por rol.</p>
          </div>
          <button class="boton boton--esmeralda" data-accion="nuevo-usuario" type="button">Invitar usuario</button>
        </div>
        <div id="usr-tabla" style="margin-bottom:var(--space-4);"></div>

        <div class="bo-panel">
          <div class="bo-panel__titulo">Matriz de permisos por rol</div>
          <div style="overflow-x:auto;">
            <table class="bo-matriz-permisos">
              <thead><tr><th>Permiso</th>${ROLES_TERRAE.map((r) => `<th>${r.replace('_', ' ')}</th>`).join('')}</tr></thead>
              <tbody>
                ${Object.entries(MATRIZ_PERMISOS).map(([permiso, roles]) => `
                  <tr><th style="font-weight:400;">${BO.escapeHtml(permiso)}</th>${ROLES_TERRAE.map((r) => `<td data-permitido="${!!roles[r]}">${roles[r] ? '✓' : '—'}</td>`).join('')}</tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      </section>`;

    contenedor.querySelector('[data-accion="nuevo-usuario"]').addEventListener('click', () => abrirDrawerUsuario());
    await recargarTablaUsuarios();
  },
});

async function recargarTablaUsuarios() {
  const contenedor = document.getElementById('usr-tabla');
  if (!contenedor) return;
  const usuarios = await AdminAPI.usuarios.listar();

  BO.renderizarTabla(contenedor, {
    filaVacia: 'No hay usuarios registrados.',
    columnas: [
      { clave: 'nombre', titulo: 'Nombre', ordenable: true },
      { clave: 'email', titulo: 'Correo' },
      {
        clave: 'rol', titulo: 'Rol', render: (u) => `
        <select class="campo__select" data-cambiar-rol="${u.id}" style="font-size:0.75rem;padding:4px 8px;">
          ${ROLES_TERRAE.map((r) => `<option value="${r}" ${u.rol === r ? 'selected' : ''}>${r.replace('_', ' ')}</option>`).join('')}
        </select>`,
      },
      { clave: 'activo', titulo: 'Estado', render: (u) => `<span class="estado ${u.activo ? 'estado--exito' : 'estado--error'}">${u.activo ? 'Activo' : 'Inactivo'}</span>` },
      {
        clave: 'acciones', titulo: '', render: (u) => `<div class="bo-tabla__acciones"><button class="bo-tabla__icono-boton" data-alternar="${u.id}" title="${u.activo ? 'Desactivar' : 'Activar'}" type="button">${u.activo ? '⏻' : '↺'}</button></div>`,
      },
    ],
    filas: usuarios,
  });

  contenedor.querySelectorAll('[data-cambiar-rol]').forEach((select) => select.addEventListener('change', async () => {
    await AdminAPI.usuarios.actualizarRol(select.dataset.cambiarRol, select.value);
    BO.toast('Rol actualizado.');
  }));
  contenedor.querySelectorAll('[data-alternar]').forEach((b) => b.addEventListener('click', async () => {
    await AdminAPI.usuarios.alternarActivo(b.dataset.alternar);
    recargarTablaUsuarios();
  }));
}

function abrirDrawerUsuario() {
  const cuerpoHTML = `
    <div class="campo"><label class="campo__label" for="uf-nombre">Nombre completo</label><input class="campo__input" id="uf-nombre" name="nombre" required></div>
    <div class="campo"><label class="campo__label" for="uf-email">Correo electrónico</label><input class="campo__input" id="uf-email" name="email" type="email" required></div>
    <div class="campo">
      <label class="campo__label" for="uf-rol">Rol</label>
      <select class="campo__select" id="uf-rol" name="rol">${ROLES_TERRAE.map((r) => `<option value="${r}">${r.replace('_', ' ')}</option>`).join('')}</select>
    </div>`;

  const { cerrar } = BO.abrirDrawer({
    titulo: 'Invitar nuevo usuario',
    cuerpoHTML,
    textoGuardar: 'Enviar invitación',
    async alGuardar(datos) {
      const { esValido, errores } = BO.validarFormulario(datos, {
        nombre: [BO.validadores.requerido],
        email: [BO.validadores.requerido, BO.validadores.email],
      });
      if (!esValido) return BO.toast(Object.values(errores)[0], 'error');

      const existentes = await AdminAPI.usuarios.listar();
      const sinDuplicado = await BO.validadores.sinDuplicado(datos.email, existentes, 'email');
      if (sinDuplicado !== true) return BO.toast(sinDuplicado, 'error');

      await AdminAPI.usuarios.crear(datos);
      BO.toast('Usuario invitado correctamente.');
      cerrar();
      recargarTablaUsuarios();
    },
  });
}
