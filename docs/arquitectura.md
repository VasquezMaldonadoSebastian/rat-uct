# Arquitectura del Sistema — RAT UCT

> **Proyecto:** Registro de Actividades de Tratamiento — Universidad Católica de Temuco
> **Versión:** 1.0.0 | **Fecha:** Julio 2026 | **Ley:** 21.719 (Protección de Datos Personales)

---

## 1. Stack Tecnológico

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| **Backend** | FastAPI | ≥0.115 | Framework REST asíncrono con validación Pydantic |
| **Base de datos** | DuckDB | ≥1.0 | Base de datos OLAP embebida (sin servidor) |
| **ORM / Validación** | Pydantic v2 | ≥2.0 | Schemas de request/response con tipado estricto |
| **Servidor ASGI** | Uvicorn | ≥0.30 | Servidor ASGI con soporte HTTP/1.1 + WebSocket |
| **Frontend** | React | 19.x | UI interactiva con componentes reutilizables |
| **Bundler** | Vite | 8.x | Build rápido con HMR y proxy de desarrollo |
| **Enrutamiento SPA** | React Router DOM | 6.x | Navegación cliente sin recarga |
| **Iconos** | Lucide React | 1.x | Iconos SVG modulares |
| **Linting Python** | Ruff | — | Formateo y linting (pyproject.toml) |
| **Linting JS** | Oxlint | 1.x | Linting de JavaScript/JSX |
| **Contenedor** | Docker | — | Multi-stage build (frontend + backend) |

### Dependencias Python (requirements.txt)

```txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
duckdb>=1.0.0
pydantic>=2.0.0
openpyxl>=3.1.0
pandas>=2.0.0
```

### Dependencias Frontend (package.json)

```json
{
  "dependencies": {
    "lucide-react": "^1.25.0",
    "react": "^19.2.7",
    "react-dom": "^19.2.7",
    "react-router-dom": "^6.30.4"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^6.0.3",
    "vite": "^8.1.1",
    "oxlint": "^1.71.0"
  }
}
```

---

## 2. Estructura de Directorios (Post-Modularización)

```
rat-uct/
│
├── app.py                     # ★ PUNTO DE ENTRADA — FastAPI app, lifespan, CORS,
│                               #   registro de routers, montaje de estáticos
├── main.py                    # Versión monolítica original (preservada como respaldo)
├── database.py                # Conexión DuckDB, init_db (8 tablas), migraciones,
│                               #   seed de áreas UCT
├── models.py                  # Schemas Pydantic: Create / Update / Out para cada entidad
├── utils.py                   # Helpers: row_to_actividad, fetch_one_dict, fetch_all_dict,
│                               #   evaluar_riesgo_actividad (motor de reglas)
│
├── routes/                    # ★ ROUTERS MODULARES (un archivo por dominio)
│   ├── __init__.py
│   ├── actividades.py         # 9 endpoints  — /api/actividades
│   ├── areas.py               # 2 endpoints  — /api/areas
│   ├── procesos.py            # 2 endpoints  — /api/procesos
│   ├── encargados.py          # 2 endpoints  — /api/encargados
│   ├── reportes.py            # 4 endpoints  — /api/reportes
│   ├── eipd.py                # 3 endpoints  — /api/eipd
│   ├── brechas.py             # 3 endpoints  — /api/brechas
│   ├── arsop.py               # 3 endpoints  — /api/arsop
│   ├── dpa.py                 # 1 endpoint   — /api/dpa
│   └── fases.py               # 1 endpoint   — /api/fases
│
├── frontend/                  # ★ SPA REACT + VITE
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js         # Proxy /api → localhost:8000 en desarrollo
│   └── src/
│       ├── main.jsx           # ReactDOM.createRoot
│       ├── App.jsx            # Router principal (BrowserRouter)
│       ├── App.css            # Estilos globales
│       ├── api.js             # Cliente HTTP (fetch wrapper)
│       ├── pages/             # 9 páginas (Dashboard, ActivitiesList, ...)
│       └── components/        # 7 componentes compartidos (Layout, DataTable, ...)
│
├── static/                    # Build de producción copiado desde frontend/dist
├── rat_uct.db                 # Base de datos DuckDB embebida
│
├── Dockerfile                 # Multi-stage: build frontend + backend Python
├── Dockerfile.hf              # Variante para HuggingFace Spaces
├── requirements.txt
├── pyproject.toml
│
├── seed.py                    # Carga inicial desde Excel RAT_UCT_v1_Julio_2026.xlsx
├── seed_matricula.py          # Registro de ejemplo (Gestión de Matrícula)
├── RAT_UCT_v1_Julio_2026.xlsx # Plantilla fuente con actividades
│
└── docs/
    ├── plan-accion.md
    ├── arquitectura.md        # ← Este documento
    ├── esquema-bd.md          # Documentación de base de datos
    ├── api.md                 # Documentación de API
    └── deploy.md              # Guía de despliegue
```

---

## 3. Diagrama de Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                      │
│                                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │Dashboard  │  │ActivitiesList│  │ ActivityForm│  │  EipdWizard  │  │
│  │(Resumen)  │  │(Tabla+Filter)│  │ (CRUD)     │  │ (4 pasos)   │  │
│  └────┬──────┘  └──────┬───────┘  └─────┬──────┘  └──────┬───────┘  │
│       │                │                │                │          │
│       └────────────────┴──────┬─────────┴────────┬───────┘          │
│                               │                  │                  │
│                        ┌──────▼──────┐    ┌──────▼──────┐          │
│                        │   api.js    │    │ App.css     │          │
│                        │ (fetch/wrap)│    │ (estilos)   │          │
│                        └──────┬──────┘    └─────────────┘          │
│                               │                                     │
│                      fetch('/api/...')                              │
│                    JSON Request/Response                            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  HTTP (localhost:5173 → :8000)
                               │  o desde static/ en producción
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI + Uvicorn)                      │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      app.py (entry point)                     │  │
│  │  ┌──────────┐   ┌──────────────────────┐   ┌──────────────┐   │  │
│  │  │ Lifespan │──>│  CORS Middleware      │──>│ StaticFiles  │   │  │
│  │  │ (init DB)│   │  (allow all origins)  │   │ (SPA fallback)│  │  │
│  │  └──────────┘   └──────────────────────┘   └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                               │                                     │
│         ┌─────────────────────┼─────────────────────┐              │
│         ▼                     ▼                     ▼              │
│  ┌──────────┐   ┌──────────────────┐   ┌──────────────────────┐   │
│  │ Routes/  │   │    models.py     │   │      utils.py        │   │
│  │ *Router  │──>│ (Pydantic val.)  │   │ (row_to_actividad,   │   │
│  │ (10 mod.)│   │ Create/Update/Out│   │  fetch, riesgo eval) │   │
│  └────┬─────┘   └──────────────────┘   └──────────────────────┘   │
│       │                                                        │
│       └────────────── duckdb.connect() ──────────────────────┘  │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                 database.py (DuckDB)                       │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │              rat_uct.db (archivo)                    │  │  │
│  │  │  ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │  │  │
│  │  │  │actividades│ │  areas  │ │procesos │ │encargados│  │  │  │
│  │  │  ├──────────┤ ├─────────┤ ├─────────┤ ├──────────┤  │  │  │
│  │  │  │ bitacora │ │  eipd   │ │ brechas │ │arsop     │  │  │  │
│  │  │  └──────────┘ └─────────┘ └─────────┘ └──────────┘  │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Flujo típico de una solicitud

```
Usuario (navegador)
    │
    ├── 1. GET / (entrega index.html + assets desde static/)
    │         FastAPI → StaticFiles → index.html → React SPA
    │
    ├── 2. React renderiza Dashboard
    │         Componentes → api.js → fetch('/api/reportes/resumen')
    │
    ├── 3. FastAPI recibe request
    │         Routes → database.py → duckdb.query() → JSON response
    │
    └── 4. React actualiza UI con datos
             api.js → JSON → estado React → renderizado
```

### Flujo en desarrollo (con Vite proxy)

```
Navegador → Vite (puerto 5173) → Proxy /api → FastAPI (puerto 8000) → DuckDB
```

### Flujo en producción (estáticos servidos por FastAPI)

```
Navegador → FastAPI (puerto 8080) → StaticFiles (SPA) → React → fetch(/api/*) → FastAPI → DuckDB
```

---

## 4. Patrón de Diseño

### 4.1 APIRouter Modular

Cada dominio de negocio se encapsula en su propio archivo dentro de `routes/`, utilizando `APIRouter` de FastAPI:

```python
# routes/actividades.py
router = APIRouter(prefix="/api/actividades", tags=["Actividades"])

@router.get("")
def listar_actividades(...): ...

@router.post("", status_code=201)
def crear_actividad(...): ...
```

Registro centralizado en `app.py`:

```python
from routes.actividades import router as actividades_router
from routes.areas import router as areas_router
# ...

app.include_router(actividades_router)
app.include_router(areas_router)
# ...
```

**Ventajas:**
- Separación clara de responsabilidades (cada archivo < 250 líneas)
- Facilidad de testing (cada router se prueba independientemente)
- Incorporación de nuevos módulos sin tocar código existente
- Documentación OpenAPI generada automáticamente con tags agrupados

### 4.2 Inyección de Conexión DuckDB

No se usa un ORM ni pool de conexiones tradicional. Cada función de ruta obtiene su propia conexión DuckDB mediante `get_connection()` al inicio y la cierra al finalizar:

```python
def get_connection():
    conn = duckdb.connect(str(DB_PATH))
    conn.execute("SET TimeZone = 'America/Santiago'")
    return conn
```

**Patrón en cada endpoint:**

```python
@router.get("", response_model=list[ActividadOut])
def listar_actividades(...):
    conn = get_connection()
    try:
        result = conn.execute("SELECT * FROM actividades ...")
        rows = result.fetchall()
        return [row_to_actividad(r, cols) for r in rows]
    finally:
        conn.close()
```

**Razonamiento:**
- DuckDB es embebida (no hay servidor de BD), las conexiones son livianas
- Cada request es atómico — no se necesita transacciones multi-endpoint
- Evita el overhead de un pool de conexiones para una base de un solo archivo

### 4.3 Capa de Serialización (utils.py)

Los helpers `row_to_actividad()`, `fetch_one_dict()` y `fetch_all_dict()` convierten las tuplas de DuckDB a diccionarios JSON-serializables, manejando valores por defecto:

| Tipo DuckDB | Valor por defecto si NULL |
|-------------|--------------------------|
| `VARCHAR` | `""` (string vacío) |
| `VARCHAR[]` | `[]` (lista vacía) |
| `BOOLEAN` | `false` |
| `'No aplica'` por defecto | `"No aplica"` (transferencia, decisiones) |
| `estado` | `"activo"` |

### 4.4 Motor de Evaluación de Riesgo

El motor `evaluar_riesgo_actividad()` implementa un sistema jerárquico de reglas:

```
Reglas (orden de precedencia):
1. CRÍTICO ← datos salud/biométricos/íntimos
             O involucra NNA (menores de edad)
             O datos sensibles + transferencia internacional
2. ALTO    ← datos sensibles (sin transferencia)
             O posible gran escala (financiero, etc.)
3. MEDIO   ← transferencia internacional
             O decisiones automatizadas
             O requiere EIPD
4. BAJO    ← por defecto

Score (0-100):
  Base: 100
  -40 si crítico, -25 si alto, -10 si medio, -0 si bajo
  -10 sin medidas_seguridad
  -10 sin plazo_conservacion
  -5  sin justificacion_conservacion
  -5  sin origen_fuente
  -10 sin garantías_transferencia (si aplica)
```

---

## 5. Decisiones Técnicas

### ¿Por qué DuckDB en lugar de PostgreSQL / SQLite?

| Criterio | DuckDB | PostgreSQL | SQLite |
|----------|--------|------------|--------|
| **Setup** | Sin servidor, archivo único | Requiere servidor + config | Sin servidor |
| **Rendimiento analítico** | Excelente (OLAP vectorizado) | Bueno | Bajo en agregaciones |
| **Arrays nativos** | `VARCHAR[]`, `INTEGER[]` | Requiere tabla pivote | No soporta |
| **UNNEST / LATERAL** | Sí | Sí | No |
| **Columnas dinámicas** | ALTER TABLE simple | Migraciones formales | ALTER limitado |
| **Portabilidad** | Un solo archivo `.db` | Backup/restore complejo | Un archivo |
| **Peso** | ~20 MB embebido | ~200 MB+ | ~1 MB |

**Conclusión:** DuckDB es ideal para un RAT institucional porque:
- Las actividades de tratamiento son datos analíticos (pocas escrituras, muchas consultas agregadas)
- Los arrays nativos (`VARCHAR[]`) reflejan naturalmente la estructura multi-área y multi-categoría del RAT
- La portabilidad (un archivo `.db`) facilita copias de seguridad y despliegues
- Sin servidor = sin configuración de red, ideal para un equipo de DPO pequeño

### ¿Por qué modularizar el monolito (main.py → routes/)?

La versión original (`main.py`) contenía 916 líneas con toda la lógica en un solo archivo. La modularización aporta:

1. **Mantenibilidad** — Cada router < 250 líneas, con una responsabilidad clara
2. **Incorporación gradual** — Los módulos se pueden desarrollar y probar independientemente
3. **Legibilidad** — Un nuevo miembro del equipo entiende el flujo en minutos
4. **Git-friendly** — Los cambios en un dominio no generan conflictos en otros
5. **Reutilización** — Los routers pueden importarse en tests unitarios sin cargar toda la app

### ¿Por qué FastAPI?

1. **Validación automática** — Pydantic v2 tipa requests y responses en tiempo real
2. **Documentación OpenAPI** — `/docs` y `/redoc` generadas automáticamente
3. **Rendimiento** — ASGI nativo, comparable con Go/Node.js en benchmarks
4. **Tipado** — Python moderno con type hints, menos bugs en producción
5. **CORS simple** — Middleware integrado para desarrollo con frontend separado

### ¿Por qué React + Vite?

1. **Componentes reutilizables** — Layout, DataTable, StatusBadge compartidos entre páginas
2. **Vite** — Build rápido (< 1s), HMR instantáneo en desarrollo
3. **React Router DOM** — SPA con navegación fluida sin recargas
4. **Lucide React** — Iconos livianos (tree-shakeable) sin dependencias pesadas

### Manejo de Migraciones

Las migraciones de esquema son incrementales e idempotentes:

```python
try:
    conn.execute("ALTER TABLE actividades ADD COLUMN nivel_riesgo VARCHAR DEFAULT 'bajo'")
except Exception:
    pass  # ya existe
```

Esto permite que el sistema se actualice automáticamente al arrancar sin scripts de migración externos. Ideal para equipos pequeños sin DBA dedicado.

---

## 6. Seguridad y Cumplimiento

- **CORS abierto** (`allow_origins=["*"]`) — apropiado para entorno institucional con VPN/Tailscale
- **DPO de contacto** — preconfigurado como `dpo@uct.cl` en cada actividad
- **Zona horaria** — configurada como `America/Santiago` para cumplimiento legal chileno
- **Bitácora** — tabla `bitacora` preparada para auditoría de cambios (pendiente de implementación completa)
- **DPA** — generación de acuerdos de encargo con terceros vía endpoint dedicado

---

## 7. Modelo de Despliegue

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Desarrollador  │────>│  GitHub / Git  │────>│   Render / Fly   │
└─────────────┘     └─────────────┘     └──────┬───────┘
                                               │
                                        ┌──────▼───────┐
                                        │  DuckDB .db   │
                                        │ (persistente) │
                                        └──────────────┘
                                               │
                                        ┌──────▼───────┐
                                        │   Tailscale   │
                                        │ (acceso remoto)│
                                        └──────────────┘
```

Ver guía completa en [`deploy.md`](./deploy.md).
