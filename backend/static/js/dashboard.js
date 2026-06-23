(function () {
  var charts = {};

  function destroyChart(id) {
    if (charts[id]) {
      charts[id].destroy();
      delete charts[id];
    }
  }

  function mkDoughnut(canvasId, labels, data, colors) {
    destroyChart(canvasId);
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;
    charts[canvasId] = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{ data: data, backgroundColor: colors }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 }, padding: 8 } } },
      },
    });
  }

  function mkBar(canvasId, labels, data, label) {
    destroyChart(canvasId);
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;
    charts[canvasId] = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{ label: label || 'Pacientes', data: data, backgroundColor: '#0d6efd' }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0, font: { size: 10 } } }, x: { ticks: { font: { size: 10 } } } },
      },
    });
  }

  function mkPie(canvasId, labels, data) {
    destroyChart(canvasId);
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;
    charts[canvasId] = new Chart(canvas, {
      type: 'pie',
      data: { labels: labels, datasets: [{ data: data }] },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 }, padding: 8 } } },
      },
    });
  }

  function mkLine(canvasId, labels, data, label) {
    destroyChart(canvasId);
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;
    charts[canvasId] = new Chart(canvas, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: label || 'Pacientes',
          data: data,
          borderColor: '#0d6efd',
          backgroundColor: 'rgba(13,110,253,.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0, font: { size: 10 } } }, x: { ticks: { font: { size: 10 } } } },
      },
    });
  }

  function renderKpis(kpis, predCount) {
    var items = [
      { label: 'Total', value: kpis.total_pacientes || 0, icon: 'bi-people', cls: '' },
      { label: 'Críticos', value: kpis.pacientes_criticos || 0, icon: 'bi-exclamation-triangle', cls: 'critical' },
      { label: 'Hipertensos', value: kpis.hipertensos || 0, icon: 'bi-heart', cls: 'warning' },
      { label: 'Diabéticos', value: kpis.diabeticos || 0, icon: 'bi-droplet', cls: 'warning' },
      { label: 'Fumadores', value: kpis.fumadores || 0, icon: 'bi-fire', cls: '' },
      { label: 'Riesgo prom.', value: (kpis.riesgo_promedio || 0).toFixed(2), icon: 'bi-graph-up', cls: 'success' },
      { label: 'Pred. ML', value: predCount || 0, icon: 'bi-cpu', cls: '' },
    ];

    var container = document.getElementById('kpiCards');
    container.innerHTML = items.map(function (item) {
      return (
        '<div class="col-6 col-md-3 col-xl">' +
          '<div class="card shadow-sm kpi-card ' + item.cls + ' h-100">' +
            '<div class="card-body py-2 px-3">' +
              '<div class="d-flex justify-content-between align-items-center">' +
                '<div class="text-muted" style="font-size:0.7rem;">' + item.label + '</div>' +
                '<i class="bi ' + item.icon + ' text-muted" style="font-size:0.8rem;"></i>' +
              '</div>' +
              '<div class="fw-semibold" style="font-size:1.1rem;">' + item.value + '</div>' +
            '</div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  async function loadDashboard() {
    var loading = document.getElementById('dashboardLoading');
    var content = document.getElementById('dashboardContent');
    HealthAPI.hideError('dashboardError');
    loading.classList.remove('d-none');
    content.classList.add('d-none');

    try {
      var base = '/api/dashboard';
      var results = await Promise.all([
        HealthAPI.apiGet(base + '/kpis/'),
        HealthAPI.apiGet(base + '/charts/'),
        HealthAPI.apiGet(base + '/trends/'),
      ]);
      var kpis = results[0];
      var chartsData = results[1];
      var trends = results[2];

      renderKpis(kpis, chartsData.predicciones?.count || 0);

      var risk = chartsData.distribucion_riesgo || { labels: [], data: [] };
      mkDoughnut('riskChart', risk.labels, risk.data, ['#dc3545', '#fd7e14', '#ffc107', '#198754']);

      var sex = chartsData.distribucion_sexo || { labels: [], data: [] };
      mkDoughnut('sexChart', sex.labels, sex.data, ['#0d6efd', '#d63384', '#6c757d']);

      var age = chartsData.edad_buckets || { labels: [], data: [] };
      mkBar('ageBar', age.labels, age.data);

      var imc = chartsData.imc_buckets || { labels: [], data: [] };
      mkBar('imcBar', imc.labels, imc.data);

      var diag = chartsData.distribucion_diagnostico || { labels: [], data: [] };
      mkPie('diagPie', diag.labels, diag.data);

      var trend = trends.tendencias_pacientes || { labels: [], data: [] };
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
