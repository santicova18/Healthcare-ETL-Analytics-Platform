(function () {
  const DEFAULT_VITALS = {
    peso: 70,
    altura: 1.7,
    presion_sistolica: 120,
    presion_diastolica: 80,
    frecuencia_cardiaca: 72,
    glucosa: 90,
    colesterol: 180,
    saturacion_oxigeno: 98,
    temperatura: 36.5,
    antecedentes_familiares: false,
    fumador: false,
    consumo_alcohol: false,
    actividad_fisica: 'Moderada',
  };

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
    const colSpan = canEdit ? 10 : 9;

    if (!results.length) {
      tbody.innerHTML = '<tr><td colspan="' + colSpan + '" class="text-center text-muted py-4">No hay pacientes registrados</td></tr>';
      return;
    }

    tbody.innerHTML = results.map(function (p) {
      return (
        '<tr>' +
          '<td>' + p.id_paciente + '</td>' +
          '<td>' + p.nombres + ' ' + p.apellidos + '</td>' +
          '<td>' + p.edad + '</td>' +
          '<td>' + p.sexo + '</td>' +
          '<td>' + (p.imc ?? '-') + '</td>' +
          '<td>' + riskBadge(p.riesgo_enfermedad) + '</td>' +
          '<td>' + (p.glucosa ?? '-') + '</td>' +
          '<td>' + (p.presion_sistolica ?? '-') + '/' + (p.presion_diastolica ?? '-') + '</td>' +
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
    form.riesgo_enfermedad.value = p.riesgo_enfermedad;
    form.diagnostico_preliminar.value = p.diagnostico_preliminar || 'Evaluación inicial';
    form.fecha_consulta.value = p.fecha_consulta;
    if (!editModal) {
      editModal = new bootstrap.Modal(document.getElementById('editPatientModal'));
    }
    editModal.show();
  }

  async function loadPatients() {
    const loading = document.getElementById('patientsLoading');
    const tableWrap = document.getElementById('patientsTableWrap');
    HealthAPI.hideError('patientsError');
    loading.classList.remove('d-none');
    tableWrap.classList.add('d-none');

    try {
      const data = await HealthAPI.apiGet('/api/patients/');
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
    const peso = DEFAULT_VITALS.peso;
    const altura = DEFAULT_VITALS.altura;
    return Object.assign({}, DEFAULT_VITALS, {
      id_paciente: parseInt(fd.get('id_paciente'), 10),
      nombres: fd.get('nombres'),
      apellidos: fd.get('apellidos'),
      edad: parseInt(fd.get('edad'), 10),
      sexo: fd.get('sexo'),
      riesgo_enfermedad: fd.get('riesgo_enfermedad'),
      diagnostico_preliminar: fd.get('diagnostico_preliminar') || 'Evaluación inicial',
      fecha_consulta: fd.get('fecha_consulta'),
      imc: Math.round((peso / (altura * altura)) * 100) / 100,
    });
  }

  function editFormToPayload(form) {
    const fd = new FormData(form);
    return {
      nombres: fd.get('nombres'),
      apellidos: fd.get('apellidos'),
      edad: parseInt(fd.get('edad'), 10),
      sexo: fd.get('sexo'),
      riesgo_enfermedad: fd.get('riesgo_enfermedad'),
      diagnostico_preliminar: fd.get('diagnostico_preliminar') || 'Evaluación inicial',
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

  document.getElementById('refreshPatients')?.addEventListener('click', loadPatients);
  document.getElementById('createPatientForm')?.addEventListener('submit', createPatient);
  document.getElementById('editPatientForm')?.addEventListener('submit', updatePatient);

  const dateInput = document.querySelector('#createPatientForm [name=fecha_consulta]');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().split('T')[0];
  }

  loadPatients();
})();
