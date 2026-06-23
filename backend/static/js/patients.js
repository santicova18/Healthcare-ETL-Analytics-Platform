(function () {
  const canEdit = window.CAN_EDIT_PATIENTS === true;
  const canDelete = window.CAN_DELETE_PATIENTS === true;
  let patientsCache = [];
  let editModal = null;

  function riskBadge(riesgo) {
    const map = {
      'Crítico': 'danger',
      'Alto': 'warning',
      'Medio': 'info',
      'Bajo': 'success',
    };
    const cls = map[riesgo] || 'secondary';
    return '<span class="badge bg-' + cls + '">' + (riesgo || '-') + '</span>';
  }

  function actionButtons(p) {
    if (!canEdit) return '';
    let html = '<button type="button" class="btn btn-sm btn-outline-primary me-1 btn-edit" data-id="' + p.id_paciente + '"><i class="bi bi-pencil"></i></button>';
    if (canDelete) {
      html += '<button type="button" class="btn btn-sm btn-outline-danger btn-delete" data-id="' + p.id_paciente + '"><i class="bi bi-trash"></i></button>';
    }
    return html;
  }

  function renderTable(results) {
    const tbody = document.getElementById('patientsTableBody');
    const countEl = document.getElementById('patientCount');
    if (!tbody) return;

    patientsCache = results;
    countEl.textContent = results.length;

    const baseCols = 22; // id + (nombre/apellidos separadas) + campos clínicos + acciones
    const colSpan = canEdit ? baseCols + 1 : baseCols;

    if (!results.length) {
      tbody.innerHTML = '<tr><td colspan="' + colSpan + '" class="text-center text-muted py-4">No hay pacientes registrados</td></tr>';
      return;
    }

    tbody.innerHTML = results.map(function (p) {
      return (
        '<tr>' +
          '<td>' + p.id_paciente + '</td>' +
          '<td>' + (p.nombres ?? '-') + '</td>' +
          '<td>' + (p.apellidos ?? '-') + '</td>' +
          '<td>' + (p.edad ?? '-') + '</td>' +
          '<td>' + (p.sexo ?? '-') + '</td>' +
          '<td>' + (p.peso ?? '-') + '</td>' +
          '<td>' + (p.altura ?? '-') + '</td>' +
          '<td>' + (p.imc ?? '-') + '</td>' +
          '<td>' + (p.presion_sistolica ?? '-') + '</td>' +
          '<td>' + (p.presion_diastolica ?? '-') + '</td>' +
          '<td>' + (p.frecuencia_cardiaca ?? '-') + '</td>' +
          '<td>' + (p.glucosa ?? '-') + '</td>' +
          '<td>' + (p.colesterol ?? '-') + '</td>' +
          '<td>' + (p.saturacion_oxigeno ?? '-') + '</td>' +
          '<td>' + (p.temperatura ?? '-') + '</td>' +
          '<td>' + (p.antecedentes_familiares ?? '-') + '</td>' +
          '<td>' + (p.fumador ?? '-') + '</td>' +
          '<td>' + (p.consumo_alcohol ?? '-') + '</td>' +
          '<td>' + (p.actividad_fisica ?? '-') + '</td>' +
          '<td>' + (p.diagnostico_preliminar ?? '-') + '</td>' +
          '<td>' + riskBadge(p.riesgo_enfermedad) + '</td>' +
          '<td>' + (p.fecha_consulta ?? '-') + '</td>' +
          (canEdit ? '<td>' + actionButtons(p) + '</td>' : '') +
        '</tr>'
      );
    }).join('');

    tbody.querySelectorAll('.btn-edit').forEach(function (btn) {
      btn.addEventListener('click', function () {
        openEditModal(parseInt(btn.dataset.id, 10));
      });
    });
    tbody.querySelectorAll('.btn-delete').forEach(function (btn) {
      btn.addEventListener('click', function () {
        deletePatient(parseInt(btn.dataset.id, 10));
      });
    });
  }

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

  function openEditModal(id) {
    const p = patientsCache.find(function (x) { return x.id_paciente === id; });
    if (!p) return;
    const form = document.getElementById('editPatientForm');
    if (!form) return;
    document.getElementById('editId').value = p.id_paciente;
    form.nombres.value = p.nombres;
    form.apellidos.value = p.apellidos;
    form.edad.value = p.edad;
    form.sexo.value = p.sexo;
    form.peso.value = p.peso;
    form.altura.value = p.altura;
    form.presion_sistolica.value = p.presion_sistolica;
    form.presion_diastolica.value = p.presion_diastolica;
    form.frecuencia_cardiaca.value = p.frecuencia_cardiaca;
    form.glucosa.value = p.glucosa;
    form.colesterol.value = p.colesterol;
    form.saturacion_oxigeno.value = p.saturacion_oxigeno;
    form.temperatura.value = p.temperatura;
    form.antecedentes_familiares.value = p.antecedentes_familiares ? 'true' : 'false';
    form.fumador.value = p.fumador ? 'true' : 'false';
    form.consumo_alcohol.value = p.consumo_alcohol ? 'true' : 'false';
    form.actividad_fisica.value = p.actividad_fisica || 'Moderada';
    form.riesgo_enfermedad.value = p.riesgo_enfermedad;
    form.diagnostico_preliminar.value = p.diagnostico_preliminar || 'Evaluación inicial';
    form.fecha_consulta.value = p.fecha_consulta;
    var imcEl = document.getElementById('editImc');
    if (imcEl) imcEl.value = p.imc || calcImc(parseFloat(p.peso) || 0, parseFloat(p.altura) || 0);
    if (!editModal) {
      editModal = new bootstrap.Modal(document.getElementById('editPatientModal'));
    }
    editModal.show();
  }

  function getSearchText() {
    const el = document.getElementById('patientSearch');
    return (el && el.value) ? el.value.trim() : '';
  }

  function debounce(fn, waitMs) {
    let t = null;
    return function () {
      const args = arguments;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(null, args); }, waitMs);
    };
  }

  async function loadPatients() {
    const loading = document.getElementById('patientsLoading');
    const tableWrap = document.getElementById('patientsTableWrap');
    HealthAPI.hideError('patientsError');
    loading.classList.remove('d-none');
    tableWrap.classList.add('d-none');

    try {
      const q = getSearchText();
      const qs = q ? ('?q=' + encodeURIComponent(q)) : '';
      const data = await HealthAPI.apiGet('/api/patients/' + qs);
      renderTable(data.results || []);
      loading.classList.add('d-none');
      tableWrap.classList.remove('d-none');
    } catch (err) {
      loading.classList.add('d-none');
      HealthAPI.showError('patientsError', 'Error cargando pacientes: ' + err.message);
    }
  }

  function formToPayload(form) {
    const fd = new FormData(form);
    const peso = parseFloat(fd.get('peso')) || 70;
    const altura = parseFloat(fd.get('altura')) || 1.7;
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
    const fd = new FormData(form);
    const peso = parseFloat(fd.get('peso')) || 70;
    const altura = parseFloat(fd.get('altura')) || 1.7;
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

  async function createPatient(e) {
    e.preventDefault();
    const form = e.target;
    const btn = document.getElementById('createPatientBtn');
    const successEl = document.getElementById('patientsSuccess');
    HealthAPI.hideError('patientsError');
    successEl.classList.add('d-none');
    btn.disabled = true;

    try {
      const payload = formToPayload(form);
      await HealthAPI.apiPostJson('/api/patients/create/', payload);
      form.reset();
      const dateInput = form.querySelector('[name=fecha_consulta]');
      if (dateInput) dateInput.value = new Date().toISOString().split('T')[0];
      successEl.textContent = 'Paciente creado correctamente.';
      successEl.classList.remove('d-none');
      await loadPatients();
    } catch (err) {
      HealthAPI.showError('patientsError', err.message);
    } finally {
      btn.disabled = false;
    }
  }

  async function updatePatient(e) {
    e.preventDefault();
    const form = e.target;
    const btn = document.getElementById('editPatientBtn');
    const successEl = document.getElementById('patientsSuccess');
    HealthAPI.hideError('patientsError');
    btn.disabled = true;

    try {
      const payload = editFormToPayload(form);
      const id = payload.id_paciente;
      await HealthAPI.apiPostJson('/api/patients/' + id + '/update/', payload);
      if (editModal) editModal.hide();
      successEl.textContent = 'Paciente actualizado correctamente.';
      successEl.classList.remove('d-none');
      await loadPatients();
    } catch (err) {
      HealthAPI.showError('patientsError', err.message);
    } finally {
      btn.disabled = false;
    }
  }

  async function deletePatient(id) {
    if (!confirm('¿Eliminar paciente #' + id + '?')) return;
    const successEl = document.getElementById('patientsSuccess');
    HealthAPI.hideError('patientsError');
    try {
      await HealthAPI.apiPostJson('/api/patients/' + id + '/delete/', {});
      successEl.textContent = 'Paciente eliminado correctamente.';
      successEl.classList.remove('d-none');
      await loadPatients();
    } catch (err) {
      HealthAPI.showError('patientsError', err.message);
    }
  }

  const debouncedLoad = debounce(loadPatients, 250);
  document.getElementById('patientSearch')?.addEventListener('input', debouncedLoad);
  document.getElementById('refreshPatients')?.addEventListener('click', loadPatients);
  document.getElementById('createPatientForm')?.addEventListener('submit', createPatient);
  document.getElementById('editPatientForm')?.addEventListener('submit', updatePatient);
  // Cargar lista inicial y coherente con el query actual
  loadPatients();

  const dateInput = document.querySelector('#createPatientForm [name=fecha_consulta]');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().split('T')[0];
  }

  setupImcCalc('createPatientForm', 'createImc');
  setupImcCalc('editPatientForm', 'editImc');

  loadPatients();
})();
