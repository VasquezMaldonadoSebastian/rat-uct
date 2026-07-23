# memoria_proy.md — RAT UCT

## Objetivo
Construir un **Registro de Actividades de Tratamiento (RAT) institucional** para la **Universidad Católica de Temuco**, como aplicación web completa (DuckDB + FastAPI + React) para gestionar y auditar todos los tratamientos de datos personales, asegurando el cumplimiento de la **Ley 21.719**.

## Estado actual — v1.0.0 🚀
21 julio 2026 — Backend completo con 22 endpoints + Frontend React con 10 páginas + 8 tablas DuckDB.

### Stack implementado
| Capa | Tecnología | Detalle |
|---|---|---|
| Base de datos | DuckDB | `rat_uct.db` (~3.1 MB), 8 tablas |
| Backend API | FastAPI + uvicorn | 22 endpoints REST en `main.py` (804 líneas) |
| Frontend | React 18 + Vite | 10 páginas + Layout ERP en `frontend/src/` |
| Diseño | CSS custom (KIMN UCT) | `App.css` ~500 líneas, paleta pastel ERP/CRM |
| **Deploy** | **Fly.io** | **https://rat-uct.fly.dev** |

---

## Esquema DuckDB — 8 tablas

| # | Tabla | Descripción | Columnas |
|---|---|---|---|
| 1 | **actividades** | Actividades de tratamiento | 30 cols (15 del Excel + riesgo, score, estado, timestamps) |
| 2 | **areas** | Catálogo unidades UCT | 4 cols (id, nombre, descripción, tipo) |
| 3 | **procesos** | Macroprocesos → subprocesos | 5 cols (id, nombre, macroproceso, descripción, actividades_ids) |
| 4 | **encargados** | Destinatarios externos | 6 cols (id, nombre, rut, país, servicio, dpa_generado) |
| 5 | **bitacora** | Trazabilidad de cambios | 6 cols |
| 6 | **eipd** | Evaluaciones de Impacto (EIPD) | 11 cols (4 pasos: diagnóstico → riesgo → medidas → firma) |
| 7 | **brechas** | Incidentes de seguridad | 15 cols (timeline, severidad, notificación 72h) |
| 8 | **solicitudes_arcop** | Derechos ARCOP de titulares | 14 cols (tipo, SLA 30 días, respuesta) |

### Tabla actividades — 30 columnas
```
id, actividad_tratamiento, responsable_tratamiento, responsable_rut,
responsable_domicilio, responsable_representante, dpo_contacto,
areas_intervienen[], finalidad, descripcion, categoria_titulares[],
categorias_datos[], datos_sensibles, origen_fuente, categoria_destinatarios[],
base_licitud, transferencia_internacional, pais_destino, garantías_transferencia,
plazo_conservacion, justificacion_conservacion, medidas_seguridad,
decisiones_automatizadas, requiere_eipd, nivel_riesgo, score_actividad,
estado, created_at, updated_at
```

### Datos sembrados
- **2 actividades** de tratamiento cargadas desde `RAT_UCT_v1_Julio_2026.xlsx`
- **12 áreas UCT**: CERETI, Admisión, Finanzas, TI, RRHH, Investigación, Biblioteca, Bienestar Estudiantil, Docencia, Vinculación, Marketing, Jurídica
- **1 EIPD** de ejemplo
- **1 brecha** de ejemplo
- **1 solicitud ARCOP** de ejemplo

---

## API Endpoints — 22 endpoints

### Actividades (6)
| Ruta | Método | Descripción |
|---|---|---|
| `/api/actividades` | GET | Listar con filtros (search, area, base_licitud, estado, datos_sensibles) |
| `/api/actividades/total` | GET | Estadísticas rápidas (total, sensibles, transferencias, por estado) |
| `/api/actividades/{id}` | GET | Obtener actividad completa |
| `/api/actividades` | POST | Crear actividad |
| `/api/actividades/{id}` | PUT | Actualizar campos (parcial) |
| `/api/actividades/{id}` | DELETE | Eliminar actividad |

### Riesgo y Score (4)
| Ruta | Método | Descripción |
|---|---|---|
| `/api/actividades/{id}/evaluar-riesgo` | POST | Evalúa riesgo de una actividad (reglas automáticas) |
| `/api/actividades/evaluar-riesgo-todas` | POST | Evalúa riesgo de todas las actividades |
| `/api/reportes/matriz-riesgo` | GET | Heatmap: nivel × área con conteo |
| `/api/reportes/score` | GET | Score global 0-100 + por área + por nivel de riesgo |

### EIPD (4)
| Ruta | Método | Descripción |
|---|---|---|
| `/api/eipd` | GET | Listar EIPDs (filtro: ?actividad_id=X) |
| `/api/eipd` | POST | Crear EIPD (4 pasos) |
| `/api/eipd/{id}` | PUT | Actualizar paso de EIPD |
| `/api/actividades/{id}/eipd` | GET | EIPDs de una actividad |

### Brechas (3)
| Ruta | Método | Descripción |
|---|---|---|
| `/api/brechas` | GET | Listar brechas (filtros: ?estado=, ?severidad=) |
| `/api/brechas` | POST | Crear brecha de seguridad |
| `/api/brechas/{id}` | PUT | Actualizar brecha |

### ARCOP (3)
| Ruta | Método | Descripción |
|---|---|---|
| `/api/arcop` | GET | Listar solicitudes (filtro: ?estado=) |
| `/api/arcop` | POST | Crear solicitud ARCOP |
| `/api/arcop/{id}` | PUT | Responder solicitud |

### DPA y Fases (2)
| Ruta | Método | Descripción |
|---|---|---|
| `/api/dpa/generar/{id}` | POST | Generar DPA para un encargado |
| `/api/fases` | GET | Barra de progreso 12 fases |

### Catálogos (6)
| Ruta | Método | Descripción |
|---|---|---|
| `/api/areas` | GET/POST | CRUD áreas UCT |
| `/api/procesos` | GET/POST | CRUD procesos institucionales |
| `/api/encargados` | GET/POST | CRUD encargados externos |
| `/api/reportes/resumen` | GET | Resumen ejecutivo (barras: base legal, área, titular) |
| `/api/reportes/dpa-pendientes` | GET | Encargados sin DPA generado |

---

## Frontend — 10 rutas

| Ruta | Componente | Descripción |
|---|---|---|
| `/` | `Dashboard.jsx` | KPIs, score gauge, heatmap, fases, brechas urgentes, tabla RAT |
| `/actividades` | `ActivitiesList.jsx` | Tabla completa con filtros y búsqueda |
| `/actividades/nueva` | `ActivityForm.jsx` | Formulario 26 campos tipo ficha |
| `/actividades/:id` | `ActivityDetail.jsx` | Vista detalle + pestañas (riesgo, EIPD, brechas, ARCOP) |
| `/actividades/:id/editar` | `ActivityForm.jsx` | Editar actividad (precargado) |
| `/actividades/:id/eipd` | `EipdWizard.jsx` | Wizard 4 pasos: Diagnóstico → Riesgo → Medidas → Firma |
| `/brechas` | `BrechasList.jsx` | Tabla + detalle de incidentes de seguridad |
| `/arcop` | `ArcopList.jsx` | Tabla de solicitudes ARCOP con SLA |
| `/areas` | `AreasList.jsx` | Catálogo agrupado por tipo (dirección, unidad, vicerrectoría) |
| `/reportes` | `Reports.jsx` | Gráficos de barras por base legal, área y titular |

### Componentes compartidos
| Componente | Descripción |
|---|---|
| `Layout.jsx` | Shell ERP: sidebar fijo (250px) + topbar + footer delgado |
| `api.js` | Cliente HTTP unificado para los 22 endpoints |

### Diseño (App.css)
- **Paleta pastel institucional**: azul polvo (#6B9EC2), salvia (#8FAD88), mostaza (#D4A853), terracota (#C27B6B)
- **Fondo**: crema cálido #FAF8F5
- **Sidebar**: beige fijo con secciones, badges de estado, footer
- **Topbar**: logo RAT + breadcrumb + badge Ley 21.719 + avatar
- **KPIs**: cards blancos con borde arena + mini-barra de progreso
- **Tablas**: striped rows alternados + hover celeste
- **Badges**: tonos pastel empolvados (pri, sage, gold, rose, lav)

---

## Estructura del proyecto

```
rat-uct/
├── main.py                   # FastAPI (804 líneas, 22 endpoints)
├── database.py               # Schema DuckDB (8 tablas, 221 líneas)
├── models.py                 # Modelos Pydantic (266 líneas)
├── seed.py                   # Carga datos desde el Excel
├── test_data.json            # Datos de prueba
├── requirements.txt          # Dependencias Python
├── RAT_UCT_v1_Julio_2026.xlsx # Planilla original
├── mockup-rat-uct.html       # Mockup visual KIMN
├── rat_uct.db                # Base de datos DuckDB (~3.1 MB)
├── memoria_proy.md           # Esta memoria
├── .hermes/
│   └── plans/
│       └── 2026-07-20_183000-expansion-riesgo-eipd-arcop-brechas.md
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── dist/                 # Build producción
    ├── public/
    │   ├── favicon.svg
    │   └── icons.svg
    └── src/
        ├── main.jsx          # Entry point React
        ├── App.jsx           # Router (10 rutas)
        ├── App.css           # Estilos globales (~500 líneas)
        ├── index.css         # Reset + variables CSS
        ├── api.js            # Cliente HTTP unificado
        ├── components/
        │   └── Layout.jsx    # Shell ERP (sidebar + topbar + footer)
        └── pages/
            ├── Dashboard.jsx       # Página principal
            ├── ActivitiesList.jsx  # Lista de actividades
            ├── ActivityForm.jsx    # Formulario crear/editar
            ├── ActivityDetail.jsx  # Vista detalle + pestañas
            ├── EipdWizard.jsx      # Wizard EIPD paso a paso
            ├── BrechasList.jsx     # Registro de brechas
            ├── ArcopList.jsx       # Portal ARCOP
            ├── AreasList.jsx       # Catálogo áreas
            └── Reports.jsx         # Reportes y gráficos
```

---

## Motor de riesgo automático

**Reglas implementadas en `evaluar_riesgo_actividad()`** (`main.py:379`):

| Condición | Nivel |
|---|---|
| Datos sensibles (salud, biométricos, racial, ideología, vida sexual) | **crítico** |
| Titulares incluyen NNA (menores de edad) | **crítico** |
| Datos sensibles + transferencia internacional | **crítico** |
| Datos sensibles (sin transferencia) | **alto** |
| Transferencia internacional (sin datos sensibles) | **medio** |
| Decisiones automatizadas | **medio** |
| Requiere EIPD | **medio** |
| Por defecto | **bajo** |

**Score de cumplimiento (0-100):**
- Base: 100 puntos
- Penalización por nivel de riesgo: crítico -40, alto -25, medio -10
- Penalizaciones adicionales: sin medidas (-10), sin plazo (-10), sin justificación (-5), sin origen (-5), transferencia sin garantías (-10)

---

## Fases de implementación (Kulvio-aligned)

| # | Fase | Completado |
|---|---|---|
| 1 | Configuración Inicial | ✅ |
| 2 | Diagnóstico | ✅ |
| 3 | RAT | ✅ |
| 4 | Evaluación de Riesgo | ✅ |
| 5 | EIPD | ✅ |
| 6 | Terceros / DPA | ❌ |
| 7 | Consentimientos | ❌ |
| 8 | ARCOP | ✅ |
| 9 | Brechas | ✅ |
| 10 | Denuncias | ❌ |
| 11 | Documentación | ❌ |
| 12 | Monitoreo | ❌ |

**Progreso: 7/12 (58%)**

---

## Pendientes

- [ ] Cargar más actividades desde la planilla Excel (solo 2 de ~50+)
- [ ] Dashboard dinámico con nivel de cumplimiento real por área
- [ ] Exportar RAT a PDF/CSV para fiscalización APDP
- [ ] Generación real de documento DPA (hoy es placeholder)
- [ ] Módulo de Consentimientos (fase 7)
- [ ] Módulo de Denuncias (fase 10)
- [ ] Autenticación de usuarios UCT (SSO)
- [ ] Auditoría con hash SHA-256
- [ ] Notificaciones automáticas (brechas 72h, ARCOP 30 días)
- [ ] Tests automatizados (pytest no configurado aún)

---

## Referencias

- **Ley 21.719**: https://www.bcn.cl/leychile/navegar?i=1209272
- **Programa Gobierno Datos UCT**: https://gobiernodedatos.uct.cl/
- **KIMN UCT**: https://kimn.uct.cl/
- **registrorat.cl** — RAT online de referencia
- **Kulvio** — Plataforma integral (12 módulos)
- **Excel base**: `RAT_UCT_v1_Julio_2026.xlsx` (15 columnas + instructivo DESCRIPCION)
