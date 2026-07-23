# Changelog

## [1.1.0] - 2026-07-23
### Added
- Logging middleware con Request ID y timing
- Docker optimizado con HEALTHCHECK, non-root user, imagenes multi-stage
- Rutas en /api/v1/ (versionado de API)
- Tests de integracion (flujos completos)
- Componentes frontend reutilizables (DataTable, StatusBadge, LoadingSpinner, ErrorAlert, CardMetric, ConfirmDialog, SearchFilter)
- CI/CD con GitHub Actions
- Documentacion tecnica (arquitectura, BD, API, deploy)
- Ruff linting + pre-commit hooks

### Changed
- Migracion de monolitos a modular (main.py 916 lineas -> app.py + routes/*.py + utils.py)
- ARCOP renombrado a ARSOP (Ajuste legal Ley 21.719)
- README actualizado con badges, ToC, quickstart profesional

### Fixed
- ARSOP: respuesta NULL en DB -> ArsopOut espera str (sanitize_row)
- Brechas: notificado_apdp/titulares NULL en DB -> BrechaOut espera bool
- Brechas: tipo_incidente, datos_afectados, medidas_correctivas NULL -> str
- EIPD: fecha_aprobacion DATE -> datetime.date vs Optional[str]

## [1.0.0] - 2026-07-21
### Added
- Lanzamiento inicial RAT UCT
- Backend FastAPI con 22 endpoints (monolito)
- Frontend React con 10 paginas
- DuckDB embebida con 8 tablas
- Motor de evaluacion de riesgo automatico
- Deploy en Render
