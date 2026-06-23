(function () {
  var canEdit = window.CAN_EDIT_PATIENTS === true;
  var canDelete = window.CAN_DELETE_PATIENTS === true;
  var patientsCache = [];
  var editModal = null;
  var addModal = null;
  var predictionModal = null;

  function riskBadge(riesgo) {
    var map = {
      'Crítico': 'danger',
      'Alto': 'warning',
      'Medio': 'info',
      'Bajo': 'success',
    };
    var cls = map[riesgo] || 'secondary';
    return '<span class="badge bg-' + cls + '">' + (riesgo || '-') + '</span>';
  }

  function actionButtons(p) {
    if (!canEdit) return '';
    var html = '<button type="button" class="btn btn-sm btn-outline-primary me-1 btn-edit" data-id="' + p.id_paciente + '" title="Editar"><i class="bi bi-pencil"></i></button>';
    if (canDelete) {
      html += '<button type="button" class="btn btn-sm btn-outline-danger btn-delete" data-id="' + p.id_paciente + '" title="Eliminar"><i class="bi bi-trash"></i></button>';
    }
    return html;
  }

  function renderTable(results) {
    var tbody = document.getElementById('patientsTableBody');
    var countEl = document.getElementById('patientCount');
    if (!tbody) return;

    patientsCache = results;
    countEl.textContent = results.length;

    // Ordenar por ID ascendente
    results.sort(function(a, b) { return a.id_paciente - b.id_paciente; });

    var colSpan = canEdit ? 23 : 22;

    if (!results.length) {
      tbody.innerHTML = '<tr><td colspan="' + colSpan + '" class="text-center text-muted py-4">No hay pacientes registrados</td></tr>';
      return;
    }

    tbody.innerHTML = results.map(function (p) {
      return (
        '<tr>' +
          '<td><a href="#" class="text-primary text-decoration-none fw-semibold patient-id-link" data-id="' + p.id_paciente + '" title="Ver predicción de riesgo">' + p.id_paciente + '</a></td>' +
          '<td>' + (p.nombres || '-') + '</td>' +
          '<td>' + (p.apellidos || '-') + '</td>' +
          '<td>' + (p.edad || '-') + '</td>' +
          '<td>' + (p.sexo || '-') + '</td>' +
          '<td>' + (p.peso != null ? Number(p.peso).toFixed(1) : '-') + '</td>' +
          '<td>' + (p.altura != null ? Number(p.altura).toFixed(2) : '-') + '</td>' +
          '<td>' + (p.imc != null ? Number(p.imc).toFixed(1) : '-') + '</td>' +
          '<td>' + (p.presion_sistolica || '-') + '</td>' +
          '<td>' + (p.presion_diastolica || '-') + '</td>' +
          '<td>' + (p.frecuencia_cardiaca || '-') + '</td>' +
          '<td>' + (p.glucosa != null ? Number(p.glucosa).toFixed(0) : '-') + '</td>' +
          '<td>' + (p.colesterol != null ? Number(p.colesterol).toFixed(0) : '-') + '</td>' +
          '<td>' + (p.saturacion_oxigeno != null ? Number(p.saturacion_oxigeno).toFixed(1) : '-') + '</td>' +
          '<td>' + (p.temperatura != null ? Number(p.temperatura).toFixed(1) : '-') + '</td>' +
          '<td>' + (p.antecedentes_familiares ? 'Sí' : 'No') + '</td>' +
          '<td>' + (p.fumador ? 'Sí' : 'No') + '</td>' +
          '<td>' + (p.consumo_alcohol ? 'Sí' : 'No') + '</td>' +
          '<td>' + (p.actividad_fisica || '-') + '</td>' +
          '<td>' + (p.diagnostico_preliminar || '-') + '</td>' +
          '<td>' + riskBadge(p.riesgo_enfermedad) + '</td>' +
          '<td class="text-nowrap">' + (p.fecha_consulta || '-') + '</td>' +
          (canEdit ? '<td class="text-nowrap">' + actionButtons(p) + '</td>' : '') +
        '</tr>'
      );
    }).join('');

    // Handlers para botones de editar
    tbody.querySelectorAll('.btn-edit').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        openEditModal(parseInt(btn.dataset.id, 10));
      });
    });

    // Handlers para botones de eliminar
    tbody.querySelectorAll('.btn-delete').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        deletePatient(parseInt(btn.dataset.id, 10));
      });
    });

    // Handlers para click en ID → predicción
    tbody.querySelectorAll('.patient-id-link').forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var id = parseInt(link.dataset.id, 10);
        showPrediction(id);
      });
    });
  }

  // ─── Modal de predicción ───
  function showPrediction(id) {
    var patient = patientsCache.find(function (x) { return x.id_paciente === id; });
    if (!patient) return;

    if (!predictionModal) {
      predictionModal = new bootstrap.Modal(document.getElementById('predictionModal'));
    }

    document.getElementById('predPatientId').textContent = '#' + id + ' — ' + (patient.nombres || '') + ' ' + (patient.apellidos || '');
    document.getElementById('predictionLoading').classList.remove('d-none');
    document.getElementById('predictionResult').classList.add('d-none');
    document.getElementById('predictionError').classList.add('d-none');
    predictionModal.show();

    var payload = {
      edad: patient.edad || 30,
      imc: patient.imc || 25,
      presion_sistolica: patient.presion_sistolica || 120,
      presion_diastolica: patient.presion_diastolica || 80,
      glucosa: patient.glucosa || 100,
      colesterol: patient.colesterol || 190,
      patient_id: id,
    };

    HealthAPI.apiPostJson('/api/ml/predicciones/', payload)
      .then(function (data) {
        document.getElementById('predictionLoading').classList.add('d-none');
        document.getElementById('predictionResult').classList.remove('d-none');

        var riesgo = data.riesgo_enfermedad;
        var badgeCls = { 'Crítico': 'danger', 'Alto': 'warning', 'Medio': 'info', 'Bajo': 'success' }[riesgo] || 'secondary';
        document.getElementById('predRiskBadge').innerHTML = '<span class="badge bg-' + badgeCls + ' fs-5">' + riesgo + '</span>';
        document.getElementById('predConfidence').textContent = (data.confidence * 100).toFixed(1) + '%';

        var probs = data.probabilidades || {};
        var probHtml = '<div class="progress" style="height:22px;">';
        var colors = { 'Crítico': 'bg-danger', 'Alto': 'bg-warning', 'Medio': 'bg-info', 'Bajo': 'bg-success' };
        var total = 0;
        Object.keys(probs).forEach(function (k) { total += probs[k]; });
        Object.keys(probs).forEach(function (k) {
          var pct = total > 0 ? (probs[k] / total * 100) : 0;
          probHtml += '<div class="progress-bar ' + (colors[k] || 'bg-secondary') + '" style="width:' + pct.toFixed(0) + '%" title="' + k + ': ' + pct.toFixed(1) + '%">' + k + ' ' + pct.toFixed(0) + '%</div>';
        });
        probHtml += '</div>';
        document.getElementById('predProbabilities').innerHTML = probHtml;
      })
      .catch(function (err) {
        document.getElementById('predictionLoading').classList.add('d-none');
        var errEl = document.getElementById('predictionError');
        errEl.textContent = 'Error: ' + (err.message || 'No se pudo obtener la predicción. Verifique que el modelo esté entrenado.');
        errEl.classList.remove('d-none');
      });
  }

  // ─── Helpers IMC ───
  function calcImc(peso, altura) {
    if (peso > 0 && altura > 0) {
      return Math.round((peso / (altura * altura)) * 100) / 100;
    }
    return '';
  }

  function setupImcCalc(formId, imcId) {
    var form = document.getElementById(formId);
    if (!form) return;
    var peso = form.querySelector('[name=peso]');
    var altura = form.querySelector('[name=altura]');
    var imc = document.getElementById(imcId);
    function update() {
      var p = parseFloat(peso.value) || 0;
      var a = parseFloat(altura.value) || 0;
      imc.value = calcImc(p, a);
    }
    if (peso && altura && imc) {
      peso.addEventListener('input', update);
      altura.addEventListener('input', update);
    }
  }

  // ─── Modal Editar ───
  function openEditModal(id) {
    var p = patientsCache.find(function (x) { return x.id_paciente === id; });
    if (!p) return;
    var form = document.getElementById('editPatientForm');
    if (!form) return;
    document.getElementById('editId').value = p.id_paciente;
    form.nombres.value = p.nombres || '';
    form.apellidos.value = p.apellidos || '';
    form.edad.value = p.edad || '';
    form.sexo.value = p.sexo || 'Masculino';
    form.peso.value = p.peso || '';
    form.altura.value = p.altura || '';
    form.presion_sistolica.value = p.presion_sistolica || '';
    form.presion_diastolica.value = p.presion_diastolica || '';
    form.frecuencia_cardiaca.value = p.frecuencia_cardiaca || '';
    form.glucosa.value = p.glucosa || '';
    form.colesterol.value = p.colesterol || '';
    form.saturacion_oxigeno.value = p.saturacion_oxigeno || '';
    form.temperatura.value = p.temperatura || '';
    form.antecedentes_familiares.value = p.antecedentes_familiares ? 'true' : 'false';
    form.fumador.value = p.fumador ? 'true' : 'false';
    form.consumo_alcohol.value = p.consumo_alcohol ? 'true' : 'false';
    form.actividad_fisica.value = p.actividad_fisica || 'Moderada';
    form.riesgo_enfermedad.value = p.riesgo_enfermedad || 'Bajo';
    form.diagnostico_preliminar.value = p.diagnostico_preliminar || '';
    form.fecha_consulta.value = p.fecha_consulta || '';
    var imcEl = document.getElementById('editImc');
    if (imcEl) imcEl.value = p.imc || calcImc(parseFloat(p.peso) || 0, parseFloat(p.altura) || 0);
    if (!editModal) {
      editModal = new bootstrap.Modal(document.getElementById('editPatientModal'));
    }
    editModal.show();
  }

  // ─── Búsqueda ───
  function getSearchText() {
    var el = document.getElementById('patientSearch');
    return (el && el.value) ? el.value.trim() : '';
  }

  function debounce(fn, waitMs) {
    var t = null;
    return function () {
      var args = arguments;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(null, args); }, waitMs);
    };
  }

  // ─── Cargar pacientes ───
  async function loadPatients() {
    var loading = document.getElementById('patientsLoading');
    var tableWrap = document.getElementById('patientsTableWrap');
    HealthAPI.hideError('patientsError');
    loading.classList.remove('d-none');
    tableWrap.classList.add('d-none');

    try {
      var q = getSearchText();
      var qs = q ? ('?q=' + encodeURIComponent(q)) : '';
      var data = await HealthAPI.apiGet('/api/patients/' + qs);
      renderTable(data.results || []);
      loading.classList.add('d-none');
      tableWrap.classList.remove('d-none');
    } catch (err) {
      loading.classList.add('d-none');
      HealthAPI.showError('patientsError', 'Error cargando pacientes: ' + err.message);
    }
  }

  // ─── Serialización de formularios ───
  function formToPayload(form) {
    var fd = new FormData(form);
    var peso = parseFloat(fd.get('peso')) || 70;
    var altura = parseFloat(fd.get('altura')) || 1.7;
    return {
      id_paciente: parseInt(fd.get('id_paciente'), 10),
      nombres: fd.get('nombres'),
      apellidos: fd.get('apellidos'),
      edad: parseInt(fd.get('edad'), 10),
      sexo: fd.get('sexo'),
      peso: peso,
      altura: altura,
      imc: Math.round((peso / (altura * altura)) * 100) / 100,
      presion_sistolica: parseInt(fd.get('presion_sistolica'), 10) || 120,
      presion_diastolica: parseInt(fd.get('presion_diastolica'), 10) || 80,
      frecuencia_cardiaca: parseInt(fd.get('frecuencia_cardiaca'), 10) || 72,
      glucosa: parseFloat(fd.get('glucosa')) || 90,
      colesterol: parseFloat(fd.get('colesterol')) || 180,
      saturacion_oxigeno: parseFloat(fd.get('saturacion_oxigeno')) || 98,
      temperatura: parseFloat(fd.get('temperatura')) || 36.5,
      antecedentes_familiares: fd.get('antecedentes_familiares') === 'true',
      fumador: fd.get('fumador') === 'true',
      consumo_alcohol: fd.get('consumo_alcohol') === 'true',
      actividad_fisica: fd.get('actividad_fisica') || 'Moderada',
      diagnostico_preliminar: fd.get('diagnostico_preliminar') || 'Evaluación inicial',
      riesgo_enfermedad: fd.get('riesgo_enfermedad'),
      fecha_consulta: fd.get('fecha_consulta'),
    };
  }

  function editFormToPayload(form) {
    var fd = new FormData(form);
    var peso = parseFloat(fd.get('peso')) || 70;
    var altura = parseFloat(fd.get('altura')) || 1.7;
    return {
      id_paciente: parseInt(fd.get('id_paciente'), 10),
      nombres: fd.get('nombres'),
      apellidos: fd.get('apellidos'),
      edad: parseInt(fd.get('edad'), 10),
      sexo: fd.get('sexo'),
      peso: peso,
      altura: altura,
      imc: Math.round((peso / (altura * altura)) * 100) / 100,
      presion_sistolica: parseInt(fd.get('presion_sistolica'), 10) || 120,
      presion_diastolica: parseInt(fd.get('presion_diastolica'), 10) || 80,
      frecuencia_cardiaca: parseInt(fd.get('frecuencia_cardiaca'), 10) || 72,
      glucosa: parseFloat(fd.get('glucosa')) || 90,
      colesterol: parseFloat(fd.get('colesterol')) || 180,
      saturacion_oxigeno: parseFloat(fd.get('saturacion_oxigeno')) || 98,
      temperatura: parseFloat(fd.get('temperatura')) || 36.5,
      antecedentes_familiares: fd.get('antecedentes_familiares') === 'true',
      fumador: fd.get('fumador') === 'true',
      consumo_alcohol: fd.get('consumo_alcohol') === 'true',
      actividad_fisica: fd.get('actividad_fisica') || 'Moderada',
      diagnostico_preliminar: fd.get('diagnostico_preliminar') || 'Evaluación inicial',
      riesgo_enfermedad: fd.get('riesgo_enfermedad'),
      fecha_consulta: fd.get('fecha_consulta'),
    };
  }

  // ─── Crear paciente ───
  async function createPatient(e) {
    e.preventDefault();
    var form = e.target;
    var btn = document.getElementById('createPatientBtn');
    var successEl = document.getElementById('patientsSuccess');
    HealthAPI.hideError('patientsError');
    successEl.classList.add('d-none');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Creando...';

    try {
      var payload = formToPayload(form);
      await HealthAPI.apiPostJson('/api/patients/create/', payload);
      form.reset();
      var dateInput = form.querySelector('[name=fecha_consulta]');
      if (dateInput) dateInput.value = new Date().toISOString().split('T')[0];
      successEl.innerHTML = '<i class="bi bi-check-circle me-1"></i>Paciente creado correctamente.';
      successEl.classList.remove('d-none');
      if (addModal) addModal.hide();
      await loadPatients();
    } catch (err) {
      HealthAPI.showError('patientsError', err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-plus-lg me-1"></i>Crear paciente';
    }
  }

  // ─── Actualizar paciente ───
  async function updatePatient(e) {
    e.preventDefault();
    var form = e.target;
    var btn = document.getElementById('editPatientBtn');
    var successEl = document.getElementById('patientsSuccess');
    HealthAPI.hideError('patientsError');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Guardando...';

    try {
      var payload = editFormToPayload(form);
      var id = payload.id_paciente;
      await HealthAPI.apiPostJson('/api/patients/' + id + '/update/', payload);
      if (editModal) editModal.hide();
      successEl.innerHTML = '<i class="bi bi-check-circle me-1"></i>Paciente actualizado correctamente.';
      successEl.classList.remove('d-none');
      await loadPatients();
    } catch (err) {
      HealthAPI.showError('patientsError', err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Guardar cambios';
    }
  }

  // ─── Eliminar paciente ───
  async function deletePatient(id) {
    if (!confirm('¿Eliminar paciente #' + id + '?')) return;
    var successEl = document.getElementById('patientsSuccess');
    HealthAPI.hideError('patientsError');
    try {
      await HealthAPI.apiPostJson('/api/patients/' + id + '/delete/', {});
      successEl.innerHTML = '<i class="bi bi-check-circle me-1"></i>Paciente eliminado correctamente.';
      successEl.classList.remove('d-none');
      await loadPatients();
    } catch (err) {
      HealthAPI.showError('patientsError', err.message);
    }
  }

  // ─── Event Listeners ───
  var debouncedLoad = debounce(loadPatients, 250);
  document.getElementById('patientSearch')?.addEventListener('input', debouncedLoad);
  document.getElementById('refreshPatients')?.addEventListener('click', loadPatients);
  document.getElementById('createPatientForm')?.addEventListener('submit', createPatient);
  document.getElementById('editPatientForm')?.addEventListener('submit', updatePatient);

  // Botón "Nuevo paciente" → modal
  document.getElementById('btnAddPatient')?.addEventListener('click', function () {
    if (!addModal) {
      addModal = new bootstrap.Modal(document.getElementById('addPatientModal'));
    }
    var form = document.getElementById('createPatientForm');
    form.reset();
    var dateInput = form.querySelector('[name=fecha_consulta]');
    if (dateInput) dateInput.value = new Date().toISOString().split('T')[0];
    addModal.show();
  });

  // Fecha por defecto en formulario de creación
  var dateInput = document.querySelector('#createPatientForm [name=fecha_consulta]');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().split('T')[0];
  }

  // Calcular IMC en ambos formularios
  setupImcCalc('createPatientForm', 'createImc');
  setupImcCalc('editPatientForm', 'editImc');

  // Carga inicial
  loadPatients();
})();
