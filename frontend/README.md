# RAT UCT — Frontend

Aplicación React + Vite para el Registro de Actividades de Tratamiento de la Universidad Católica de Temuco.

Diseño ERP/CRM con paleta pastel institucional basada en el sistema KIMN UCT.

---

## 🚀 Inicio rápido

```bash
cd rat-uct/frontend/

# Instalar dependencias
npm install

# Desarrollo (HMR en localhost:5173)
npx vite --host 0.0.0.0

# Build producción
npm run build       # → dist/
npx vite preview    # → localhost:4173
```

---

## 🧭 Rutas

| Ruta | Componente | Descripción |
|---|---|---|
| `/` | `Dashboard` | KPIs, score gauge, heatmap, fases, brechas urgentes, tabla RAT |
| `/actividades` | `ActivitiesList` | Tabla completa con filtros y búsqueda textual |
| `/actividades/nueva` | `ActivityForm` | Formulario de creación (26 campos) |
| `/actividades/:id` | `ActivityDetail` | Vista detalle + pestañas (riesgo, EIPD, brechas, ARCOP) |
| `/actividades/:id/editar` | `ActivityForm` | Editar actividad (formulario precargado) |
| `/actividades/:id/eipd` | `EipdWizard` | Wizard EIPD 4 pasos: Diagnóstico → Riesgo → Medidas → Firma |
| `/brechas` | `BrechasList` | Registro de incidentes de seguridad + alerta 72h |
| `/arcop` | `ArcopList` | Solicitudes de derechos ARCOP con SLA 30 días |
| `/areas` | `AreasList` | Catálogo agrupado por tipo (dirección, unidad, vicerrectoría) |
| `/reportes` | `Reports` | Gráficos de barras por base legal, área y titular |

---

## 🏗️ Arquitectura de archivos

```
src/
├── main.jsx              # Entry point — monta <App> en #root
├── App.jsx               # BrowserRouter + rutas
├── App.css               # Estilos globales (~500 líneas)
│                          #   - Variables CSS (paleta, sombras, radios)
│                          #   - Layout (sidebar, topbar, footer)
│                          #   - Componentes (cards, tablas, badges, botones)
│                          #   - Utilidades (margins, flex, grid)
├── index.css             # Reset CSS + normalize
├── api.js                # Cliente HTTP unificado
│                          #   - fetch wrapper con error handling
│                          #   - métodos para los 22 endpoints del backend
│
├── components/
│   └── Layout.jsx        # Shell ERP de la aplicación
│                          #   - Sidebar fijo 250px (logo, nav, secciones, footer)
│                          #   - Topbar (breadcrumb, badge Ley 21.719, avatar)
│                          #   - Footer delgado (Gobierno de Datos UCT)
│
└── pages/
    ├── Dashboard.jsx      # Página principal
    │                       #   - KPIs (total, sensibles, score, brechas)
    │                       #   - Score gauge circular (SVG)
    │                       #   - Matriz de riesgo (heatmap)
    │                       #   - Fases de implementación (barra progreso)
    │                       #   - Brechas urgentes + alerta 72h
    │                       #   - Tabla RAT compacta
    │
    ├── ActivitiesList.jsx # Lista de actividades
    │                       #   - Búsqueda textual + filtros (área, base legal, estado)
    │                       #   - Tabla completa con columnas clave
    │                       #   - Links a detalle, editar, EIPD
    │
    ├── ActivityForm.jsx   # Formulario crear/editar actividad
    │                       #   - Modo dual: crear (vacío) / editar (precargado)
    │                       #   - 26 campos en secciones colapsables
    │                       #   - Arrays para áreas, titulares, categorías
    │
    ├── ActivityDetail.jsx # Vista detalle de una actividad
    │                       #   - Card principal con todos los campos
    │                       #   - Pestañas: Riesgo, EIPD, Brechas, ARCOP
    │                       #   - Acciones: editar, evaluar riesgo, eliminar
    │
    ├── EipdWizard.jsx     # Wizard EIPD paso a paso
    │                       #   - Paso 1: Diagnóstico (motivo activación)
    │                       #   - Paso 2: Riesgo (inherente + residual)
    │                       #   - Paso 3: Medidas (propuestas + implementadas)
    │                       #   - Paso 4: Firma (resumen + aprobación)
    │
    ├── BrechasList.jsx    # Registro de brechas de seguridad
    │                       #   - Tabla con severidad, estado, fechas
    │                       #   - Alerta visual para brechas con 72h vencidas
    │                       #   - Formulario para reportar nueva brecha
    │
    ├── ArcopList.jsx      # Portal ARCOP
    │                       #   - Tabla de solicitudes con SLA (30 días)
    │                       #   - Estados: recibida → en estudio → respondida
    │                       #   - Formulario de respuesta
    │
    ├── AreasList.jsx      # Catálogo de áreas UCT
    │                       #   - Agrupadas por tipo (dirección, unidad, vicerrectoría)
    │                       #   - Cards con descripción
    │
    └── Reports.jsx        # Reportes y gráficos
                            #   - Barras: actividades por base legal
                            #   - Barras: actividades por área
                            #   - Barras: actividades por tipo de titular
```

---

## 🎨 Sistema de diseño

### Paleta de colores (variables en `App.css` + `index.css`)

| Variable | Hex | Uso |
|---|---|---|
| `--bg-primary` | `#FAF8F5` | Fondo general |
| `--bg-sidebar` | `#F5F0E8` | Fondo sidebar |
| `--accent-blue` | `#6B9EC2` | Acciones primarias, links |
| `--accent-sage` | `#8FAD88` | Éxito, completado |
| `--accent-gold` | `#D4A853` | Advertencias |
| `--accent-rose` | `#C27B6B` | Errores, crítico |
| `--border-sand` | `#E8E0D5` | Bordes de cards |
| `--text-primary` | `#2D2A26` | Texto principal |
| `--text-muted` | `#8B8580` | Texto secundario |

### Badges por severidad
- `bajo` → verde salvia claro
- `medio` → mostaza claro
- `alto` → naranja empolvado
- `crítico` → terracota claro

---

## 🔌 Conexión con el backend

El archivo `api.js` centraliza todas las llamadas HTTP. El proxy de Vite (`vite.config.js`) redirige `/api/*` → `http://localhost:8000` en desarrollo.

```js
import { api } from './api';

// Listar actividades con filtros
const acts = await api.listarActividades({ search: 'matrícula', area: 'Admisión' });

// Evaluar riesgo
const riesgo = await api.evaluarRiesgoTodas();

// Crear EIPD
await api.crearEipd({ actividad_id: 1, necesita_eipd: true });
```

---

## 🧪 Desarrollo

```bash
# Dev server con HMR
npx vite --host 0.0.0.0

# Build de producción
npm run build

# Lint (Oxlint configurado)
npx oxlint
```

**Nota:** El proyecto usa JavaScript plano (no TypeScript). Las reglas de lint están en `.oxlintrc.json`.
