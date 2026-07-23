# 📋 RAT UCT — Registro de Actividades de Tratamiento

<p align="center">
  <img src="https://img.shields.io/badge/status-activo-brightgreen?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/license-institucional%20UCT-blueviolet?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/frontend-React-61DAFB?style=flat-square&logo=react" alt="React">
  <img src="https://img.shields.io/badge/database-DuckDB-FFF000?style=flat-square&logo=duckdb" alt="DuckDB">
</p>

Aplicación web full-stack para gestionar y auditar los tratamientos de datos personales en la **Universidad Católica de Temuco**, asegurando el cumplimiento de la **Ley 21.719** (vigencia: 1 diciembre 2026).

---

## 📑 Tabla de Contenidos

- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Inicio Rápido](#-inicio-rápido)
  - [Requisitos](#requisitos)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Acceso Remoto](#acceso-remoto-tailscale)
- [Captura de Pantalla](#-captura-de-pantalla)
- [API Reference](#-api-reference--22-endpoints)
  - [Actividades de Tratamiento](#actividades-de-tratamiento)
  - [Evaluación de Riesgo](#evaluación-de-riesgo)
  - [EIPD](#eipd--evaluación-de-impacto)
  - [Brechas de Seguridad](#brechas-de-seguridad)
  - [ARSOP](#arsop--derechos-de-titulares)
  - [Otros](#otros)
  - [Catálogos](#catálogos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Diseño](#-diseño)
- [Marco Legal](#️-marco-legal)
- [Desarrollo](#-desarrollo)
- [Licencia](#-licencia)

---

## 🧱 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (React)                   │
│                localhost:5173 (Vite)                 │
│  10 páginas · Layout ERP · Paleta pastel KIMN UCT    │
└─────────────────────┬───────────────────────────────┘
                      │ REST API (JSON)
┌─────────────────────▼───────────────────────────────┐
│                 Backend (FastAPI)                    │
│                localhost:8000 (uvicorn)              │
│       22 endpoints · CORS abierto · OpenAPI /docs    │
└─────────────────────┬───────────────────────────────┘
                      │ DuckDB
┌─────────────────────▼───────────────────────────────┐
│              Base de datos (DuckDB)                  │
│     rat_uct.db · 8 tablas · Embedded (sin servidor)  │
│     SQL analítico · Arrays nativos · Timezone CL     │
└─────────────────────────────────────────────────────┘
```

El flujo de datos es unidireccional: el frontend React consume la API REST expuesta por FastAPI, que a su vez consulta y escribe sobre una base de datos DuckDB embebida. No se requiere servidor de base de datos externo.

---

## 🛠️ Tecnologías

### Backend

| Tecnología | Versión | Propósito |
|---|---|---|
| **FastAPI** | ≥ 0.115 | Framework web asíncrono con validación Pydantic y OpenAPI automático |
| **Uvicorn** | ≥ 0.30 | Servidor ASGI con hot-reload |
| **DuckDB** | ≥ 1.0 | Base de datos embebida analítica (sin servidor) |
| **Pydantic** | ≥ 2.0 | Validación de datos y modelos |
| **OpenPyXL** | ≥ 3.1 | Lectura/escritura de archivos Excel |
| **Pandas** | ≥ 2.0 | Manipulación de datos tabulares |

### Frontend

| Tecnología | Propósito |
|---|---|
| **React 18** | UI declarativa con componentes funcionales |
| **Vite** | Bundler rápido con HMR (Hot Module Replacement) |
| **React Router** | Enrutamiento SPA (10 rutas) |
| **CSS vanilla** | Estilos basados en sistema KIMN UCT |

### Herramientas de Desarrollo

| Herramienta | Uso |
|---|---|
| **Ruff** | Linter y formateador Python (configurado en `pyproject.toml`) |
| **oxlint** | Linter JavaScript/JSX (configurado en `frontend/.oxlintrc.json`) |
| **Pre-commit** | Hooks automatizados de calidad de código |
| **Vite HMR** | Hot-reload del frontend en desarrollo |

---

## 🚀 Inicio Rápido

### Requisitos

| Herramienta | Versión Mínima | Instalación |
|---|---|---|
| **Python** | ≥ 3.11 | [python.org](https://python.org) |
| **uv** | ≥ 0.1 | `pip install uv` o [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| **Node.js** | ≥ 18 | [nodejs.org](https://nodejs.org) |
| **npm** | ≥ 9 | Incluido con Node.js |

### Backend

```bash
# Clonar el repositorio (si aplica)
# cd rat-uct/

# Instalar dependencias con uv
uv pip install -r requirements.txt

# (Opcional) Inicializar base de datos y sembrar áreas por defecto
python database.py

# Iniciar servidor de desarrollo con hot-reload
python main.py
```

El servidor se levanta en:

| Servicio | URL |
|---|---|
| **API REST** | http://localhost:8000 |
| **Documentación OpenAPI** | http://localhost:8000/docs |
| **Esquema OpenAPI (JSON)** | http://localhost:8000/openapi.json |

### Frontend

```bash
# Moverse al directorio del frontend
cd rat-uct/frontend/

# Instalar dependencias
npm install

# Desarrollo con Hot Module Replacement
npx vite --host 0.0.0.0 --port 5173

# Build para producción
npm run build          # → genera en dist/

# Vista previa del build de producción
npx vite preview       # → http://localhost:4173
```

### Acceso Remoto (Tailscale)

Si la máquina está en la red **Tailscale**, se puede acceder desde cualquier dispositivo en la misma red:

```
http://100.112.230.42:5173       → Frontend
http://100.112.230.42:8000       → Backend API
http://100.112.230.42:8000/docs  → OpenAPI Docs
```

---

## 📸 Captura de Pantalla

> ![Screenshot de RAT UCT](docs/screenshot.png)
>
> *— Vista del dashboard principal del sistema. (Agregar captura real en `docs/screenshot.png`)*

---

## 📊 API Reference — 22 Endpoints

Todas las rutas devuelven JSON. La documentación interactiva está disponible en `/docs` una vez levantado el servidor.

### Actividades de Tratamiento

| Método | Ruta | Descripción | Filtros |
|---|---|---|---|
| `GET` | `/api/actividades` | Listar actividades | `?search=&area=&base_licitud=&estado=&datos_sensibles=&limit=&offset=` |
| `GET` | `/api/actividades/total` | Estadísticas rápidas | — |
| `GET` | `/api/actividades/{id}` | Obtener una actividad | — |
| `POST` | `/api/actividades` | Crear actividad | — |
| `PUT` | `/api/actividades/{id}` | Actualizar actividad | — |
| `DELETE` | `/api/actividades/{id}` | Eliminar actividad | — |

### Evaluación de Riesgo

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/actividades/{id}/evaluar-riesgo` | Evalúa el riesgo de una actividad |
| `POST` | `/api/actividades/evaluar-riesgo-todas` | Evalúa el riesgo de todas las actividades |
| `GET` | `/api/reportes/matriz-riesgo` | Matriz de riesgo (heatmap nivel × área) |
| `GET` | `/api/reportes/score` | Score de cumplimiento global + por área |

### EIPD — Evaluación de Impacto

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/eipd` | Listar EIPDs (`?actividad_id=X`) |
| `POST` | `/api/eipd` | Crear EIPD |
| `PUT` | `/api/eipd/{id}` | Actualizar paso de EIPD |
| `GET` | `/api/actividades/{id}/eipd` | EIPDs de una actividad |

### Brechas de Seguridad

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/brechas` | Listar brechas (`?estado=&severidad=`) |
| `POST` | `/api/brechas` | Reportar brecha |
| `PUT` | `/api/brechas/{id}` | Actualizar brecha |

### ARSOP — Derechos de Titulares

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/arsop` | Listar solicitudes (`?estado=`) |
| `POST` | `/api/arsop` | Crear solicitud |
| `PUT` | `/api/arsop/{id}` | Responder solicitud |

### Otros

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/dpa/generar/{encargado_id}` | Generar DPA para un encargado |
| `GET` | `/api/fases` | Barra de progreso 12 fases |
| `GET` | `/api/reportes/resumen` | Resumen ejecutivo |
| `GET` | `/api/reportes/dpa-pendientes` | Encargados sin DPA |

### Catálogos

| Método | Ruta | Descripción |
|---|---|---|
| `GET` `POST` | `/api/areas` | CRUD áreas UCT |
| `GET` `POST` | `/api/procesos` | CRUD procesos |
| `GET` `POST` | `/api/encargados` | CRUD encargados |

---

## 📁 Estructura del Proyecto

```
rat-uct/
├── main.py                   # FastAPI (804 líneas, 22 endpoints)
├── database.py               # Schema DuckDB (8 tablas, 221 líneas)
├── models.py                 # Modelos Pydantic (266 líneas)
├── seed.py                   # Carga datos desde Excel
├── requirements.txt          # Dependencias Python
├── pyproject.toml            # Configuración Ruff y metadatos del proyecto
├── .pre-commit-config.yaml   # Hooks de pre-commit
├── .gitignore                # Exclusiones Git
├── rat_uct.db                # Base de datos DuckDB (local)
├── RAT_UCT_v1_Julio_2026.xlsx # Planilla original de datos
├── memoria_proy.md           # Memoria completa del proyecto
├── README.md                 # Este archivo
└── frontend/
    ├── package.json
    ├── .oxlintrc.json        # Configuración linter JavaScript
    ├── vite.config.js
    ├── index.html
    ├── dist/                 # Build de producción
    ├── public/
    └── src/
        ├── main.jsx
        ├── App.jsx            # Router (10 rutas)
        ├── App.css            # Estilos (~500 líneas)
        ├── api.js             # Cliente HTTP
        ├── components/
        │   └── Layout.jsx     # Shell ERP
        └── pages/
            ├── Dashboard.jsx
            ├── ActivitiesList.jsx
            ├── ActivityForm.jsx
            ├── ActivityDetail.jsx
            ├── EipdWizard.jsx
            ├── BrechasList.jsx
            ├── ArsopList.jsx
            ├── AreasList.jsx
            └── Reports.jsx
```

---

## 🎨 Diseño

- **Identidad visual**: Sistema KIMN UCT — paleta pastel institucional
- **Layout**: ERP/CRM con sidebar fijo, topbar delgada, footer institucional
- **Paleta de colores**:
  - Azul polvo `#6B9EC2`
  - Salvia `#8FAD88`
  - Mostaza `#D4A853`
  - Terracota `#C27B6B`
- **Tipografía**: Inter / system-ui
- **Componentes**: Cards blancos con borde arena, badges pastel, tablas striped

---

## ⚖️ Marco Legal

- **Ley 21.719** — Protección de Datos Personales (Chile, vigencia diciembre 2026)
- **Agencia fiscalizadora**: APDP (Agencia de Protección de Datos Personales)
- **Multas**: Hasta 20.000 UTM (~USD 1.55M)
- **Derechos ARSOP**: Acceso, Rectificación, Cancelación, Oposición, Portabilidad, Bloqueo
- **Obligaciones**: RAT, EIPD, Consentimiento, Notificación de brechas (72h), DPO, DPA

---

## 🔧 Desarrollo

```bash
# Backend con hot-reload
python main.py

# Frontend con HMR
cd frontend && npx vite --host 0.0.0.0

# Verificar build frontend
cd frontend && npm run build

# Seed de datos desde Excel
python seed.py

# Linter Python (Ruff)
ruff check .
ruff format --check .

# Linter Frontend (oxlint)
cd frontend && npx oxlint@latest --config .oxlintrc.json src/
```

---

## 📝 Licencia

Proyecto institucional — **Universidad Católica de Temuco**. Uso interno.
