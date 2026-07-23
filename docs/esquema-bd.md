# Esquema de Base de Datos — RAT UCT

> **Motor:** DuckDB ≥ 1.0 | **Archivo:** `rat_uct.db` | **Tablas:** 8
> **Fecha:** Julio 2026

---

## 1. Diagrama Entidad-Relación

```
┌─────────────────────────┐       ┌──────────────────────────┐
│       actividades        │       │         procesos          │
│──────────────────────────│       │──────────────────────────│
│ id (PK)                  │       │ id (PK)                  │
│ actividad_tratamiento    │       │ nombre                   │
│ responsable_tratamiento  │       │ macroproceso             │
│ responsable_rut          │       │ descripcion              │
│ responsable_domicilio    │       │ actividades_ids (INT[])──┼───┐
│ responsable_representante│       └──────────────────────────┘   │
│ dpo_contacto             │                                      │
│ areas_intervienen (VC[])─┼───┐   ┌──────────────────────────┐   │
│ finalidad                │   │   │         areas             │   │
│ descripcion              │   │   │──────────────────────────│   │
│ categoria_titulares(VC[])│   │   │ id (PK)                  │   │
│ categorias_datos (VC[])  │   │   │ nombre (UNIQUE)          │   │
│ datos_sensibles (BOOL)   │   │   │ descripcion              │   │
│ origen_fuente            │   │   │ tipo                     │   │
│ categoria_destinatarios  │   │   └──────────────────────────┘   │
│ base_licitud             │   │                                  │
│ transferencia_internac.  │   │   ┌──────────────────────────┐   │
│ pais_destino             │   │   │       encargados          │   │
│ garantías_transferencia  │   │   │──────────────────────────│   │
│ plazo_conservacion       │   │   │ id (PK)                  │   │
│ justificacion_conservac. │   │   │ nombre (UNIQUE)          │   │
│ medidas_seguridad        │   │   │ rut                      │   │
│ decisiones_automatizadas │   │   │ pais                     │   │
│ requiere_eipd (BOOL) ────┼───┼───┤ servicio                 │   │
│ nivel_riesgo             │   │   │ dpa_generado (BOOL)      │   │
│ score_actividad (INT)    │   │   │ created_at               │   │
│ estado                   │   │   └──────────────────────────┘   │
│ created_at               │   │                                  │
│ updated_at               │   │   ┌──────────────────────────┐   │
└──────────┬───────────────┘   │   │         bitacora          │   │
           │                   │   │──────────────────────────│   │
           │ relacionan por ID │   │ id (PK)                  │   │
           ▼                   │   │ actividad_id (FK)────────┼───┤
┌─────────────────────────┐   │   │ campo_modificado          │   │
│          eipd            │   │   │ valor_anterior            │   │
│──────────────────────────│   │   │ valor_nuevo               │   │
│ id (PK)                  │   │   │ modificado_por            │   │
│ actividad_id (FK) ───────┼───┘   │ modified_at              │   │
│ estado                   │       └──────────────────────────┘   │
│ necesita_eipd (BOOL)     │                                      │
│ motivo_activacion        │       ┌──────────────────────────┐   │
│ riesgo_inherente         │       │    solicitudes_arsop     │   │
│ riesgo_residual          │       │──────────────────────────│   │
│ medidas_propuestas       │       │ id (PK)                  │   │
│ medidas_implementadas    │       │ tipo_derecho             │   │
│ aprobado_por             │       │ solicitante_nombre       │   │
│ fecha_aprobacion (DATE)  │       │ solicitante_email        │   │
│ created_at               │       │ solicitante_rut          │   │
│ updated_at               │       │ descripcion              │   │
└─────────────────────────┘       │ actividad_id (FK) ───────┼───┘
                                  │ fecha_solicitud          │
┌─────────────────────────┐      │ fecha_vencimiento        │
│        brechas           │      │ estado                   │
│──────────────────────────│      │ respuesta                │
│ id (PK)                  │      │ fecha_respuesta          │
│ actividad_id (FK) ───────┼──┐   │ created_at               │
│ titulo                   │  │   │ updated_at               │
│ descripcion              │  │   └──────────────────────────┘
│ fecha_deteccion          │  │
│ fecha_notificacion       │  │
│ plazo_notificacion       │  │
│ severidad                │  │
│ tipo_incidente           │  │
│ datos_afectados          │  │
│ titulares_afectados(INT) │  │
│ medidas_correctivas      │  │
│ notificado_apdp (BOOL)   │  │
│ notificado_titulares(BOOL)│ │
│ estado                   │  │
│ created_at               │  │
│ updated_at               │  │
└──────────────────────────┘  │
                              │
                  ┌───────────┘
                  ▼ Todas las relaciones son opcionales (FK lógica)

Relaciones:
  actividades.id ──< eipd.actividad_id (1:N)
  actividades.id ──< brechas.actividad_id (1:N)
  actividades.id ──< solicitudes_arsop.actividad_id (1:N)
  actividades.id ──< bitacora.actividad_id (1:N)
  actividades.id ──< procesos.actividades_ids (N:M mediante array)
  areas_intervienen ──> areas.nombre (relación lógica por nombre)
```

---

## 2. Tablas y Columnas

### 2.1 `actividades` — Actividades de Tratamiento

**Tabla principal del RAT. 30 columnas. Almacena cada actividad de tratamiento de datos personales que realiza la UCT.**

| # | Columna | Tipo DuckDB | Nulable | Default | Descripción |
|---|---------|-------------|---------|---------|-------------|
| 1 | `id` | `INTEGER` | NO | `nextval('seq_actividades')` | Identificador único |
| 2 | `actividad_tratamiento` | `VARCHAR` | NO | — | Nombre de la actividad |
| 3 | `responsable_tratamiento` | `VARCHAR` | SÍ | `'UCT — Universidad Católica de Temuco'` | Responsable del tratamiento |
| 4 | `responsable_rut` | `VARCHAR` | SÍ | `'XX.XXX.XXX-X'` | RUT del responsable |
| 5 | `responsable_domicilio` | `VARCHAR` | SÍ | `'Manuel Montt 56, Temuco, Chile'` | Domicilio del responsable |
| 6 | `responsable_representante` | `VARCHAR` | SÍ | `'Rector UCT'` | Representante legal |
| 7 | `dpo_contacto` | `VARCHAR` | SÍ | `'dpo@uct.cl'` | Contacto del DPO |
| 8 | `areas_intervienen` | `VARCHAR[]` | SÍ | — | Áreas UCT que participan |
| 9 | `finalidad` | `VARCHAR` | NO | — | Finalidad del tratamiento |
| 10 | `descripcion` | `VARCHAR` | SÍ | — | Descripción detallada |
| 11 | `categoria_titulares` | `VARCHAR[]` | SÍ | — | Categorías de titulares |
| 12 | `categorias_datos` | `VARCHAR[]` | SÍ | — | Categorías de datos tratados |
| 13 | `datos_sensibles` | `BOOLEAN` | SÍ | `false` | ¿Incluye datos sensibles? |
| 14 | `origen_fuente` | `VARCHAR` | SÍ | — | Origen de los datos |
| 15 | `categoria_destinatarios` | `VARCHAR[]` | SÍ | — | Destinatarios de los datos |
| 16 | `base_licitud` | `VARCHAR` | NO | — | Base legal del tratamiento |
| 17 | `transferencia_internacional` | `VARCHAR` | SÍ | `'No aplica'` | Transferencia internacional |
| 18 | `pais_destino` | `VARCHAR` | SÍ | — | País destino de transferencia |
| 19 | `garantías_transferencia` | `VARCHAR` | SÍ | — | Garantías de la transferencia |
| 20 | `plazo_conservacion` | `VARCHAR` | NO | — | Plazo de conservación |
| 21 | `justificacion_conservacion` | `VARCHAR` | SÍ | — | Justificación del plazo |
| 22 | `medidas_seguridad` | `VARCHAR` | SÍ | — | Medidas de seguridad |
| 23 | `decisiones_automatizadas` | `VARCHAR` | SÍ | `'No aplica'` | Decisiones automatizadas |
| 24 | `requiere_eipd` | `BOOLEAN` | SÍ | `false` | ¿Requiere EIPD? |
| 25 | `nivel_riesgo` | `VARCHAR` | SÍ | `'bajo'` | Nivel de riesgo (`bajo`, `medio`, `alto`, `crítico`) |
| 26 | `score_actividad` | `INTEGER` | SÍ | — | Score de cumplimiento (0–100) |
| 27 | `estado` | `VARCHAR` | SÍ | `'activo'` | Estado (`activo`, `revisión`, `archivado`) |
| 28 | `created_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de creación |
| 29 | `updated_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de modificación |

**Campos obligatorios (NOT NULL):** `actividad_tratamiento`, `finalidad`, `base_licitud`, `plazo_conservacion`.

**Campos con lista (`VARCHAR[]`):** `areas_intervienen`, `categoria_titulares`, `categorias_datos`, `categoria_destinatarios`.

**Campos calculados:** `nivel_riesgo` y `score_actividad` se actualizan mediante el motor de evaluación (`POST /api/actividades/{id}/evaluar-riesgo`).

---

### 2.2 `areas` — Catálogo de Áreas UCT

**Catálogo de unidades/facultades/direcciones de la Universidad Católica de Temuco. 12 áreas sembradas por defecto.**

| # | Columna | Tipo DuckDB | Nulable | Default | Descripción |
|---|---------|-------------|---------|---------|-------------|
| 1 | `id` | `INTEGER` | NO | `nextval('seq_actividades')` | Identificador único |
| 2 | `nombre` | `VARCHAR` | NO | — | Nombre del área (UNIQUE) |
| 3 | `descripcion` | `VARCHAR` | SÍ | — | Descripción del área |
| 4 | `tipo` | `VARCHAR` | SÍ | `'unidad'` | Tipo: `facultad`, `dirección`, `unidad`, `carrera` |

---

### 2.3 `procesos` — Macroprocesos Institucionales

**Catálogo de macroprocesos. Se vinculan a actividades mediante un array de IDs.**

| # | Columna | Tipo DuckDB | Nulable | Default | Descripción |
|---|---------|-------------|---------|---------|-------------|
| 1 | `id` | `INTEGER` | NO | `nextval('seq_actividades')` | Identificador único |
| 2 | `nombre` | `VARCHAR` | NO | — | Nombre del proceso |
| 3 | `macroproceso` | `VARCHAR` | SÍ | — | Macroproceso al que pertenece (ej: `Académico`, `Financiero`) |
| 4 | `descripcion` | `VARCHAR` | SÍ | — | Descripción del proceso |
| 5 | `actividades_ids` | `INTEGER[]` | SÍ | — | IDs de actividades RAT asociadas |

---

### 2.4 `encargados` — Destinatarios Externos (Encargados)

**Registro de terceros que reciben datos personales (encargados del tratamiento).**

| # | Columna | Tipo DuckDB | Nulable | Default | Descripción |
|---|---------|-------------|---------|---------|-------------|
| 1 | `id` | `INTEGER` | NO | `nextval('seq_actividades')` | Identificador único |
| 2 | `nombre` | `VARCHAR` | NO | — | Nombre del encargado (UNIQUE) |
| 3 | `rut` | `VARCHAR` | SÍ | — | RUT o identificación |
| 4 | `pais` | `VARCHAR` | SÍ | `'Chile'` | País del encargado |
| 5 | `servicio` | `VARCHAR` | SÍ | — | Servicio contratado |
| 6 | `dpa_generado` | `BOOLEAN` | SÍ | `false` | ¿DPA firmado? |
| 7 | `created_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de registro |

---

### 2.5 `bitacora` — Trazabilidad de Cambios

**Registro de auditoría para cambios en actividades de tratamiento.**

| # | Columna | Tipo DuckDB | Nulable | Default | Descripción |
|---|---------|-------------|---------|---------|-------------|
| 1 | `id` | `INTEGER` | NO | `nextval('seq_actividades')` | Identificador único |
| 2 | `actividad_id` | `INTEGER` | SÍ | — | ID de la actividad modificada |
| 3 | `campo_modificado` | `VARCHAR` | SÍ | — | Nombre del campo cambiado |
| 4 | `valor_anterior` | `VARCHAR` | SÍ | — | Valor previo al cambio |
| 5 | `valor_nuevo` | `VARCHAR` | SÍ | — | Valor después del cambio |
| 6 | `modificado_por` | `VARCHAR` | SÍ | `'sistema'` | Usuario que realizó el cambio |
| 7 | `modified_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha del cambio |

> **Nota:** La bitácora está preparada en el esquema pero a la fecha no se implementa su registro automático. Es un punto de mejora planificado.

---

### 2.6 `eipd` — Evaluación de Impacto en Protección de Datos

**Flujo de 4 pasos para evaluar el impacto de actividades de alto riesgo.**

| # | Columna | Tipo DuckDB | Nulable | Default | Descripción |
|---|---------|-------------|---------|---------|-------------|
| 1 | `id` | `INTEGER` | NO | `nextval('seq_actividades')` | Identificador único |
| 2 | `actividad_id` | `INTEGER` | NO | — | Actividad evaluada (FK) |
| 3 | `estado` | `VARCHAR` | SÍ | `'borrador'` | Estado (`borrador`, `en_curso`, `completada`) |
| 4 | `necesita_eipd` | `BOOLEAN` | SÍ | — | Paso 1: ¿requiere EIPD? |
| 5 | `motivo_activacion` | `VARCHAR` | SÍ | — | Paso 1: motivo de activación |
| 6 | `riesgo_inherente` | `VARCHAR` | SÍ | — | Paso 2: riesgo inherente |
| 7 | `riesgo_residual` | `VARCHAR` | SÍ | — | Paso 2: riesgo residual |
| 8 | `medidas_propuestas` | `VARCHAR` | SÍ | — | Paso 3: medidas propuestas |
| 9 | `medidas_implementadas` | `VARCHAR` | SÍ | — | Paso 3: medidas implementadas |
| 10 | `aprobado_por` | `VARCHAR` | SÍ | — | Paso 4: quién aprueba |
| 11 | `fecha_aprobacion` | `DATE` | SÍ | — | Paso 4: fecha de aprobación |
| 12 | `created_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de creación |
| 13 | `updated_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de modificación |

---

### 2.7 `brechas` — Brechas de Seguridad

**Registro de incidentes de seguridad con alerta de notificación en 72h (Ley 21.719).**

| # | Columna | Tipo DuckDB | Nulable | Default | Descripción |
|---|---------|-------------|---------|---------|-------------|
| 1 | `id` | `INTEGER` | NO | `nextval('seq_actividades')` | Identificador único |
| 2 | `actividad_id` | `INTEGER` | SÍ | — | Actividad relacionada (FK) |
| 3 | `titulo` | `VARCHAR` | NO | — | Título del incidente |
| 4 | `descripcion` | `VARCHAR` | SÍ | — | Descripción detallada |
| 5 | `fecha_deteccion` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Cuándo se detectó |
| 6 | `fecha_notificacion` | `TIMESTAMP` | SÍ | — | Cuándo se notificó |
| 7 | `plazo_notificacion` | `TIMESTAMP` | SÍ | — | Límite de 72h para notificar |
| 8 | `severidad` | `VARCHAR` | SÍ | `'media'` | Severidad (`baja`, `media`, `alta`, `crítica`) |
| 9 | `tipo_incidente` | `VARCHAR` | SÍ | — | Tipo de incidente |
| 10 | `datos_afectados` | `VARCHAR` | SÍ | — | Datos comprometidos |
| 11 | `titulares_afectados` | `INTEGER` | SÍ | — | N° de titulares afectados |
| 12 | `medidas_correctivas` | `VARCHAR` | SÍ | — | Medidas aplicadas |
| 13 | `notificado_apdp` | `BOOLEAN` | SÍ | `false` | ¿Notificado a la APDP? |
| 14 | `notificado_titulares` | `BOOLEAN` | SÍ | `false` | ¿Notificado a titulares? |
| 15 | `estado` | `VARCHAR` | SÍ | `'abierta'` | Estado (`abierta`, `en_investigación`, `cerrada`) |
| 16 | `created_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de creación |
| 17 | `updated_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de modificación |

---

### 2.8 `solicitudes_arsop` — Derechos ARSOP

**Gestión de solicitudes de derechos ARSOP (Acceso, Rectificación, Cancelación, Oposición, Portabilidad). SLA: 30 días.**

| # | Columna | Tipo DuckDB | Nulable | Default | Descripción |
|---|---------|-------------|---------|---------|-------------|
| 1 | `id` | `INTEGER` | NO | `nextval('seq_actividades')` | Identificador único |
| 2 | `tipo_derecho` | `VARCHAR` | NO | — | Derecho solicitado (`acceso`, `rectificación`, `cancelación`, `oposición`, `portabilidad`) |
| 3 | `solicitante_nombre` | `VARCHAR` | SÍ | — | Nombre del solicitante |
| 4 | `solicitante_email` | `VARCHAR` | SÍ | — | Email del solicitante |
| 5 | `solicitante_rut` | `VARCHAR` | SÍ | — | RUT del solicitante |
| 6 | `descripcion` | `VARCHAR` | SÍ | — | Descripción de la solicitud |
| 7 | `actividad_id` | `INTEGER` | SÍ | — | Actividad relacionada (FK) |
| 8 | `fecha_solicitud` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de recepción |
| 9 | `fecha_vencimiento` | `TIMESTAMP` | SÍ | — | Fecha límite (+30 días) |
| 10 | `estado` | `VARCHAR` | SÍ | `'recibida'` | Estado (`recibida`, `en_estudio`, `respondida`, `rechazada`) |
| 11 | `respuesta` | `VARCHAR` | SÍ | — | Contenido de la respuesta |
| 12 | `fecha_respuesta` | `TIMESTAMP` | SÍ | — | Fecha de respuesta |
| 13 | `created_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de creación |
| 14 | `updated_at` | `TIMESTAMP` | SÍ | `CURRENT_TIMESTAMP` | Fecha de modificación |

---

## 3. Tipos de Datos DuckDB Utilizados

| Tipo DuckDB | Uso en RAT UCT |
|-------------|----------------|
| `INTEGER` | IDs, `score_actividad`, `titulares_afectados` |
| `VARCHAR` | Texto: nombres, descripciones, bases legales, estados |
| `BOOLEAN` | Flags: `datos_sensibles`, `requiere_eipd`, `dpa_generado`, `notificado_apdp` |
| `VARCHAR[]` | Listas: `areas_intervienen`, `categoria_titulares`, `categorias_datos`, `categoria_destinatarios` |
| `INTEGER[]` | Lista de IDs: `actividades_ids` (en procesos) |
| `TIMESTAMP` | Fechas con hora: `created_at`, `updated_at`, `fecha_solicitud`, `fecha_deteccion` |
| `DATE` | Fechas sin hora: `fecha_aprobacion` (en EIPD) |

**Particularidades DuckDB:**
- `VARCHAR[]` se maneja como array nativo — las consultas SQL pueden usar `UNNEST()` para expandirlo
- `INTEGER[]` permite relaciones N:M sin tabla pivote
- `BOOLEAN` se comporta como `0`/`1` en contextos numéricos
- `ifnull(col, [])` protege contra arrays NULL en operaciones de desanidado

---

## 4. Migraciones Existentes

### 4.1 Migración: `nivel_riesgo`

```sql
ALTER TABLE actividades ADD COLUMN nivel_riesgo VARCHAR DEFAULT 'bajo';
```

- **Agregada:** Post-despliegue inicial
- **Propósito:** Clasificar actividades por nivel de riesgo (`bajo`, `medio`, `alto`, `crítico`)
- **Mecanismo:** Idempotente (try/except si ya existe)

### 4.2 Migración: `score_actividad`

```sql
ALTER TABLE actividades ADD COLUMN score_actividad INTEGER DEFAULT NULL;
```

- **Agregada:** Post-despliegue inicial
- **Propósito:** Score de cumplimiento (0–100) calculado por el motor de reglas
- **Mecanismo:** Idempotente (try/except si ya existe)

### Política de Migraciones

Las migraciones se ejecutan en cada inicio de la aplicación (`init_db()` en `database.py`), son **idempotentes** y no requieren scripts externos:

```python
def init_db(conn=None):
    # ... CREATE TABLE IF NOT EXISTS ...
    try:
        conn.execute("ALTER TABLE actividades ADD COLUMN nivel_riesgo VARCHAR DEFAULT 'bajo'")
    except Exception:
        pass  # ya existe
    try:
        conn.execute("ALTER TABLE actividades ADD COLUMN score_actividad INTEGER DEFAULT NULL")
    except Exception:
        pass  # ya existe
    return conn
```

---

## 5. Seed Data

### Áreas UCT (12 sembradas por `seed_areas_uct()`)

Ejecutado automáticamente al iniciar la aplicación si la tabla está vacía.

| # | Nombre | Descripción | Tipo |
|---|--------|-------------|------|
| 1 | CERETI | Centro de Recursos para Estudiantes con Discapacidad | `unidad` |
| 2 | Admisión | Dirección de Admisión y Registro Académico | `dirección` |
| 3 | Finanzas | Dirección de Finanzas | `dirección` |
| 4 | TI | Dirección de Tecnologías de Información | `dirección` |
| 5 | RRHH | Dirección de Gestión de Personas | `dirección` |
| 6 | Investigación | Dirección de Investigación | `dirección` |
| 7 | Biblioteca | Sistema de Bibliotecas UCT | `unidad` |
| 8 | Bienestar Estudiantil | Dirección de Asuntos Estudiantiles | `dirección` |
| 9 | Docencia | Vicerrectoría Académica | `vicerrectoría` |
| 10 | Vinculación | Dirección de Vinculación con el Medio | `dirección` |
| 11 | Marketing | Dirección de Comunicaciones y Marketing | `dirección` |
| 12 | Jurídica | Dirección Jurídica | `dirección` |

### Actividad de Ejemplo (vía `seed_matricula.py`)

```sql
INSERT INTO actividades (
    actividad_tratamiento, areas_intervienen, finalidad,
    categoria_titulares, categorias_datos, datos_sensibles,
    base_licitud, plazo_conservacion, medidas_seguridad
) VALUES (
    'Gestión de matrícula',
    ['Admisión', 'TI'],
    'Gestión del proceso de matrícula de estudiantes nuevos y antiguos',
    ['Estudiantes', 'Postulantes'],
    ['Identificación', 'Académicos', 'Socioeconómicos'],
    false,
    'Obligación legal + Consentimiento',
    '10 años desde último acceso',
    'Encriptación en reposo, acceso por roles, MFA'
);
```

### Carga desde Excel (vía `seed.py`)

El script `seed.py` lee la planilla `RAT_UCT_v1_Julio_2026.xlsx` y mapea las columnas del Excel a las columnas de la base de datos:

| Columna Excel | Columna DB |
|---------------|------------|
| ACTIVIDAD DE TRATAMIENTO | `actividad_tratamiento` |
| RESPONSABLE DEL TRATAMIENTO | `responsable_tratamiento` |
| DELEGADO DE PROTECCIÓN DE DATOS (DPO) | `dpo_contacto` |
| ÁREAS QUE INTERVIENEN | `areas_intervienen` |
| FINALIDAD DEL TRATAMIENTO | `finalidad` |
| DESCRIPCIÓN DE LA ACTIVIDAD | `descripcion` |
| CATEGORÍA DE TITULARES | `categoria_titulares` |
| CATEGORÍAS DE DATOS TRATADOS | `categorias_datos` |
| ORIGEN O FUENTE DE LOS DATOS | `origen_fuente` |
| CATEGORÍA DE DESTINATARIOS | `categoria_destinatarios` |
| BASE DE LICITUD | `base_licitud` |
| TRANSFERENCIA INTERNACIONAL | `transferencia_internacional` |
| PLAZO DE CONSERVACIÓN | `plazo_conservacion` |
| MEDIDAS DE SEGURIDAD | `medidas_seguridad` |
| DECISIONES AUTOMATIZADAS | `decisiones_automatizadas` |

---

## 6. Consultas SQL Relevantes

### Estadísticas rápidas

```sql
-- Total de actividades
SELECT count(*) FROM actividades;

-- Distribución por estado
SELECT estado, count(*) as cnt FROM actividades GROUP BY estado ORDER BY cnt DESC;

-- Actividades con datos sensibles
SELECT count(*) FROM actividades WHERE datos_sensibles = true;

-- Matriz de riesgo
SELECT nivel_riesgo, count(*) as cnt FROM actividades GROUP BY nivel_riesgo ORDER BY cnt DESC;

-- Actividades por área (usando UNNEST)
SELECT t.area, count(*) as cnt
FROM (SELECT UNNEST(ifnull(areas_intervienen, [])) as area FROM actividades) t
WHERE t.area IS NOT NULL
GROUP BY t.area ORDER BY cnt DESC;

-- Score promedio por nivel de riesgo
SELECT nivel_riesgo, avg(score_actividad) as score_avg, count(*) as cnt
FROM actividades WHERE nivel_riesgo IS NOT NULL
GROUP BY nivel_riesgo;
```

### Verificar integridad

```sql
-- Actividades con score NULL
SELECT id, actividad_tratamiento FROM actividades WHERE score_actividad IS NULL;

-- Áreas no usadas en ninguna actividad
SELECT a.nombre FROM areas a
WHERE a.nombre NOT IN (
    SELECT DISTINCT UNNEST(ifnull(areas_intervienen, [])) FROM actividades
);
```
