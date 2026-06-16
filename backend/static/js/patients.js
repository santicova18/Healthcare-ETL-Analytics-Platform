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

  function renderTable(results) {
    const tbody = document.getElementById('patientsTableBody');
    const countEl = document.getElementById('patientCount');
    if (!tbody) return;

    countEl.textContent = results.length;

    if (!results.length) {
      tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-4">No hay pacientes registrados</td></tr>';
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
        '</tr>'
      );
    }).join('');
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
    const payload = Object.assign({}, DEFAULT_VITALS, {
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
    return payload;
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

  document.getElementById('refreshPatients')?.addEventListener('click', loadPatients);
  document.getElementById('createPatientForm')?.addEventListener('submit', createPatient);

  const dateInput = document.querySelector('[name=fecha_consulta]');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().split('T')[0];
  }

  loadPatients();
})();
