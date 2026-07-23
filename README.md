# RAT UCT — Registro de Actividades de Tratamiento

Aplicación web full-stack para gestionar y auditar los tratamientos de datos personales en la **Universidad Católica de Temuco**, asegurando el cumplimiento de la **Ley 21.719** (vigencia: 1 diciembre 2026).

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

---

## 🚀 Inicio rápido

### Requisitos

- Python 3.10+ con `uv` (instalador de paquetes)
- Node.js 18+ con npm

### Backend

```bash
cd rat-uct/

# Instalar dependencias
uv pip install -r requirements.txt

# (Opcional) Inicializar DB y sembrar áreas
python database.py

# Levantar servidor
python main.py
# → FastAPI en http://localhost:8000
# → OpenAPI docs en http://localhost:8000/docs
```

### Frontend

```bash
cd rat-uct/frontend/

# Instalar dependencias
npm install

# Desarrollo (HMR)
npx vite --host 0.0.0.0 --port 5173

# Producción
npm run build     # → dist/
npx vite preview  # → http://localhost:4173
```

### Acceso remoto (Tailscale)

Si la máquina está en la red Tailscale:
```
http://100.112.230.42:5173   → Frontend
http://100.112.230.42:8000   → Backend API
http://100.112.230.42:8000/docs → OpenAPI docs
```

---

## 📊 API Reference — 22 endpoints

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

### ARCOP — Derechos de Titulares

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/arcop` | Listar solicitudes (`?estado=`) |
| `POST` | `/api/arcop` | Crear solicitud |
| `PUT` | `/api/arcop/{id}` | Responder solicitud |

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

## 📁 Estructura del proyecto

```
rat-uct/
├── main.py                   # FastAPI (804 líneas, 22 endpoints)
├── database.py               # Schema DuckDB (8 tablas, 221 líneas)
├── models.py                 # Modelos Pydantic (266 líneas)
├── seed.py                   # Carga datos desde Excel
├── requirements.txt          # Dependencias Python
├── rat_uct.db                # Base de datos DuckDB
├── RAT_UCT_v1_Julio_2026.xlsx # Planilla original
├── memoria_proy.md           # Memoria completa del proyecto
├── README.md                 # Este archivo
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── dist/                 # Build producción
    ├── public/
    └── src/
        ├── main.jsx
        ├── App.jsx           # Router (10 rutas)
        ├── App.css           # Estilos (~500 líneas)
        ├── api.js            # Cliente HTTP
        ├── components/
        │   └── Layout.jsx    # Shell ERP
        └── pages/
            ├── Dashboard.jsx
            ├── ActivitiesList.jsx
            ├── ActivityForm.jsx
            ├── ActivityDetail.jsx
            ├── EipdWizard.jsx
            ├── BrechasList.jsx
            ├── ArcopList.jsx
            ├── AreasList.jsx
            └── Reports.jsx
```

---

## 🎨 Diseño

- **Identidad**: Sistema KIMN UCT — paleta pastel institucional
- **Layout**: ERP/CRM con sidebar fijo, topbar delgada, footer institucional
- **Colores**: azul polvo (#6B9EC2), salvia (#8FAD88), mostaza (#D4A853), terracota (#C27B6B)
- **Tipografía**: Inter / system-ui
- **Componentes**: Cards blancos con borde arena, badges pastel, tablas striped

---

## ⚖️ Marco legal

- **Ley 21.719** — Protección de Datos Personales (Chile, vigencia dic 2026)
- **Agencia**: APDP (Agencia de Protección de Datos Personales)
- **Multas**: hasta 20.000 UTM (~USD 1.55M)
- **Derechos**: ARCOP (Acceso, Rectificación, Cancelación, Oposición, Portabilidad, Bloqueo)
- **Obligaciones**: RAT, EIPD, consentimiento, notificación brechas (72h), DPO, DPA

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
```

---

## 📝 Licencia

Proyecto institucional UCT. Uso interno.
