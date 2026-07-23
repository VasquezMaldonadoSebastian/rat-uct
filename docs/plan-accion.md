# Plan de Acción — RAT UCT Profesional

> **Objetivo:** Llevar RAT UCT a un estándar profesional: documentado, testeado, modular, desplegable.
> **Proyecto:** `C:\Users\Sebastian\proyectos\rat-uct`
> **Deploy:** https://rat-uct.onrender.com
> **Inicio:** Julio 2026

---

## 🗓️ Fases

### Fase 1: Base Profesional (corto plazo)

| # | Tarea | Archivos/Área | Tiempo |
|:-:|:------|:-------------|:------:|
| 1.1 | **Modularizar backend** — Separar `main.py` en `routes/` (actividades, eipd, brechas, arsop, reportes, areas, procesos, encargados) + esquema de dependencias | `main.py` → `routes/*.py`, `app.py` | ~60 min |
| 1.2 | **Estructurar frontend** — Crear carpeta `components/` con DataTable, FormModal, StatusBadge, LoadingSpinner. Separar lógica de negocio de páginas | `frontend/src/components/` | ~45 min |
| 1.3 | **Testing base** — Tests unitarios del modelo y base de datos + tests de API con pytest + httpx. CI en GitHub Actions | `tests/`, `.github/workflows/` | ~90 min |
| 1.4 | **Documentación técnica** — `docs/arquitectura.md`, `docs/esquema-bd.md`, `docs/api.md`, `docs/deploy.md` | `docs/` | ~60 min |
| 1.5 | **README profesional** — Badges, screenshot, quickstart, tabla de contenido, sección de tecnologías, contribución | `README.md` | ~30 min |
| 1.6 | **Linting y formato** — Ruff (Python), ESLint (React), pre-commit hooks | `pyproject.toml`, `.pre-commit-config.yaml` | ~20 min |

### Fase 2: Calidad y DevOps (mediano plazo)

| # | Tarea | Tiempo |
|:-:|:------|:------:|
| 2.1 | **Tests de integración** — Tests que cubren flujos completos (crear actividad → evaluar riesgo → asociar EIPD) | ~60 min |
| 2.2 | **API versionada** — Migrar endpoints a `/api/v1/...` manteniendo compatibilidad | ~30 min |
| 2.3 | **Middleware de logging** — Logging estructurado de requests, respuestas y errores | ~20 min |
| 2.4 | **CHANGELOG.md + versionado semántico** | ~15 min |
| 2.5 | **Docker optimizado** — Multi-stage build más eficiente, reducir tamaño de imagen | ~30 min |

### Fase 3: Features desde Fides (mediano-largo plazo)

| # | Tarea | Inspirado en | Tiempo |
|:-:|:------|:------------|:------:|
| 3.1 | **Taxonomía de datos** — Sistema de clasificación basado en fideslang (categorías de datos, finalidades, bases de licitud) con UI de gestión | Fides Taxonomy | ~90 min |
| 3.2 | **Privacy Center** — Frontend público para que titulares externos hagan solicitudes ARSOP sin login | Fides Privacy Center | ~60 min |
| 3.3 | **Data Map visual** — Diagrama Sankey o de flujo que muestre cómo viajan los datos personales entre áreas y destinatarios | Fides Data Map | ~45 min |
| 3.4 | **Dashboard ejecutivo** — Reportes visuales de cumplimiento: brechas por mes, EIPD pendientes, ARSOP por estado | Fides Admin UI | ~45 min |

### Fase 4: Auth y Seguridad (pausado — luego)

| # | Tarea | Estado |
|:-:|:------|:------:|
| 4.1 | Sistema de autenticación JWT | ⏸️ Postergado |
| 4.2 | Roles: admin, encargado, viewer | ⏸️ Postergado |
| 4.3 | Protección de endpoints por rol | ⏸️ Postergado |

---

## 🚀 Orden de arranque sugerido

```
Semana 1:
  Lunes   → 1.1 Modularizar backend
  Martes  → 1.2 Estructurar frontend
  Miércoles → 1.3 Testing base + CI
  Jueves  → 1.4 + 1.5 Documentación
  Viernes → 1.6 Linting + revisión general

Semana 2:
  Fase 2 (DevOps + calidad)

Semana 3:
  Fase 3 (Features Fides)

Posterior:
  Fase 4 (Auth)
```

---

## 📐 Criterios de calidad

| Criterio | Cómo se mide |
|:---------|:-------------|
| Cobertura de tests | >70% en backend |
| Modularidad | main.py < 100 líneas (solo bootstrap) |
| Documentación | docs/ con 4+ archivos + README completo |
| CI verde | GitHub Actions pasa siempre |
| Linting | 0 errores ruff + eslint |
| Deploy | Un solo comando (docker build + push) |

---

*Documento generado el 22 Julio 2026. Pendiente de aprobación antes de ejecutar.*
