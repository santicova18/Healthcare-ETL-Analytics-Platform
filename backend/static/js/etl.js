(function () {
  async function runEtl(e) {
    e.preventDefault();
    const btn = document.getElementById('etlRunBtn');
    const successEl = document.getElementById('etlSuccess');
    const resultEl = document.getElementById('etlResult');
    HealthAPI.hideError('etlError');
    successEl.classList.add('d-none');
    resultEl.classList.add('d-none');
    btn.disabled = true;

    try {
      const fileInput = document.getElementById('etlFile');
      const formData = new FormData();
      if (fileInput && fileInput.files.length) {
        formData.append('file', fileInput.files[0]);
      }
      const data = await HealthAPI.apiPostForm('/api/etl/run/', formData);
      successEl.textContent = 'ETL ejecutado correctamente.';
      successEl.classList.remove('d-none');
      document.getElementById('etlRecords').textContent = data.records_created ?? '-';
      document.getElementById('etlElapsed').textContent = data.elapsed_seconds ?? '-';
      resultEl.classList.remove('d-none');
    } catch (err) {
      HealthAPI.showError('etlError', err.message);
    } finally {
      btn.disabled = false;
    }
  }

  document.getElementById('etlForm')?.addEventListener('submit', runEtl);
})();
