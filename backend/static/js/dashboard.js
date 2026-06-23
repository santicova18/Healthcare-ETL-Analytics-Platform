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

  function renderKpis(kpis, predData) {
    var predCount = predData.count || 0;
    var items = [
      { label: 'Total', value: kpis.total_pacientes || 0, icon: 'bi-people', cls: '', id: 'kpi-total' },
      { label: 'Críticos', value: kpis.pacientes_criticos || 0, icon: 'bi-exclamation-triangle', cls: 'critical', id: 'kpi-criticos' },
      { label: 'Hipertensos', value: kpis.hipertensos || 0, icon: 'bi-heart', cls: 'warning', id: 'kpi-hipertensos' },
      { label: 'Diabéticos', value: kpis.diabeticos || 0, icon: 'bi-droplet', cls: 'warning', id: 'kpi-diabeticos' },
      { label: 'Fumadores', value: kpis.fumadores || 0, icon: 'bi-fire', cls: '', id: 'kpi-fumadores' },
      { label: 'Riesgo prom.', value: (kpis.riesgo_promedio || 0).toFixed(2), icon: 'bi-graph-up', cls: 'success', id: 'kpi-riesgo' },
      { label: 'Pred. ML', value: predCount, icon: 'bi-cpu', cls: '', id: 'kpi-predicciones', clickable: true },
    ];

    var container = document.getElementById('kpiCards');
    container.innerHTML = items.map(function (item) {
      var clickAttr = item.clickable ? ' style="cursor:pointer;" class="kpi-pred-clickable"' : '';
      return (
        '<div class="col-6 col-md-3 col-xl"' + (item.id ? ' id="' + item.id + '"' : '') + '>' +
          '<div class="card shadow-sm kpi-card ' + item.cls + ' h-100"' + clickAttr + '>' +
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

    // Si hay predicciones, hacer la tarjeta clickeable para mostrar las últimas
    if (predCount > 0) {
      var predCard = container.querySelector('.kpi-pred-clickable');
      if (predCard) {
        predCard.title = 'Ver últimas predicciones';
        predCard.addEventListener('click', function () {
          showPredictionsDetail(predData.items || []);
        });
      }
    }
  }

  // Muestra un modal con las últimas predicciones
  function showPredictionsDetail(items) {
    var modal = document.getElementById('predDashboardModal');
    if (!modal) {
      // Crear modal dinámico si no existe
      modal = document.createElement('div');
      modal.id = 'predDashboardModal';
      modal.className = 'modal fade';
      modal.tabIndex = -1;
      modal.innerHTML =
        '<div class="modal-dialog modal-lg modal-dialog-scrollable">' +
          '<div class="modal-content">' +
            '<div class="modal-header bg-info text-white py-2">' +
              '<h5 class="modal-title"><i class="bi bi-cpu me-2"></i>Últimas predicciones realizadas</h5>' +
              '<button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>' +
            '</div>' +
            '<div class="modal-body p-0">' +
              '<table class="table table-sm table-hover mb-0" style="font-size:0.8rem;">' +
                '<thead class="table-light"><tr>' +
                  '<th>ID</th><th>Paciente</th><th>Riesgo</th><th>Confianza</th><th>Fecha</th>' +
                '</tr></thead>' +
                '<tbody id="predDashboardBody"></tbody>' +
              '</table>' +
            '</div>' +
            '<div class="modal-footer py-2">' +
              '<a href="/ml/" class="btn btn-sm btn-primary">Ir a ML</a>' +
              '<button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cerrar</button>' +
            '</div>' +
          '</div>' +
        '</div>';
      document.body.appendChild(modal);
    }

    var tbody = modal.querySelector('#predDashboardBody');
    var badgeMap = { 'Crítico': 'danger', 'Alto': 'warning', 'Medio': 'info', 'Bajo': 'success' };
    tbody.innerHTML = items.map(function (p) {
      var badge = badgeMap[p.prediction] || 'secondary';
      var nombre = (p.nombres || '') + ' ' + (p.apellidos || '');
      return (
        '<tr>' +
          '<td><a href="/patients/" class="text-primary">' + (p.id_paciente || '-') + '</a></td>' +
          '<td>' + (nombre.trim() || 'Paciente #' + p.id_paciente) + '</td>' +
          '<td><span class="badge bg-' + badge + '">' + (p.prediction || '-') + '</span></td>' +
          '<td>' + (p.probability || '-') + '%</td>' +
          '<td class="text-nowrap">' + (p.created_at ? p.created_at.split('T')[0] : '-') + '</td>' +
        '</tr>'
      );
    }).join('');

    var bsModal = bootstrap.Modal.getOrCreateInstance(modal);
    bsModal.show();
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

      renderKpis(kpis, chartsData.predicciones || { count: 0, items: [] });

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
