# RAT UCT — Plan de Expansión: Riesgo, EIPD, ARCOP, Brechas y más

> **Para Hermes:** Ejecutar tarea por tarea con subagent-driven-development, sin saltos.
>
> **Goal:** Completar el RAT UCT con los módulos faltantes identificados en herramientas reales (registrorat.cl, Kulvio, Portal ARCOP), comenzando por la matriz de riesgo y avanzando en orden de prioridad.
>
> **Architecture:** Backend FastAPI + DuckDB en `rat-uct/`, Frontend React + Vite en `rat-uct/frontend/`. Cada módulo agrega tablas nuevas al schema existente y endpoints REST + UI.
>
> **Metodología:** 1 tarea = 1 módulo. Backend primero (schema + endpoints), luego frontend (página/nueva sección en Dashboard). No TDD formal (no hay pytest configurado), pero verificar con curl + build cada paso.

---

## Contexto actual

### Lo que YA existe

| Componente | Archivos |
|---|---|
| Schema DuckDB (5 tablas) | `database.py` — actividades, areas, procesos, encargados, bitacora |
| API CRUD (11 endpoints) | `main.py` — /api/actividades, /api/areas, /api/procesos, /api/encargados, /api/reportes |
| Frontend React (6 páginas) | `frontend/src/pages/` — Dashboard, ActivitiesList, ActivityForm, ActivityDetail, AreasList, Reports |
| Diseño KIMN | `App.css`, `components/Layout.jsx` — Nav/Footer UCT oficial |

### Lo que falta (priorizado)

| # | Módulo | Descripción | Ref. |
|---|---|---|---|
| **1** | **Matriz de Riesgo** | Heatmap bajo·medio·alto·crítico por actividad con reglas automáticas | Kulvio Fase 3 |
| **2** | **Score Cumplimiento** | Gauge 0-100 con % por área y brechas detectadas | registrorat.cl |
| **3** | **EIPD Wizard** | Evaluación de Impacto paso a paso | Kulvio Fase 4 |
| **4** | **Registro de Brechas** | Timeline + alerta 72h notificación | Kulvio Fase 8 |
| **5** | **Generación DPA** | Documento por encargado con un clic | registrorat.cl |
| **6** | **Portal ARCOP** | Gestión derechos titulares con SLA | Kulvio Fase 7 |
| **7** | **Fases/Progreso** | Barra de avance tipo "12 fases" | Kulvio |

---

## Tarea 1: Matriz de Riesgo + Score de Cumplimiento

**Objetivo:** Agregar evaluación de riesgo automática por actividad y score global de cumplimiento.

### 1A — Schema: nuevo campo nivel_riesgo y motor de reglas

**Archivos a modificar:**
- `database.py` — agregar columna `nivel_riesgo VARCHAR` a tabla actividades
- `main.py` — nuevo endpoint POST /api/actividades/evaluar-riesgo + campo en crear/actualizar

**Schema del campo:**
```sql
ALTER TABLE actividades ADD COLUMN nivel_riesgo VARCHAR DEFAULT 'bajo';
```

**Reglas de riesgo automáticas (implementar en función `evaluar_riesgo` en main.py):**

| Condición | Nivel |
|---|---|
| categorias_datos contiene "Salud" o "Biométricos" o "Origen racial" o "Ideología" o "Vida sexual" | **crítico** |
| categoria_titulares contiene "Menores (NNA)" | **crítico** |
| datos_sensibles = true + transferencia_internacional != 'No aplica' | **crítico** |
| datos_sensibles = true (sin transferencia) | **alto** |
| transferencia_internacional != 'No aplica' (sin datos sensibles) | **medio** |
| decisiones_automatizadas != 'No aplica' y != '' | **medio** |
| requiere_eipd = true | **medio** |
| Por defecto | **bajo** |

**Endpoints nuevos:**
```
POST /api/actividades/{id}/evaluar-riesgo → { nivel_riesgo, factores, score }
GET  /api/reportes/matriz-riesgo → { critico: N, alto: N, medio: N, bajo: N, por_area: {...} }
GET  /api/reportes/score → { score_global, por_area, brechas }
```

### 1B — Frontend: Heatmap + Score Gauge

**Archivos a modificar:**
- `frontend/src/pages/Dashboard.jsx` — agregar sección matriz de riesgo + score gauge

**Componentes a agregar en Dashboard:**

1. **Score Gauge** — indicador circular grande (SVG) mostrando score 0-100
   - Colores: <40 rojo, 40-70 amarillo, >70 verde
   - Debajo: score numérico + "En progreso" / "Aceptable" / "Óptimo"

2. **Matriz de Riesgo (Heatmap)** — grid heatmap:
   ```
           Vic. Acad   Docencia    Personas   Admisión
   CRÍTICO   ■■          □□          □□         □□
   ALTO      ■■          ■■          □□         □□
   MEDIO     □□          ■■          ■■         ■■
   BAJO      □□          □□          ■■         ■■
   ```
   - Cada celda: número de actividades en ese cruce área×riesgo
   - Color: rojo (crítico) → naranjo (alto) → amarillo (medio) → verde (bajo)

3. **Score por área** — barras horizontales mostrando compliance % por unidad

**Validación:**
```bash
curl -s http://localhost:8000/api/reportes/matriz-riesgo | python -m json.tool
curl -s http://localhost:8000/api/reportes/score | python -m json.tool
curl -s -X POST http://localhost:8000/api/actividades/1/evaluar-riesgo | python -m json.tool
```

---

## Tarea 2: EIPD Wizard

**Objetivo:** Formulario paso a paso para Evaluación de Impacto en Protección de Datos.

### 2A — Schema: nueva tabla eipd

**Archivo:** `database.py`

```sql
CREATE TABLE IF NOT EXISTS eipd (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
    actividad_id INTEGER NOT NULL,
    estado VARCHAR DEFAULT 'borrador',  -- borrador, en_curso, completado, firmado
    -- Paso 1: Identificación
    necesita_eipd BOOLEAN,
    motivo_activacion VARCHAR,  -- datos sensibles, NNA, gran escala, transferencias
    -- Paso 2: Evaluación de riesgo
    riesgo_inherente VARCHAR,  -- bajo, medio, alto, crítico
    riesgo_residual VARCHAR,
    -- Paso 3: Medidas
    medidas_propuestas VARCHAR,
    medidas_implementadas VARCHAR,
    -- Paso 4: Aprobación
    aprobado_por VARCHAR,
    fecha_aprobacion DATE,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2B — Endpoints

```
GET    /api/eipd?actividad_id=X      — listar EIPDs
POST   /api/eipd                      — crear EIPD
PUT    /api/eipd/{id}                 — actualizar paso
GET    /api/eipd/{id}                 — obtener EIPD
POST   /api/eipd/{id}/firmar          — firmar EIPD
```

### 2C — Frontend: EIPDWizard

**Archivo nuevo:** `frontend/src/pages/EipdWizard.jsx`

**Ruta:** `/actividades/:id/eipd`

**Pasos:**
1. **Diagnóstico** — preguntas: ¿tiene datos sensibles? ¿NNA? ¿gran escala?
2. **Riesgo** — clasificación automática + override manual por DPO
3. **Medidas** — checklist + texto libre de medidas
4. **Firma** — resumen + firmar

**Agregar al Layout en rutas App.jsx:**
```jsx
<Route path="/actividades/:id/eipd" element={<EipdWizard />} />
```

---

## Tarea 3: Registro de Brechas

**Objetivo:** Timeline de incidentes con alerta de notificación 72h.

### 3A — Schema: tabla brechas

```sql
CREATE TABLE IF NOT EXISTS brechas (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
    actividad_id INTEGER,
    titulo VARCHAR NOT NULL,
    descripcion VARCHAR,
    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_notificacion TIMESTAMP,
    plazo_notificacion TIMESTAMP,  -- fecha_deteccion + 72h
    severidad VARCHAR DEFAULT 'media',  -- baja, media, alta, crítica
    tipo_incidente VARCHAR,  -- fuga, pérdida, acceso no autorizado, etc.
    datos_afectados VARCHAR,
    titulares_afectados INTEGER,
    medidas_correctivas VARCHAR,
    notificado_apdp BOOLEAN DEFAULT FALSE,
    notificado_titulares BOOLEAN DEFAULT FALSE,
    estado VARCHAR DEFAULT 'abierta',  -- abierta, en_investigación, cerrada
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3B — Endpoints

```
GET    /api/brechas                          — listar
POST   /api/brechas                          — crear
PUT    /api/brechas/{id}                     — actualizar
GET    /api/reportes/brechas-urgentes        — brechas con alerta 72h vencida/próxima
```

### 3C — Frontend

**Sección en Dashboard.jsx** — expandir brechas existentes con timeline y alerta 72h
**Página standalone** `/brechas` — tabla + detalle de cada brecha

---

## Tarea 4: Generación DPA

**Objetivo:** Documento de acuerdo con encargado generable con un clic.

### 4A — Schema: tabla dpa

```sql
CREATE TABLE IF NOT EXISTS dpa (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
    encargado_id INTEGER NOT NULL,
    actividad_id INTEGER,
    estado VARCHAR DEFAULT 'borrador',  -- borrador, pendiente_firma, firmado
    contenido_generado TEXT,  -- texto del DPA
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_firma TIMESTAMP,
    hash_sha256 VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4B — Endpoints

```
POST /api/dpa/generar/{encargado_id}     — generar DPA para un encargado
GET  /api/dpa?encargado_id=X             — listar DPAs
GET  /api/dpa/{id}                       — descargar DPA
```

### 4C — Frontend

**Botón "Generar DPA"** en cards de encargados (vista actividad/detalle)
**Sección** en Dashboard sidebar → "DPAs"

---

## Tarea 5: Portal ARCOP

**Objetivo:** Gestión de derechos ARCOP (Acceso, Rectificación, Cancelación, Oposición, Portabilidad, Bloqueo).

### 5A — Schema: tabla solicitudes_arcop

```sql
CREATE TABLE IF NOT EXISTS solicitudes_arcop (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
    tipo_derecho VARCHAR NOT NULL,  -- acceso, rectificación, cancelación, oposición, portabilidad, bloqueo
    solicitante_nombre VARCHAR,
    solicitante_email VARCHAR,
    solicitante_rut VARCHAR,
    descripcion VARCHAR,
    actividad_id INTEGER,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento TIMESTAMP,  -- fecha_solicitud + 30 días
    estado VARCHAR DEFAULT 'recibida',  -- recibida, en_estudio, respondida, rechazada
    respuesta VARCHAR,
    fecha_respuesta TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5B — Endpoints

```
GET    /api/arcop                     — listar solicitudes
POST   /api/arcop                     — crear solicitud
PUT    /api/arcop/{id}                — responder solicitud
GET    /api/reportes/arcop-vencidas   — solicitudes vencidas
```

### 5C — Frontend

**Página nueva:** `/arcop` — tabla de solicitudes con estados y SLA
**Formulario público:** formulario para que titulares envíen solicitud
**Sidebar → "👤 ARCOP"** ya existe en el mockup, solo hay que enrutarlo

---

## Tarea 6: Fases de Implementación

**Objetivo:** Barra de progreso tipo "12 fases" similar a Kulvio.

### 6A — Lógica

Las 12 fases (inspiradas en Kulvio):
1. Configuración inicial
2. Diagnóstico
3. RAT ← (completado)
4. Evaluación de Riesgo ← (Tarea 1)
5. EIPD ← (Tarea 2)
6. Terceros/DPA ← (Tarea 4)
7. Consentimientos
8. ARCOP ← (Tarea 5)
9. Brechas ← (Tarea 3)
10. Denuncias
11. Documentación
12. Monitoreo

### 6B — Frontend

**Componente:** `frontend/src/components/ProgressBar.jsx`
**Ubicación:** Dashboard arriba de métricas

---

## Orden de ejecución

```
Tarea 1  → Matriz de Riesgo + Score        (prioridad máxima)
Tarea 2  → EIPD Wizard
Tarea 3  → Brechas
Tarea 4  → DPA
Tarea 5  → ARCOP
Tarea 6  → Fases
```

## Archivos que cambiarán

| Archivo | Tareas |
|---|---|
| `rat-uct/database.py` | 1, 2, 3, 4, 5 |
| `rat-uct/main.py` | 1, 2, 3, 4, 5 |
| `rat-uct/frontend/src/pages/Dashboard.jsx` | 1 |
| `rat-uct/frontend/src/pages/EipdWizard.jsx` | 2 (nuevo) |
| `rat-uct/frontend/src/pages/BrechasList.jsx` | 3 (nuevo) |
| `rat-uct/frontend/src/pages/ArcopList.jsx` | 5 (nuevo) |
| `rat-uct/frontend/src/components/ProgressBar.jsx` | 6 (nuevo) |
| `rat-uct/frontend/src/App.jsx` | 2, 3, 5 |
| `rat-uct/frontend/src/App.css` | 1, 6 |
| `rat-uct/memoria_proy.md` | todas |

## Verificación final

```bash
# Backend
curl http://localhost:8000/api/reportes/matriz-riesgo
curl http://localhost:8000/api/reportes/score
curl http://localhost:8000/api/eipd
curl http://localhost:8000/api/brechas
curl http://localhost:8000/api/dpa
curl http://localhost:8000/api/arcop

# Frontend
cd rat-uct/frontend && npm run build  # debe compilar sin errores

# Demo visual
# Abrir http://100.112.230.42:5173 y verificar Dashboard + nuevas secciones
```
