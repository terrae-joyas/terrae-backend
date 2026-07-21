/**
 * TERRAE — admin-modules/dashboard.js
 * -----------------------------------------------------------------------
 * Módulo 1: Dashboard Ejecutivo. KPIs calculados sobre AdminAPI (hoy,
 * localStorage; mañana, agregaciones reales de PostgreSQL). El gráfico
 * de barras es SVG/CSS puro para no depender de librerías — el
 * contenedor `.bo-panel` está listo para recibir Chart.js/D3 cuando el
 * backend exponga series temporales reales.
 * -----------------------------------------------------------------------
 */

BO.registrarModulo('dashboard', {
  async montar(contenedor) {
    contenedor.innerHTML = `
      <section class="bo-vista">
        <div class="bo-vista__cabecera">
          <div>
            <h1>Dashboard Ejecutivo</h1>
            <p class="bo-vista__subtitulo">Estado general del ecosistema Terrae en tiempo real.</p>
          </div>
        </div>
        <div class="bo-kpi-grid" id="dash-kpis"></div>
        <div class="bo-paneles-grid">
          <div class="bo-panel">
            <div class="bo-panel__titulo">Certificados emitidos (últimos 6 meses)</div>
            <div class="bo-grafico-barras" id="dash-grafico"></div>
            <div class="bo-grafico-barras__eje" id="dash-grafico-eje"></div>
          </div>
          <div class="bo-panel">
            <div class="bo-panel__titulo">Actividad reciente</div>
            <ul class="bo-lista-actividad" id="dash-actividad"></ul>
          </div>
        </div>
      </section>`;

    const indicadores = await AdminAPI.dashboard.obtenerIndicadores();
    pintarKPIs(indicadores);
    pintarGraficoPreparado(indicadores);
    pintarActividad(indicadores.actividadReciente);
  },
});

function pintarKPIs(indicadores) {
  const tarjetas = [
    { label: 'Total de joyas', valor: indicadores.totalJoyas },
    { label: 'Disponibles', valor: indicadores.joyasDisponibles },
    { label: 'Vendidas', valor: indicadores.joyasVendidas },
    { label: 'Certificados emitidos', valor: indicadores.certificadosEmitidos },
    { label: 'QR generados', valor: indicadores.qrGenerados },
    { label: 'Registros blockchain', valor: indicadores.registrosBlockchain },
    { label: 'Garantías activas', valor: indicadores.garantiasActivas },
    { label: 'Mantenimientos realizados', valor: indicadores.mantenimientosRealizados },
    { label: 'Pendientes de certificación', valor: indicadores.pendientesCertificacion },
    { label: 'Valor estimado del inventario', valor: BO.formatearMoneda(indicadores.valorInventario) },
  ];

  document.getElementById('dash-kpis').innerHTML = tarjetas.map((t) => `
    <div class="bo-kpi">
      <div class="bo-kpi__label">${BO.escapeHtml(t.label)}</div>
      <div class="bo-kpi__valor">${BO.escapeHtml(String(t.valor))}</div>
    </div>`).join('');
}

function pintarGraficoPreparado(indicadores) {
  // Serie simulada a partir del total actual, distribuida en 6 meses —
  // placeholder honesto: cuando el backend exponga /dashboard/series,
  // esto se reemplaza por datos reales sin cambiar el markup.
  const base = Math.max(1, indicadores.certificadosEmitidos);
  const serie = [0.5, 0.65, 0.7, 0.85, 0.95, 1].map((f) => Math.round(base * f));
  const maximo = Math.max(...serie, 1);
  const meses = ['Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul'];

  document.getElementById('dash-grafico').innerHTML = serie
    .map((valor) => `<div class="bo-grafico-barras__barra" style="height:${Math.max(4, (valor / maximo) * 100)}%" title="${valor}"></div>`)
    .join('');
  document.getElementById('dash-grafico-eje').innerHTML = meses.map((m) => `<span>${m}</span>`).join('');
}

function pintarActividad(eventos) {
  const contenedor = document.getElementById('dash-actividad');
  if (!eventos.length) {
    contenedor.innerHTML = '<li>Sin actividad reciente todavía.</li>';
    return;
  }
  contenedor.innerHTML = eventos.map((e) => `
    <li>
      <time>${BO.formatearFechaHora(e.fecha)}</time>
      <span>${BO.escapeHtml(e.usuario)} — ${BO.escapeHtml(e.accion.toLowerCase())} ${BO.escapeHtml(e.entidad.toLowerCase())}</span>
    </li>`).join('');
}
