/**
 * Helpers fetch para HealthAnalytics IPS (sesión Django + CSRF).
 */
(function (global) {
  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  function getCsrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return (input && input.value) || getCookie('csrftoken') || '';
  }

  async function apiGet(url) {
    const res = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: { Accept: 'application/json' },
    });
    if (res.status === 403) {
      window.location.href = '/api/auth/login/';
      throw new Error('Sesión expirada o sin permisos');
    }
    if (!res.ok) {
      const text = await res.text();
      throw new Error('HTTP ' + res.status + (text ? ': ' + text.slice(0, 120) : ''));
    }
    return res.json();
  }

  async function apiPostJson(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify(data),
    });
    const body = await res.json().catch(() => ({}));
    if (res.status === 403) {
      throw new Error(body.error || 'No autorizado para esta acción');
    }
    if (!res.ok) {
      throw new Error(body.error || 'HTTP ' + res.status);
    }
    return body;
  }

  function showError(elId, message) {
    const el = document.getElementById(elId);
    if (!el) return;
    el.textContent = message;
    el.classList.remove('d-none');
  }

  function hideError(elId) {
    const el = document.getElementById(elId);
    if (el) el.classList.add('d-none');
  }

  global.HealthAPI = {
    getCookie,
    getCsrfToken,
    apiGet,
    apiPostJson,
    showError,
    hideError,
  };
})(window);
