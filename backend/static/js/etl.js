(function () {
  async function runEtl(e) {
    e.preventDefault();
    const btn = document.getElementById('etlRunBtn');
    const successEl = document.getElementById('etlSuccess');
    const errorEl = document.getElementById('etlError');
    const resultEl = document.getElementById('etlResult');
    HealthAPI.hideError('etlError');
    successEl.classList.add('d-none');
    errorEl.classList.add('d-none');
    resultEl.classList.add('d-none');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Procesando...';

    try {
      var fileInput = document.getElementById('etlFile');
      var formData = new FormData();
      if (fileInput && fileInput.files.length) {
        formData.append('file', fileInput.files[0]);
      }
      var data = await HealthAPI.apiPostForm('/api/etl/run/', formData);

      if (data.ok) {
        document.getElementById('etlRecords').textContent = data.processed || 0;
        document.getElementById('etlInserted').textContent = data.inserted || 0;
        document.getElementById('etlDuplicates').textContent = data.duplicates || 0;
        document.getElementById('etlElapsed').textContent = data.elapsed_seconds || '-';
        successEl.innerHTML = '<i class="bi bi-check-circle me-1"></i>ETL ejecutado correctamente.';
        successEl.className = 'alert alert-success';
        successEl.classList.remove('d-none');
        resultEl.classList.remove('d-none');
      } else if (data.reason === 'dataset_already_processed') {
        var msg = data.message || 'Este archivo ya fue procesado anteriormente.';
        if (data.processed_at) {
          msg += '<br><small class="text-muted">Procesado el: ' + data.processed_at.split('T')[0] + '</small>';
        }
        if (data.records_inserted) {
          msg += '<br><small class="text-muted">Se insertaron ' + data.records_inserted + ' pacientes en esa ejecución.</small>';
        }
        msg += '<br><small class="text-muted">Si necesita reprocesar, cargue un archivo diferente o con datos nuevos.</small>';
        errorEl.innerHTML = '<i class="bi bi-exclamation-triangle me-1"></i>' + msg;
        errorEl.className = 'alert alert-warning';
        errorEl.classList.remove('d-none');
      }
    } catch (err) {
      var msg = err.message || 'Error desconocido';
      if (msg.indexOf('payload JSON') !== -1) {
        msg = 'Seleccione un archivo CSV o XLSX para procesar, o use el dataset por defecto.';
      }
      HealthAPI.showError('etlError', msg);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Ejecutar ETL';
    }
  }

  document.getElementById('etlForm')?.addEventListener('submit', runEtl);
})();
