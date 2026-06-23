(function () {
  function buildUrl(base) {
    const riesgo = document.getElementById('riesgoFilter')?.value;
    if (!riesgo) return base;
    const sep = base.indexOf('?') >= 0 ? '&' : '?';
    return base + sep + 'riesgo_enfermedad=' + encodeURIComponent(riesgo);
  }

  function updateLinks() {
    ['exportCsv', 'exportPdf', 'exportExcel'].forEach(function (id) {
      const el = document.getElementById(id);
      if (!el) return;
      const base = el.getAttribute('data-base') || el.getAttribute('href');
      el.setAttribute('data-base', base.split('?')[0]);
      el.href = buildUrl(el.getAttribute('data-base'));
    });
  }

  document.getElementById('riesgoFilter')?.addEventListener('change', updateLinks);
  updateLinks();
})();
