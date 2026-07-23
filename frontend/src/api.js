const API = '/api';
const API_V1 = '/api/v1';

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

async function requestV1(url, options = {}) {
  const res = await fetch(`${API_V1}${url}`, {
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
  // ARSOP
  listarArsop() { return request('/arsop'); },
  crearArsop(data) { return request('/arsop', { method: 'POST', body: JSON.stringify(data) }); },
  responderArsop(id, data) { return request(`/arsop/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
  // DPA / Fases
  generarDpa(encargadoId) { return request(`/dpa/generar/${encargadoId}`, { method: 'POST' }); },
  fases() { return request('/fases'); },
  // Taxonomía de Datos (Fides)
  listarCategoriasDatos() { return requestV1('/taxonomia/categorias'); },
  crearCategoriaDato(data) { return requestV1('/taxonomia/categorias', { method: 'POST', body: JSON.stringify(data) }); },
  listarFinalidades() { return requestV1('/taxonomia/finalidades'); },
  crearFinalidad(data) { return requestV1('/taxonomia/finalidades', { method: 'POST', body: JSON.stringify(data) }); },
  listarBasesLicitud() { return requestV1('/taxonomia/bases'); },
  crearBaseLicitud(data) { return requestV1('/taxonomia/bases', { method: 'POST', body: JSON.stringify(data) }); },
  listarAsignaciones(actividadId) { return requestV1(`/taxonomia/asignaciones?actividad_id=${actividadId}`); },
  crearAsignacion(data) { return requestV1('/taxonomia/asignaciones', { method: 'POST', body: JSON.stringify(data) }); },
};

export const apiV1 = {
  // Actividades
  listarActividades(params = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') q.set(k, v); });
    return requestV1(`/actividades?${q}`);
  },
  obtenerActividad(id) { return requestV1(`/actividades/${id}`); },
  crearActividad(data) { return requestV1('/actividades', { method: 'POST', body: JSON.stringify(data) }); },
  actualizarActividad(id, data) { return requestV1(`/actividades/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
  eliminarActividad(id) { return requestV1(`/actividades/${id}`, { method: 'DELETE' }); },
  totalActividades() { return requestV1('/actividades/total'); },

  // Áreas
  listarAreas() { return requestV1('/areas'); },
  crearArea(data) { return requestV1('/areas', { method: 'POST', body: JSON.stringify(data) }); },

  // Procesos
  listarProcesos() { return requestV1('/procesos'); },

  // Encargados
  listarEncargados() { return requestV1('/encargados'); },

  // Reportes
  reporteResumen() { return requestV1('/reportes/resumen'); },
  reporteDpaPendientes() { return requestV1('/reportes/dpa-pendientes'); },
  matrizRiesgo() { return requestV1('/reportes/matriz-riesgo'); },
  reporteScore() { return requestV1('/reportes/score'); },
  evaluarRiesgoTodas() { return requestV1('/actividades/evaluar-riesgo-todas', { method: 'POST' }); },
  // EIPD
  listarEipd(actividadId) { return requestV1(`/actividades/${actividadId}/eipd`); },
  crearEipd(data) { return requestV1('/eipd', { method: 'POST', body: JSON.stringify(data) }); },
  actualizarEipd(id, data) { return requestV1(`/eipd/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
  // Brechas
  listarBrechas(params) { const q = new URLSearchParams(params||{}); return requestV1(`/brechas?${q}`); },
  crearBrecha(data) { return requestV1('/brechas', { method: 'POST', body: JSON.stringify(data) }); },
  // ARSOP
  listarArsop() { return requestV1('/arsop'); },
  crearArsop(data) { return requestV1('/arsop', { method: 'POST', body: JSON.stringify(data) }); },
  responderArsop(id, data) { return requestV1(`/arsop/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
  // DPA / Fases
  generarDpa(encargadoId) { return requestV1(`/dpa/generar/${encargadoId}`, { method: 'POST' }); },
  fases() { return requestV1('/fases'); },
  // Cumplimiento
  reporteCumplimiento() { return requestV1('/reportes/cumplimiento'); },
  // Data Flow
  dataFlow() { return requestV1('/reportes/data-flow'); },
};
