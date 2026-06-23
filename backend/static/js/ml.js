(function () {
  function riskBadge(riesgo) {
    const map = { 'Crítico': 'danger', 'Alto': 'warning', 'Medio': 'info', 'Bajo': 'success' };
    const cls = map[riesgo] || 'secondary';
    return '<span class="badge bg-' + cls + '">' + riesgo + '</span>';
  }

  async function loadModelInfo() {
    const body = document.getElementById('modelInfoBody');
    const loading = document.getElementById('modelInfoLoading');
    if (!body) return;

    const fmt = function (v) {
      return v != null ? Number(v).toFixed(2) : '-';
    };

    try {
      const data = await HealthAPI.apiGet('/api/ml/model-info/');

      let perClassHtml = '';
      if (data.precision_per_class && typeof data.precision_per_class === 'object') {
        const classes = Object.keys(data.precision_per_class);
        if (classes.length) {
          const rows = classes.map(function (cls) {
            return '<tr>' +
              '<td>' + cls + '</td>' +
              '<td>' + fmt(data.precision_per_class[cls]) + '</td>' +
              '<td>' + fmt(data.recall_per_class[cls]) + '</td>' +
              '<td>' + fmt(data.f1_per_class[cls]) + '</td>' +
            '</tr>';
          }).join('');
          perClassHtml =
            '<div class="mt-2">' +
              '<a class="small" data-bs-toggle="collapse" href="#perClassMetrics" role="button">' +
                'Ver métricas por clase &raquo;' +
              '</a>' +
              '<div class="collapse mt-1" id="perClassMetrics">' +
                '<table class="table table-sm table-bordered mb-0">' +
                  '<thead class="table-light"><tr><th>Clase</th><th>Precision</th><th>Recall</th><th>F1</th></tr></thead>' +
                  '<tbody>' + rows + '</tbody>' +
                '</table>' +
              '</div>' +
            '</div>';
        }
      }

      body.innerHTML =
        '<dl class="row mb-0">' +
          '<dt class="col-sm-5">Versión</dt><dd class="col-sm-7">' + data.version + '</dd>' +
          '<dt class="col-sm-5">Accuracy</dt><dd class="col-sm-7">' + fmt(data.accuracy) + '</dd>' +
          '<dt class="col-sm-5">Precision</dt><dd class="col-sm-7">' + fmt(data.precision) + '</dd>' +
          '<dt class="col-sm-5">Recall</dt><dd class="col-sm-7">' + fmt(data.recall) + '</dd>' +
          '<dt class="col-sm-5">F1</dt><dd class="col-sm-7">' + fmt(data.f1_score) + '</dd>' +
          '<dt class="col-sm-5">Dataset</dt><dd class="col-sm-7">' + (data.dataset_size ?? '-') + '</dd>' +
          '<dt class="col-sm-5">Entrenamiento</dt><dd class="col-sm-7">' + (data.fecha_entrenamiento ?? '-') + '</dd>' +
        '</dl>' +
        perClassHtml;
    } catch (err) {
      if (loading) loading.remove();
      body.innerHTML = '<p class="text-danger mb-0">' + err.message + '</p>';
    }
  }

  async function loadVersions() {
    const tbody = document.getElementById('versionsTableBody');
    if (!tbody) return;

    try {
      const data = await HealthAPI.apiGet('/api/ml/model-versions/');
      const versions = data.versions || [];
      if (!versions.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">Sin versiones registradas</td></tr>';
        return;
      }
      tbody.innerHTML = versions.map(function (v) {
        return (
          '<tr>' +
            '<td>' + v.version + '</td>' +
            '<td>' + (v.algorithm || '-') + '</td>' +
            '<td>' + (v.accuracy != null ? v.accuracy : '-') + '</td>' +
            '<td>' + (v.dataset_size ?? '-') + '</td>' +
            '<td>' + (v.is_active ? '<span class="badge bg-success">Sí</span>' : '<span class="badge bg-secondary">No</span>') + '</td>' +
            '<td>' + (v.created_at || '-') + '</td>' +
          '</tr>'
        );
      }).join('');
    } catch (err) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-danger text-center py-4">' + err.message + '</td></tr>';
    }
  }

  async function runPrediction(e) {
    e.preventDefault();
    const btn = document.getElementById('predictBtn');
    const resultEl = document.getElementById('predictionResult');
    HealthAPI.hideError('mlError');
    btn.disabled = true;

    try {
      const fd = new FormData(e.target);
      const payload = {
        edad: parseInt(fd.get('edad'), 10),
        imc: parseFloat(fd.get('imc')),
        presion_sistolica: parseInt(fd.get('presion_sistolica'), 10),
        presion_diastolica: parseInt(fd.get('presion_diastolica'), 10),
        glucosa: parseFloat(fd.get('glucosa')),
        colesterol: parseFloat(fd.get('colesterol')),
      };
      const patientId = fd.get('patient_id');
      if (patientId) payload.patient_id = parseInt(patientId, 10);

      const data = await HealthAPI.apiPostJson('/api/ml/predicciones/', payload);
      resultEl.innerHTML =
        '<strong>Resultado:</strong> ' + riskBadge(data.riesgo_enfermedad) +
        ' &nbsp; <strong>Confianza:</strong> ' + ((data.confidence * 100).toFixed(1)) + '%';
      resultEl.classList.remove('d-none');
    } catch (err) {
      HealthAPI.showError('mlError', err.message);
      resultEl.classList.add('d-none');
    } finally {
      btn.disabled = false;
    }
  }

  async function runTraining() {
    const btn = document.getElementById('trainBtn');
    const spinner = document.getElementById('trainSpinner');
    const resultEl = document.getElementById('trainResult');
    btn.disabled = true;
    spinner.classList.remove('d-none');
    resultEl.classList.add('d-none');
    HealthAPI.hideError('mlError');

    try {
      const data = await HealthAPI.apiPostJson('/api/ml/train/', {});
      resultEl.innerHTML = '<div class="alert alert-success mb-0">' +
        '<strong>Modelo entrenado correctamente</strong><br>' +
        'Versión: <code>' + (data.version || '-') + '</code>' +
        (data.accuracy != null ? ' &nbsp; Accuracy: <strong>' + Number(data.accuracy).toFixed(4) + '</strong>' : '') +
        '</div>';
      resultEl.classList.remove('d-none');
      loadVersions();
    } catch (err) {
      resultEl.innerHTML = '<div class="alert alert-danger mb-0">' + err.message + '</div>';
      resultEl.classList.remove('d-none');
    } finally {
      btn.disabled = false;
      spinner.classList.add('d-none');
    }
  }

  if (window.ML_SHOW_CLINICAL) {
    loadModelInfo();
    document.getElementById('predictionForm')?.addEventListener('submit', runPrediction);
  }
  if (window.ML_SHOW_ANALYST) {
    loadVersions();
    document.getElementById('refreshVersions')?.addEventListener('click', loadVersions);
    document.getElementById('trainBtn')?.addEventListener('click', runTraining);
  }
})();
