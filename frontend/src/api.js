const API = '/api';

async function request(url, options = {}) {
  const res = await fetch(`${API}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text.slice(0, 200)}`);
  }
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json') && res.status !== 204) {
    return res.json();
  }
  return null;
}

export const api = {
  // Actividades
  listarActividades(params = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') q.set(k, v); });
    return request(`/actividades?${q}`);
  },
  obtenerActividad(id) { return request(`/actividades/${id}`); },
  crearActividad(data) { return request('/actividades', { method: 'POST', body: JSON.stringify(data) }); },
  actualizarActividad(id, data) { return request(`/actividades/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
  eliminarActividad(id) { return request(`/actividades/${id}`, { method: 'DELETE' }); },
  totalActividades() { return request('/actividades/total'); },

  // Áreas
  listarAreas() { return request('/areas'); },
  crearArea(data) { return request('/areas', { method: 'POST', body: JSON.stringify(data) }); },

  // Procesos
  listarProcesos() { return request('/procesos'); },

  // Encargados
  listarEncargados() { return request('/encargados'); },

  // Reportes
  reporteResumen() { return request('/reportes/resumen'); },
  reporteDpaPendientes() { return request('/reportes/dpa-pendientes'); },
  matrizRiesgo() { return request('/reportes/matriz-riesgo'); },
  reporteScore() { return request('/reportes/score'); },
  evaluarRiesgoTodas() { return request('/actividades/evaluar-riesgo-todas', { method: 'POST' }); },
  // EIPD
  listarEipd(actividadId) { return request(`/actividades/${actividadId}/eipd`); },
  crearEipd(data) { return request('/eipd', { method: 'POST', body: JSON.stringify(data) }); },
  actualizarEipd(id, data) { return request(`/eipd/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
  // Brechas
  listarBrechas(params) { const q = new URLSearchParams(params||{}); return request(`/brechas?${q}`); },
  crearBrecha(data) { return request('/brechas', { method: 'POST', body: JSON.stringify(data) }); },
  // ARCOP
  listarArcop() { return request('/arcop'); },
  crearArcop(data) { return request('/arcop', { method: 'POST', body: JSON.stringify(data) }); },
  responderArcop(id, data) { return request(`/arcop/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
  // DPA / Fases
  generarDpa(encargadoId) { return request(`/dpa/generar/${encargadoId}`, { method: 'POST' }); },
  fases() { return request('/fases'); },
};
