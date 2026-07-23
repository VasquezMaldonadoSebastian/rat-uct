# Documentación de la API — RAT UCT

> **Base URL:** `http://localhost:8000` (desarrollo) / `https://rat-uct.onrender.com` (producción)
> **Formato:** JSON | **Documentación interactiva:** `/docs` (Swagger UI) | `/redoc` (ReDoc)
> **Versión API:** 1.0.0 | **Fecha:** Julio 2026

---

## Resumen

La API REST de RAT UCT expone 30 endpoints organizados en 10 routers modulares, cubriendo todos los aspectos del Registro de Actividades de Tratamiento según la Ley 21.719.

| Router | Endpoints | Ruta base | Propósito |
|--------|-----------|-----------|-----------|
| [Actividades](#1-actividades) | 9 | `/api/actividades` | CRUD + riesgo + EIPD asociadas |
| [Áreas](#2-áreas) | 2 | `/api/areas` | Catálogo de unidades UCT |
| [Procesos](#3-procesos) | 2 | `/api/procesos` | Macroprocesos institucionales |
| [Encargados](#4-encargados) | 2 | `/api/encargados` | Destinatarios externos |
| [Reportes](#5-reportes) | 4 | `/api/reportes` | Agregados y monitoreo |
| [EIPD](#6-eipd) | 3 | `/api/eipd` | Evaluaciones de Impacto |
| [Brechas](#7-brechas) | 3 | `/api/brechas` | Incidentes de seguridad |
| [ARSOP](#8-arsop) | 3 | `/api/arsop` | Derechos de titulares |
| [DPA](#9-dpa) | 1 | `/api/dpa` | Acuerdos de encargo |
| [Fases](#10-fases) | 1 | `/api/fases` | Progreso de implementación |
| **Total** | **30** | | |

---

## Códigos de Error

| Código | Significado | Ejemplo |
|--------|-------------|---------|
| `200 OK` | Operación exitosa | GET, PUT |
| `201 Created` | Recurso creado | POST |
| `204 No Content` | Eliminación exitosa | DELETE |
| `400 Bad Request` | Error de validación (Pydantic) | Campo requerido faltante |
| `404 Not Found` | Recurso no encontrado | ID inexistente |
| `422 Unprocessable Entity` | Error de validación de tipos | Tipo incorrecto en campo |
| `500 Internal Server Error` | Error del servidor | Error en consulta DB |

**Formato de error:**

```json
{
  "detail": "Actividad no encontrada"
}
```

Para errores de validación Pydantic (422):

```json
{
  "detail": [
    {
      "loc": ["body", "finalidad"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 1. Actividades

**Ruta base:** `/api/actividades` | **9 endpoints**

### 1.1 Listar Actividades

`GET /api/actividades`

Lista actividades de tratamiento con filtros opcionales. Paginación con `limit`/`offset`.

**Parámetros (query):**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `search` | `string` | — | Búsqueda textual en nombre, finalidad y descripción (ILIKE) |
| `area` | `string` | — | Filtrar por área que interviene (`array_has`) |
| `base_licitud` | `string` | — | Filtrar por base legal (ILIKE) |
| `estado` | `string` | — | Filtrar por estado (`activo`, `revisión`, `archivado`) |
| `datos_sensibles` | `boolean` | — | Filtrar por datos sensibles (`true`/`false`) |
| `limit` | `integer` | `50` | Máximo de registros (1–500) |
| `offset` | `integer` | `0` | Desplazamiento para paginación |

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/actividades?search=matrícula&estado=activo&limit=5&offset=0"
```

**Ejemplo response (200):**

```json
[
  {
    "id": 1,
    "actividad_tratamiento": "Gestión de matrícula",
    "responsable_tratamiento": "UCT — Universidad Católica de Temuco",
    "responsable_rut": "XX.XXX.XXX-X",
    "responsable_domicilio": "Manuel Montt 56, Temuco, Chile",
    "responsable_representante": "Rector UCT",
    "dpo_contacto": "dpo@uct.cl",
    "areas_intervienen": ["Admisión", "TI"],
    "finalidad": "Gestión del proceso de matrícula de estudiantes nuevos y antiguos",
    "descripcion": "Proceso completo de matrícula que involucra datos personales, académicos y socioeconómicos",
    "categoria_titulares": ["Estudiantes", "Postulantes"],
    "categorias_datos": ["Identificación", "Académicos", "Socioeconómicos"],
    "datos_sensibles": false,
    "origen_fuente": "Titular",
    "categoria_destinatarios": ["MINEDUC", "SENCE"],
    "base_licitud": "Obligación legal + Consentimiento",
    "transferencia_internacional": "No aplica",
    "pais_destino": "",
    "garantías_transferencia": "",
    "plazo_conservacion": "10 años desde último acceso",
    "justificacion_conservacion": "",
    "medidas_seguridad": "Encriptación en reposo, acceso por roles, MFA",
    "decisiones_automatizadas": "No aplica",
    "requiere_eipd": false,
    "nivel_riesgo": "bajo",
    "score_actividad": null,
    "estado": "activo",
    "created_at": "2026-07-20 15:30:00",
    "updated_at": "2026-07-20 15:30:00"
  }
]
```

---

### 1.2 Obtener Actividad por ID

`GET /api/actividades/{actividad_id}`

**Parámetros (path):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `actividad_id` | `integer` | ID de la actividad |

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/actividades/1"
```

**Ejemplo response (200):** Ídem al item individual de listar.

**Ejemplo response (404):**

```json
{
  "detail": "Actividad no encontrada"
}
```

---

### 1.3 Crear Actividad

`POST /api/actividades`

**Cuerpo (JSON):**

```json
{
  "actividad_tratamiento": "Evaluación académica docente",
  "responsable_tratamiento": "UCT — Universidad Católica de Temuco",
  "responsable_rut": "XX.XXX.XXX-X",
  "responsable_domicilio": "Manuel Montt 56, Temuco, Chile",
  "responsable_representante": "Rector UCT",
  "dpo_contacto": "dpo@uct.cl",
  "areas_intervienen": ["Docencia", "TI"],
  "finalidad": "Evaluar el desempeño académico del cuerpo docente",
  "descripcion": "Proceso de evaluación docente que recopila datos de rendimiento académico",
  "categoria_titulares": ["Docentes", "Académicos"],
  "categorias_datos": ["Identificación", "Laborales", "Rendimiento"],
  "datos_sensibles": false,
  "origen_fuente": "Titular",
  "categoria_destinatarios": ["Ministerio de Educación"],
  "base_licitud": "Obligación legal",
  "transferencia_internacional": "No aplica",
  "pais_destino": "",
  "garantías_transferencia": "",
  "plazo_conservacion": "5 años desde última evaluación",
  "justificacion_conservacion": "Respaldo legal y acreditación institucional",
  "medidas_seguridad": "Acceso restringido, logs de auditoría",
  "decisiones_automatizadas": "No aplica",
  "requiere_eipd": false,
  "nivel_riesgo": "bajo",
  "score_actividad": null,
  "estado": "activo"
}
```

**Campos obligatorios:** `actividad_tratamiento`, `finalidad`, `base_licitud`, `plazo_conservacion`.

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/actividades" \
  -H "Content-Type: application/json" \
  -d '{"actividad_tratamiento": "Evaluación académica docente", "finalidad": "Evaluar desempeño académico", "base_licitud": "Obligación legal", "plazo_conservacion": "5 años"}'
```

**Ejemplo response (201):** Recurso creado, incluyendo `id` y `created_at`.

---

### 1.4 Actualizar Actividad

`PUT /api/actividades/{actividad_id}`

Actualización parcial: solo los campos enviados se modifican. Los campos no enviados conservan su valor.

**Ejemplo request:**

```bash
curl -X PUT "http://localhost:8000/api/actividades/1" \
  -H "Content-Type: application/json" \
  -d '{"estado": "revisión", "nivel_riesgo": "medio", "score_actividad": 75}'
```

**Ejemplo response (200):** Recurso actualizado completo.

---

### 1.5 Eliminar Actividad

`DELETE /api/actividades/{actividad_id}`

**Ejemplo request:**

```bash
curl -X DELETE "http://localhost:8000/api/actividades/1" -w "%{http_code}"
```

**Ejemplo response:** `204 No Content` (sin cuerpo).

---

### 1.6 Total Actividades (Estadísticas)

`GET /api/actividades/total`

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/actividades/total"
```

**Ejemplo response (200):**

```json
{
  "total": 15,
  "datos_sensibles": 3,
  "transferencias_internacionales": 1,
  "por_estado": {
    "activo": 12,
    "revisión": 2,
    "archivado": 1
  }
}
```

---

### 1.7 Evaluar Riesgo de una Actividad

`POST /api/actividades/{actividad_id}/evaluar-riesgo`

Evalúa y actualiza `nivel_riesgo` y `score_actividad` de una actividad según el motor de reglas.

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/actividades/1/evaluar-riesgo"
```

**Ejemplo response (200):**

```json
{
  "nivel_riesgo": "bajo",
  "score_actividad": 85,
  "factores": []
}
```

**Ejemplo para actividad con datos sensibles:**

```json
{
  "nivel_riesgo": "alto",
  "score_actividad": 60,
  "factores": ["Datos sensibles"]
}
```

---

### 1.8 Evaluar Riesgo de Todas las Actividades

`POST /api/actividades/evaluar-riesgo-todas`

Evalúa el riesgo de todas las actividades activas.

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/actividades/evaluar-riesgo-todas"
```

**Ejemplo response (200):**

```json
{
  "evaluadas": 12,
  "resultados": [
    {
      "id": 1,
      "actividad": "Gestión de matrícula",
      "nivel_riesgo": "bajo",
      "score_actividad": 85,
      "factores": []
    },
    {
      "id": 2,
      "actividad": "Gestión de salud estudiantil",
      "nivel_riesgo": "crítico",
      "score_actividad": 30,
      "factores": ["Datos sensibles (salud/biométricos/íntimos)"]
    }
  ]
}
```

---

### 1.9 EIPDs por Actividad

`GET /api/actividades/{actividad_id}/eipd`

Obtiene las Evaluaciones de Impacto asociadas a una actividad.

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/actividades/2/eipd"
```

**Ejemplo response (200):**

```json
[
  {
    "id": 1,
    "actividad_id": 2,
    "estado": "completada",
    "necesita_eipd": true,
    "motivo_activacion": "Tratamiento de datos de salud a gran escala",
    "riesgo_inherente": "Alto",
    "riesgo_residual": "Medio",
    "medidas_propuestas": "Seudonimización, minimización de datos, formación del personal",
    "medidas_implementadas": "Seudonimización implementada, formación en curso",
    "aprobado_por": "DPO UCT",
    "fecha_aprobacion": "2026-06-15",
    "created_at": "2026-05-20 10:00:00",
    "updated_at": "2026-06-15 16:30:00"
  }
]
```

---

## 2. Áreas

**Ruta base:** `/api/areas` | **2 endpoints**

### 2.1 Listar Áreas

`GET /api/areas`

**Parámetros (query):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `tipo` | `string` | Filtrar por tipo (`dirección`, `unidad`, `vicerrectoría`, `facultad`) |

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/areas"
curl -X GET "http://localhost:8000/api/areas?tipo=dirección"
```

**Ejemplo response (200):**

```json
[
  {
    "id": 1,
    "nombre": "Admisión",
    "descripcion": "Dirección de Admisión y Registro Académico",
    "tipo": "dirección"
  },
  {
    "id": 2,
    "nombre": "Biblioteca",
    "descripcion": "Sistema de Bibliotecas UCT",
    "tipo": "unidad"
  },
  {
    "id": 3,
    "nombre": "CERETI",
    "descripcion": "Centro de Recursos para Estudiantes con Discapacidad",
    "tipo": "unidad"
  }
]
```

### 2.2 Crear Área

`POST /api/areas`

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/areas" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Internacionalización", "descripcion": "Dirección de Relaciones Internacionales", "tipo": "dirección"}'
```

**Ejemplo response (201):**

```json
{
  "id": 13,
  "nombre": "Internacionalización",
  "descripcion": "Dirección de Relaciones Internacionales",
  "tipo": "dirección"
}
```

---

## 3. Procesos

**Ruta base:** `/api/procesos` | **2 endpoints**

### 3.1 Listar Procesos

`GET /api/procesos`

**Parámetros (query):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `macroproceso` | `string` | Filtrar por macroproceso (`Académico`, `Financiero`, etc.) |

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/procesos"
curl -X GET "http://localhost:8000/api/procesos?macroproceso=Académico"
```

**Ejemplo response (200):**

```json
[
  {
    "id": 1,
    "nombre": "Admisión de estudiantes",
    "macroproceso": "Académico",
    "descripcion": "Proceso de admisión y matrícula de nuevos estudiantes",
    "actividades_ids": [1, 3]
  },
  {
    "id": 2,
    "nombre": "Gestión de remuneraciones",
    "macroproceso": "Gestión de Personas",
    "descripcion": "Proceso de pago y liquidación de remuneraciones",
    "actividades_ids": []
  }
]
```

### 3.2 Crear Proceso

`POST /api/procesos`

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/procesos" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Evaluación docente", "macroproceso": "Académico", "descripcion": "Evaluación de desempeño académico", "actividades_ids": [1]}'
```

**Ejemplo response (201):**

```json
{
  "id": 3,
  "nombre": "Evaluación docente",
  "macroproceso": "Académico",
  "descripcion": "Evaluación de desempeño académico",
  "actividades_ids": [1]
}
```

---

## 4. Encargados

**Ruta base:** `/api/encargados` | **2 endpoints**

### 4.1 Listar Encargados

`GET /api/encargados`

**Parámetros (query):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `pais` | `string` | Filtrar por país |

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/encargados"
curl -X GET "http://localhost:8000/api/encargados?pais=Chile"
```

**Ejemplo response (200):**

```json
[
  {
    "id": 1,
    "nombre": "Google Workspace",
    "rut": "",
    "pais": "Estados Unidos",
    "servicio": "Correo electrónico institucional",
    "dpa_generado": false
  },
  {
    "id": 2,
    "nombre": "SENCE",
    "rut": "XX.XXX.XXX-X",
    "pais": "Chile",
    "servicio": "Prácticas profesionales",
    "dpa_generado": true
  }
]
```

### 4.2 Crear Encargado

`POST /api/encargados`

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/encargados" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "AWS Chile", "pais": "Chile", "servicio": "Infraestructura cloud", "dpa_generado": false}'
```

**Ejemplo response (201):**

```json
{
  "id": 3,
  "nombre": "AWS Chile",
  "rut": "",
  "pais": "Chile",
  "servicio": "Infraestructura cloud",
  "dpa_generado": false
}
```

---

## 5. Reportes

**Ruta base:** `/api/reportes` | **4 endpoints**

### 5.1 Resumen Ejecutivo

`GET /api/reportes/resumen`

Distribución de actividades por base legal, área y categoría de titular.

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/reportes/resumen"
```

**Ejemplo response (200):**

```json
{
  "total_actividades": 15,
  "por_base_legal": {
    "Obligación legal": 8,
    "Consentimiento": 4,
    "Interés legítimo": 3
  },
  "por_area": {
    "Admisión": 5,
    "TI": 4,
    "Docencia": 3,
    "RRHH": 2,
    "Finanzas": 1,
    "Biblioteca": 1
  },
  "por_titular": {
    "Estudiantes": 8,
    "Docentes": 4,
    "Funcionarios": 3,
    "Postulantes": 2,
    "Egresados": 1
  }
}
```

### 5.2 DPA Pendientes

`GET /api/reportes/dpa-pendientes`

Encargados internacionales sin acuerdo DPA firmado.

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/reportes/dpa-pendientes"
```

**Ejemplo response (200):**

```json
[
  {
    "id": 1,
    "nombre": "Google Workspace",
    "rut": "",
    "pais": "Estados Unidos",
    "servicio": "Correo electrónico institucional",
    "dpa_generado": false
  }
]
```

### 5.3 Matriz de Riesgo

`GET /api/reportes/matriz-riesgo`

Distribución de actividades por nivel de riesgo y heatmap por área.

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/reportes/matriz-riesgo"
```

**Ejemplo response (200):**

```json
{
  "por_nivel": {
    "bajo": 8,
    "medio": 4,
    "alto": 2,
    "crítico": 1
  },
  "heatmap": {
    "Admisión": { "crítico": 0, "alto": 0, "medio": 1, "bajo": 4 },
    "TI": { "crítico": 0, "alto": 1, "medio": 1, "bajo": 2 },
    "Docencia": { "crítico": 0, "alto": 0, "medio": 0, "bajo": 3 },
    "RRHH": { "crítico": 0, "alto": 1, "medio": 1, "bajo": 0 },
    "Salud Estudiantil": { "crítico": 1, "alto": 0, "medio": 0, "bajo": 0 }
  }
}
```

### 5.4 Score de Cumplimiento

`GET /api/reportes/score`

Score de cumplimiento global y por área.

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/reportes/score"
```

**Ejemplo response (200):**

```json
{
  "score_global": 82,
  "total_evaluadas": 12,
  "por_area": [
    { "area": "Biblioteca", "score": 95, "actividades": 1 },
    { "area": "Docencia", "score": 90, "actividades": 3 },
    { "area": "Admisión", "score": 85, "actividades": 5 },
    { "area": "TI", "score": 70, "actividades": 4 },
    { "area": "RRHH", "score": 65, "actividades": 2 },
    { "area": "Salud Estudiantil", "score": 30, "actividades": 1 }
  ],
  "por_nivel_riesgo": [
    { "nivel": "bajo", "count": 6, "score_promedio": 92 },
    { "nivel": "medio", "count": 3, "score_promedio": 78 },
    { "nivel": "alto", "count": 2, "score_promedio": 60 },
    { "nivel": "crítico", "count": 1, "score_promedio": 30 }
  ]
}
```

---

## 6. EIPD

**Ruta base:** `/api/eipd` | **3 endpoints**

### 6.1 Listar EIPDs

`GET /api/eipd`

**Parámetros (query):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `actividad_id` | `integer` | Filtrar por actividad |

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/eipd"
curl -X GET "http://localhost:8000/api/eipd?actividad_id=2"
```

**Ejemplo response (200):**

```json
[
  {
    "id": 1,
    "actividad_id": 2,
    "estado": "completada",
    "necesita_eipd": true,
    "motivo_activacion": "Datos de salud a gran escala",
    "riesgo_inherente": "Alto",
    "riesgo_residual": "Medio",
    "medidas_propuestas": "Seudonimización, minimización",
    "medidas_implementadas": "Seudonimización implementada",
    "aprobado_por": "DPO UCT",
    "fecha_aprobacion": "2026-06-15",
    "created_at": "2026-05-20 10:00:00",
    "updated_at": "2026-06-15 16:30:00"
  }
]
```

### 6.2 Crear EIPD

`POST /api/eipd`

Inicia una nueva evaluación de impacto.

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/eipd" \
  -H "Content-Type: application/json" \
  -d '{"actividad_id": 2, "necesita_eipd": true, "motivo_activacion": "Tratamiento de datos biométricos para control de acceso"}'
```

**Ejemplo response (201):**

```json
{
  "id": 2,
  "actividad_id": 2,
  "estado": "borrador",
  "necesita_eipd": true,
  "motivo_activacion": "Tratamiento de datos biométricos para control de acceso",
  "riesgo_inherente": "",
  "riesgo_residual": "",
  "medidas_propuestas": "",
  "medidas_implementadas": "",
  "aprobado_por": "",
  "fecha_aprobacion": "",
  "created_at": "2026-07-23 12:00:00",
  "updated_at": "2026-07-23 12:00:00"
}
```

### 6.3 Actualizar EIPD

`PUT /api/eipd/{eipd_id}`

Actualiza campos de una EIPD (avance por pasos).

**Ejemplo request (Paso 2 — Riesgo):**

```bash
curl -X PUT "http://localhost:8000/api/eipd/2" \
  -H "Content-Type: application/json" \
  -d '{"riesgo_inherente": "Alto", "riesgo_residual": "Bajo"}'
```

**Ejemplo request (Paso 4 — Aprobación):**

```bash
curl -X PUT "http://localhost:8000/api/eipd/2" \
  -H "Content-Type: application/json" \
  -d '{"estado": "completada", "aprobado_por": "DPO UCT", "fecha_aprobacion": "2026-08-01"}'
```

**Ejemplo response (200):**

```json
{
  "id": 2,
  "actividad_id": 2,
  "estado": "completada",
  "necesita_eipd": true,
  "motivo_activacion": "Tratamiento de datos biométricos para control de acceso",
  "riesgo_inherente": "Alto",
  "riesgo_residual": "Bajo",
  "medidas_propuestas": "",
  "medidas_implementadas": "",
  "aprobado_por": "DPO UCT",
  "fecha_aprobacion": "2026-08-01",
  "created_at": "2026-07-23 12:00:00",
  "updated_at": "2026-07-23 12:00:00"
}
```

---

## 7. Brechas

**Ruta base:** `/api/brechas` | **3 endpoints**

### 7.1 Listar Brechas

`GET /api/brechas`

**Parámetros (query):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `estado` | `string` | Filtrar por estado (`abierta`, `en_investigación`, `cerrada`) |
| `severidad` | `string` | Filtrar por severidad (`baja`, `media`, `alta`, `crítica`) |

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/brechas?estado=abierta&severidad=alta"
```

**Ejemplo response (200):**

```json
[
  {
    "id": 1,
    "actividad_id": 1,
    "titulo": "Acceso no autorizado a base de datos de estudiantes",
    "descripcion": "Se detectó acceso desde IP externa sin autenticación MFA a la BD de admisión",
    "fecha_deteccion": "2026-07-22 08:30:00",
    "fecha_notificacion": null,
    "plazo_notificacion": "2026-07-25 08:30:00",
    "severidad": "alta",
    "tipo_incidente": "Acceso no autorizado",
    "datos_afectados": "Nombres, RUT, direcciones, teléfonos",
    "titulares_afectados": 2340,
    "medidas_correctivas": "Revocación de credenciales, rotación de claves",
    "notificado_apdp": false,
    "notificado_titulares": false,
    "estado": "abierta",
    "created_at": "2026-07-22 09:00:00",
    "updated_at": "2026-07-22 09:00:00"
  }
]
```

### 7.2 Crear Brecha

`POST /api/brechas`

Registra una nueva brecha de seguridad.

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/brechas" \
  -H "Content-Type: application/json" \
  -d '{"actividad_id": 1, "titulo": "Intento de phishing a funcionarios", "descripcion": "Campaña de phishing detectada por el equipo de seguridad", "severidad": "media", "tipo_incidente": "Phishing", "datos_afectados": "Credenciales de acceso", "titulares_afectados": 15}'
```

**Ejemplo response (201):**

```json
{
  "id": 2,
  "actividad_id": 1,
  "titulo": "Intento de phishing a funcionarios",
  "descripcion": "Campaña de phishing detectada por el equipo de seguridad",
  "fecha_deteccion": "2026-07-23 12:00:00",
  "fecha_notificacion": null,
  "plazo_notificacion": null,
  "severidad": "media",
  "tipo_incidente": "Phishing",
  "datos_afectados": "Credenciales de acceso",
  "titulares_afectados": 15,
  "medidas_correctivas": "",
  "notificado_apdp": false,
  "notificado_titulares": false,
  "estado": "abierta",
  "created_at": "2026-07-23 12:00:00",
  "updated_at": "2026-07-23 12:00:00"
}
```

### 7.3 Actualizar Brecha

`PUT /api/brechas/{brecha_id}`

Actualiza una brecha (estado, medidas, notificaciones).

**Ejemplo request:**

```bash
curl -X PUT "http://localhost:8000/api/brechas/1" \
  -H "Content-Type: application/json" \
  -d '{"estado": "cerrada", "medidas_correctivas": "Rotación de claves, implementación de MFA obligatorio", "notificado_apdp": true, "notificado_titulares": true, "fecha_notificacion": "2026-07-24 10:00:00"}'
```

---

## 8. ARSOP

**Ruta base:** `/api/arsop` | **3 endpoints**

### 8.1 Listar Solicitudes ARSOP

`GET /api/arsop`

**Parámetros (query):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `estado` | `string` | Filtrar por estado (`recibida`, `en_estudio`, `respondida`, `rechazada`) |

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/arsop"
curl -X GET "http://localhost:8000/api/arsop?estado=recibida"
```

**Ejemplo response (200):**

```json
[
  {
    "id": 1,
    "tipo_derecho": "acceso",
    "solicitante_nombre": "María González",
    "solicitante_email": "maria.gonzalez@ejemplo.cl",
    "solicitante_rut": "12.345.678-9",
    "descripcion": "Solicita acceso a todos los datos personales almacenados en el sistema de admisión",
    "actividad_id": 1,
    "fecha_solicitud": "2026-07-15 09:00:00",
    "fecha_vencimiento": "2026-08-14 09:00:00",
    "estado": "en_estudio",
    "respuesta": "",
    "fecha_respuesta": null,
    "created_at": "2026-07-15 09:00:00",
    "updated_at": "2026-07-15 09:00:00"
  }
]
```

### 8.2 Crear Solicitud ARSOP

`POST /api/arsop`

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/arsop" \
  -H "Content-Type: application/json" \
  -d '{"tipo_derecho": "cancelación", "solicitante_nombre": "Juan Pérez", "solicitante_email": "juan@ejemplo.cl", "solicitante_rut": "23.456.789-0", "descripcion": "Solicita cancelación de datos del sistema de egresados", "actividad_id": 1}'
```

**Ejemplo response (201):**

```json
{
  "id": 2,
  "tipo_derecho": "cancelación",
  "solicitante_nombre": "Juan Pérez",
  "solicitante_email": "juan@ejemplo.cl",
  "solicitante_rut": "23.456.789-0",
  "descripcion": "Solicita cancelación de datos del sistema de egresados",
  "actividad_id": 1,
  "fecha_solicitud": "2026-07-23 12:00:00",
  "fecha_vencimiento": null,
  "estado": "recibida",
  "respuesta": "",
  "fecha_respuesta": null,
  "created_at": "2026-07-23 12:00:00",
  "updated_at": "2026-07-23 12:00:00"
}
```

### 8.3 Responder Solicitud ARSOP

`PUT /api/arsop/{arsop_id}`

Actualiza el estado y registra la respuesta.

**Ejemplo request:**

```bash
curl -X PUT "http://localhost:8000/api/arsop/1" \
  -H "Content-Type: application/json" \
  -d '{"estado": "respondida", "respuesta": "Se adjuntan los datos solicitados en formato PDF. Plazo de atención: 30 días hábiles.", "fecha_respuesta": "2026-08-01"}'
```

---

## 9. DPA

**Ruta base:** `/api/dpa` | **1 endpoint**

### 9.1 Generar DPA

`POST /api/dpa/generar/{encargado_id}`

Genera un Data Processing Agreement para un encargado externo y marca `dpa_generado=true`.

**Ejemplo request:**

```bash
curl -X POST "http://localhost:8000/api/dpa/generar/1"
```

**Ejemplo response (200):**

```json
{
  "mensaje": "DPA generado exitosamente",
  "encargado": "Google Workspace",
  "contenido": "Acuerdo de tratamiento de datos con Google Workspace según Ley 21.719. País: Estados Unidos. Servicio: Correo electrónico institucional."
}
```

**Ejemplo response (404):**

```json
{
  "detail": "Encargado no encontrado"
}
```

---

## 10. Fases

**Ruta base:** `/api/fases` | **1 endpoint**

### 10.1 Obtener Progreso de Fases

`GET /api/fases`

Retorna el progreso de las 12 fases de implementación del modelo Kulvio, evaluado contra datos reales en la base de datos.

**Ejemplo request:**

```bash
curl -X GET "http://localhost:8000/api/fases"
```

**Ejemplo response (200):**

```json
{
  "total": 12,
  "completadas": 5,
  "progreso": 42,
  "fases": [
    { "id": 1,  "nombre": "Configuración Inicial",     "completado": true  },
    { "id": 2,  "nombre": "Diagnóstico",               "completado": true  },
    { "id": 3,  "nombre": "RAT",                       "completado": true  },
    { "id": 4,  "nombre": "Evaluación de Riesgo",       "completado": true  },
    { "id": 5,  "nombre": "EIPD",                      "completado": true  },
    { "id": 6,  "nombre": "Terceros / DPA",             "completado": false },
    { "id": 7,  "nombre": "Consentimientos",            "completado": false },
    { "id": 8,  "nombre": "ARSOP",                     "completado": false },
    { "id": 9,  "nombre": "Brechas",                   "completado": false },
    { "id": 10, "nombre": "Denuncias",                 "completado": false },
    { "id": 11, "nombre": "Documentación",              "completado": false },
    { "id": 12, "nombre": "Monitoreo",                 "completado": false }
  ]
}
```

---

## Resumen Completo de Endpoints

| # | Método | Ruta | Router | Descripción |
|---|--------|------|--------|-------------|
| 1 | GET | `/api/actividades` | Actividades | Listar con filtros y paginación |
| 2 | GET | `/api/actividades/total` | Actividades | Estadísticas rápidas |
| 3 | GET | `/api/actividades/{id}` | Actividades | Obtener por ID |
| 4 | POST | `/api/actividades` | Actividades | Crear |
| 5 | PUT | `/api/actividades/{id}` | Actividades | Actualizar parcial |
| 6 | DELETE | `/api/actividades/{id}` | Actividades | Eliminar |
| 7 | POST | `/api/actividades/{id}/evaluar-riesgo` | Actividades | Evaluar riesgo (individual) |
| 8 | POST | `/api/actividades/evaluar-riesgo-todas` | Actividades | Evaluar riesgo (todas) |
| 9 | GET | `/api/actividades/{id}/eipd` | Actividades | EIPDs por actividad |
| 10 | GET | `/api/areas` | Áreas | Listar catálogo |
| 11 | POST | `/api/areas` | Áreas | Crear área |
| 12 | GET | `/api/procesos` | Procesos | Listar procesos |
| 13 | POST | `/api/procesos` | Procesos | Crear proceso |
| 14 | GET | `/api/encargados` | Encargados | Listar encargados |
| 15 | POST | `/api/encargados` | Encargados | Crear encargado |
| 16 | GET | `/api/reportes/resumen` | Reportes | Resumen ejecutivo |
| 17 | GET | `/api/reportes/dpa-pendientes` | Reportes | DPA pendientes |
| 18 | GET | `/api/reportes/matriz-riesgo` | Reportes | Matriz de riesgo |
| 19 | GET | `/api/reportes/score` | Reportes | Score de cumplimiento |
| 20 | GET | `/api/eipd` | EIPD | Listar evaluaciones |
| 21 | POST | `/api/eipd` | EIPD | Crear evaluación |
| 22 | PUT | `/api/eipd/{id}` | EIPD | Actualizar evaluación |
| 23 | GET | `/api/brechas` | Brechas | Listar brechas |
| 24 | POST | `/api/brechas` | Brechas | Crear brecha |
| 25 | PUT | `/api/brechas/{id}` | Brechas | Actualizar brecha |
| 26 | GET | `/api/arsop` | ARSOP | Listar solicitudes |
| 27 | POST | `/api/arsop` | ARSOP | Crear solicitud |
| 28 | PUT | `/api/arsop/{id}` | ARSOP | Responder solicitud |
| 29 | POST | `/api/dpa/generar/{encargado_id}` | DPA | Generar DPA |
| 30 | GET | `/api/fases` | Fases | Progreso de implementación |
