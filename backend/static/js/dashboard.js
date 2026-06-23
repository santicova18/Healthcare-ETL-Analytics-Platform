(function () {
  const charts = {};

  function destroyChart(id) {
    if (charts[id]) {
      charts[id].destroy();
      delete charts[id];
    }
  }

  function mkDoughnut(canvasId, labels, data, colors) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    charts[canvasId] = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{ data, backgroundColor: colors }],
      },
      options: { responsive: true, maintainAspectRatio: true },
    });
  }

  function mkBar(canvasId, labels, data, label) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    charts[canvasId] = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{ label: label || 'Pacientes', data, backgroundColor: '#0d6efd' }],
      },
      options: {
        responsive: true,
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
      },
    });
  }

  function mkPie(canvasId, labels, data) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    charts[canvasId] = new Chart(canvas, {
      type: 'pie',
      data: { labels, datasets: [{ data }] },
      options: { responsive: true },
    });
  }

  function mkLine(canvasId, labels, data, label) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    charts[canvasId] = new Chart(canvas, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: label || 'Pacientes',
          data,
          borderColor: '#0d6efd',
          backgroundColor: 'rgba(13,110,253,.1)',
          fill: true,
          tension: 0.3,
        }],
      },
      options: {
        responsive: true,
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
      },
    });
  }

  function renderKpis(kpis, predCount) {
    const items = [
      { label: 'Total pacientes', value: kpis.total_pacientes ?? 0, cls: '' },
      { label: 'Críticos', value: kpis.pacientes_criticos ?? 0, cls: 'critical' },
      { label: 'Hipertensos', value: kpis.hipertensos ?? 0, cls: 'warning' },
      { label: 'Diabéticos', value: kpis.diabeticos ?? 0, cls: 'warning' },
      { label: 'Fumadores', value: kpis.fumadores ?? 0, cls: '' },
      { label: 'Riesgo promedio', value: kpis.riesgo_promedio ?? 0, cls: 'success' },
      { label: 'Predicciones ML', value: predCount ?? 0, cls: '' },
    ];

    const container = document.getElementById('kpiCards');
    container.innerHTML = items.map(function (item) {
      return (
        '<div class="col-6 col-md-4 col-xl">' +
          '<div class="card shadow-sm kpi-card ' + item.cls + ' h-100">' +
            '<div class="card-body">' +
              '<div class="text-muted small">' + item.label + '</div>' +
              '<div class="fs-4 fw-semibold">' + item.value + '</div>' +
            '</div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  async function loadDashboard() {
    const loading = document.getElementById('dashboardLoading');
    const content = document.getElementById('dashboardContent');
    HealthAPI.hideError('dashboardError');
    loading.classList.remove('d-none');
    content.classList.add('d-none');

    try {
      const base = '/api/dashboard';
      const [kpis, chartsData, trends] = await Promise.all([
        HealthAPI.apiGet(base + '/kpis/'),
        HealthAPI.apiGet(base + '/charts/'),
        HealthAPI.apiGet(base + '/trends/'),
      ]);

      renderKpis(kpis, chartsData.predicciones?.count ?? 0);

      const risk = chartsData.distribucion_riesgo || { labels: [], data: [] };
      mkDoughnut('riskChart', risk.labels, risk.data, ['#dc3545', '#fd7e14', '#ffc107', '#198754']);

      const sex = chartsData.distribucion_sexo || { labels: [], data: [] };
      mkDoughnut('sexChart', sex.labels, sex.data, ['#0d6efd', '#d63384', '#6c757d']);

      const age = chartsData.edad_buckets || { labels: [], data: [] };
      mkBar('ageBar', age.labels, age.data);

      const imc = chartsData.imc_buckets || { labels: [], data: [] };
      mkBar('imcBar', imc.labels, imc.data);

      const diag = chartsData.distribucion_diagnostico || { labels: [], data: [] };
      mkPie('diagPie', diag.labels, diag.data);

      const trend = trends.tendencias_pacientes || { labels: [], data: [] };
      mkLine('trendLine', trend.labels, trend.data);

      loading.classList.add('d-none');
      content.classList.remove('d-none');
    } catch (err) {
      loading.classList.add('d-none');
      HealthAPI.showError('dashboardError', 'Error cargando dashboard: ' + err.message);
    }
  }

  document.getElementById('refreshDashboard')?.addEventListener('click', loadDashboard);
  loadDashboard();
})();
