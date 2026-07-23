"""
RAT UCT — FastAPI Backend
==========================

API RESTful para el Registro de Actividades de Tratamiento de la
Universidad Católica de Temuco, en cumplimiento de la Ley 21.719.

Módulos:
- Actividades CRUD (6 endpoints) con filtros avanzados
- Evaluación de riesgo automática (4 endpoints, motor de reglas)
- EIPD — Evaluación de Impacto (4 endpoints, wizard 4 pasos)
- Brechas de seguridad (3 endpoints, alerta 72h)
- ARCOP — Derechos de titulares (3 endpoints, SLA 30 días)
- DPA — Acuerdos con encargados (1 endpoint)
- Fases de implementación (1 endpoint, barra 12 fases)
- Catálogos: áreas, procesos, encargados (6 endpoints)
- Reportes: resumen, DPA pendientes, matriz de riesgo, score

Total: 22 endpoints REST.

Uso:
    python main.py               # Arranca en http://0.0.0.0:8000
    http://localhost:8000/docs   # Documentación OpenAPI interactiva
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
from contextlib import asynccontextmanager
import os

from database import get_connection, init_db, seed_areas_uct
from models import (
    ActividadCreate, ActividadUpdate, ActividadOut,
    AreaCreate, AreaOut,
    ProcesoCreate, ProcesoOut,
    EncargadoCreate, EncargadoOut,
    EipdCreate, EipdUpdate, EipdOut,
    BrechaCreate, BrechaUpdate, BrechaOut,
    ArcopCreate, ArcopUpdate, ArcopOut,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa DB al arrancar."""
    conn = get_connection()
    init_db(conn)
    seed_areas_uct(conn)
    conn.close()
    yield


app = FastAPI(
    title="RAT UCT — Registro de Actividades de Tratamiento",
    description="API para gestionar el RAT institucional de la Universidad Católica de Temuco (Ley 21.719)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Helpers ────────────────────────────────────────────────────────────────
# Convierte filas DuckDB (tuplas) a diccionarios JSON-serializables con
# valores por defecto para NULLs, booleanos, arrays y strings vacíos.

COLUMNAS_ACTIVIDADES = [
    "id", "actividad_tratamiento", "responsable_tratamiento", "responsable_rut",
    "responsable_domicilio", "responsable_representante", "dpo_contacto",
    "areas_intervienen", "finalidad", "descripcion",
    "categoria_titulares", "categorias_datos", "datos_sensibles",
    "origen_fuente", "categoria_destinatarios", "base_licitud",
    "transferencia_internacional", "pais_destino", "garantías_transferencia",
    "plazo_conservacion", "justificacion_conservacion", "medidas_seguridad",
    "decisiones_automatizadas", "requiere_eipd", "nivel_riesgo",
    "score_actividad", "estado",
    "created_at", "updated_at",
]

# Valores por defecto cuando el campo es NULL
DEFAULT_NULL = {
    "descripcion": "", "origen_fuente": "", "medidas_seguridad": "",
    "justificacion_conservacion": "", "responsable_rut": "",
    "responsable_domicilio": "", "responsable_representante": "",
    "pais_destino": "", "garantías_transferencia": "",
}
DEFAULT_EMPTY_LIST = {"areas_intervienen", "categoria_titulares", "categorias_datos", "categoria_destinatarios"}
DEFAULT_FALSE = {"datos_sensibles", "requiere_eipd"}
DEFAULT_NO_APLICA = {"transferencia_internacional", "decisiones_automatizadas"}


def row_to_actividad(row, columns=None):
    """Convierte una fila DuckDB (tupla) a dict serializable."""
    if row is None:
        return None
    if columns is None:
        columns = COLUMNAS_ACTIVIDADES
    d = {}
    for i, k in enumerate(columns):
        val = row[i] if i < len(row) else None
        if isinstance(val, list):
            d[k] = list(val)
        elif val is None:
            if k in DEFAULT_NULL:
                d[k] = ""
            elif k in DEFAULT_EMPTY_LIST:
                d[k] = []
            elif k in DEFAULT_FALSE:
                d[k] = False
            elif k in DEFAULT_NO_APLICA:
                d[k] = "No aplica"
            elif k == "estado":
                d[k] = "activo"
            else:
                d[k] = val
        else:
            d[k] = val
    return d


def fetch_one_dict(conn, sql, params=None, columns=None):
    """Ejecuta SELECT y retorna un dict."""
    if params:
        result = conn.execute(sql, params)
    else:
        result = conn.execute(sql)
    cols = [desc[0] for desc in result.description]
    row = result.fetchone()
    return row_to_actividad(row, cols) if row else None


def fetch_all_dict(conn, sql, params=None, columns=None):
    """Ejecuta SELECT y retorna lista de dicts."""
    if params:
        result = conn.execute(sql, params)
    else:
        result = conn.execute(sql)
    cols = [desc[0] for desc in result.description]
    return [row_to_actividad(r, cols) for r in result.fetchall()]


# ─── Actividades CRUD ───────────────────────────────────────────────────────
# CRUD completo de la tabla 'actividades' (30 columnas).
# Soporta búsqueda textual, filtros por área, base legal, estado
# y datos sensibles. Paginación con limit/offset.

@app.get("/api/actividades", response_model=list[ActividadOut])
def listar_actividades(
    search: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    base_licitud: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    datos_sensibles: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Lista actividades con filtros opcionales."""
    conn = get_connection()
    where = ["1=1"]
    params = []

    if search:
        where.append("(actividad_tratamiento ILIKE ? OR finalidad ILIKE ? OR descripcion ILIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if area:
        where.append("array_has(areas_intervienen, ?)")
        params.append(area)
    if base_licitud:
        where.append("base_licitud ILIKE ?")
        params.append(f"%{base_licitud}%")
    if estado:
        where.append("estado = ?")
        params.append(estado)
    if datos_sensibles is not None:
        where.append("datos_sensibles = ?")
        params.append(datos_sensibles)

    sql = f"SELECT * FROM actividades WHERE {' AND '.join(where)} ORDER BY updated_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    result = conn.execute(sql, params)
    cols = [desc[0] for desc in result.description]
    rows = result.fetchall()
    conn.close()
    return [row_to_actividad(r, cols) for r in rows]


@app.get("/api/actividades/total")
def total_actividades():
    """Estadísticas rápidas del RAT: total, cuántas tienen datos sensibles,
    cuántas hacen transferencias internacionales, distribución por estado."""
    conn = get_connection()
    total = conn.execute("SELECT count(*) FROM actividades").fetchone()[0]
    con_sensibles = conn.execute("SELECT count(*) FROM actividades WHERE datos_sensibles = true").fetchone()[0]
    con_transferencia = conn.execute(
        "SELECT count(*) FROM actividades WHERE transferencia_internacional != 'No aplica' AND transferencia_internacional != ''"
    ).fetchone()[0]
    por_estado = conn.execute(
        "SELECT estado, count(*) as cnt FROM actividades GROUP BY estado ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "datos_sensibles": con_sensibles,
        "transferencias_internacionales": con_transferencia,
        "por_estado": {r[0]: r[1] for r in por_estado},
    }


@app.get("/api/actividades/{actividad_id}", response_model=ActividadOut)
def obtener_actividad(actividad_id: int):
    """Obtiene una actividad de tratamiento por su ID con todos los campos
    incluyendo nivel_riesgo y score_actividad calculados."""
    conn = get_connection()
    row = fetch_one_dict(conn, "SELECT * FROM actividades WHERE id = ?", [actividad_id])
    conn.close()
    if not row:
        raise HTTPException(404, "Actividad no encontrada")
    return row


@app.post("/api/actividades", response_model=ActividadOut, status_code=201)
def crear_actividad(data: ActividadCreate):
    """Crea una nueva actividad de tratamiento con los 26 campos del RAT.
    Campos obligatorios: actividad_tratamiento, finalidad, base_licitud,
    plazo_conservacion. Retorna el registro creado con ID asignado."""
    conn = get_connection()
    result = conn.execute("""INSERT INTO actividades (
            actividad_tratamiento, responsable_tratamiento, responsable_rut,
            responsable_domicilio, responsable_representante, dpo_contacto,
            areas_intervienen, finalidad, descripcion,
            categoria_titulares, categorias_datos, datos_sensibles,
            origen_fuente, categoria_destinatarios, base_licitud,
            transferencia_internacional, pais_destino, garantías_transferencia,
            plazo_conservacion, justificacion_conservacion, medidas_seguridad,
            decisiones_automatizadas, requiere_eipd, nivel_riesgo, score_actividad, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id""", (
        data.actividad_tratamiento, data.responsable_tratamiento, data.responsable_rut,
        data.responsable_domicilio, data.responsable_representante, data.dpo_contacto,
        data.areas_intervienen, data.finalidad, data.descripcion,
        data.categoria_titulares, data.categorias_datos, data.datos_sensibles,
        data.origen_fuente, data.categoria_destinatarios, data.base_licitud,
        data.transferencia_internacional, data.pais_destino, data.garantías_transferencia,
        data.plazo_conservacion, data.justificacion_conservacion, data.medidas_seguridad,
        data.decisiones_automatizadas, data.requiere_eipd, data.nivel_riesgo, data.score_actividad, data.estado,
    ))
    new_id = result.fetchone()[0]
    row = fetch_one_dict(conn, "SELECT * FROM actividades WHERE id = ?", [new_id])
    conn.close()
    return row


@app.put("/api/actividades/{actividad_id}", response_model=ActividadOut)
def actualizar_actividad(actividad_id: int, data: ActividadUpdate):
    """Actualiza parcialmente una actividad. Solo los campos enviados son
    modificados; los demás conservan su valor. Actualiza updated_at."""
    conn = get_connection()
    existente = conn.execute("SELECT * FROM actividades WHERE id = ?", [actividad_id]).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(404, "Actividad no encontrada")

    updates = []
    params = []
    for field, val in data.model_dump(exclude_unset=True).items():
        if val is not None:
            updates.append(f"{field} = ?")
            params.append(val)
    if not updates:
        row = fetch_one_dict(conn, "SELECT * FROM actividades WHERE id = ?", [actividad_id])
        conn.close()
        return row

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(actividad_id)
    conn.execute(f"UPDATE actividades SET {', '.join(updates)} WHERE id = ?", params)
    row = fetch_one_dict(conn, "SELECT * FROM actividades WHERE id = ?", [actividad_id])
    conn.close()
    return row


@app.delete("/api/actividades/{actividad_id}", status_code=204)
def eliminar_actividad(actividad_id: int):
    """Elimina una actividad de tratamiento por su ID.
    Retorna 204 No Content."""
    conn = get_connection()
    conn.execute("DELETE FROM actividades WHERE id = ?", [actividad_id])
    conn.close()
    return None


# ─── Áreas ───────────────────────────────────────────────────────────────────
# Catálogo de unidades UCT. 12 áreas sembradas: CERETI, Admisión, Finanzas,
# TI, RRHH, Investigación, Biblioteca, Bienestar, Docencia, Vinculación,
# Marketing, Jurídica. Agrupables por tipo (dirección, unidad, vicerrectoría).

@app.get("/api/areas", response_model=list[AreaOut])
def listar_areas(tipo: Optional[str] = None):
    """Lista el catálogo de áreas/unidades UCT.
    Filtro opcional por tipo: 'dirección', 'unidad', 'vicerrectoría'."""
    conn = get_connection()
    if tipo:
        rows = conn.execute("SELECT * FROM areas WHERE tipo = ? ORDER BY nombre", [tipo]).fetchall()
    else:
        rows = conn.execute("SELECT * FROM areas ORDER BY nombre").fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "descripcion": r[2], "tipo": r[3]} for r in rows]


@app.post("/api/areas", response_model=AreaOut, status_code=201)
def crear_area(data: AreaCreate):
    """Agrega una nueva área/unidad al catálogo UCT.
    Campos: nombre, descripcion, tipo (default: 'unidad')."""
    conn = get_connection()
    result = conn.execute("INSERT INTO areas (nombre, descripcion, tipo) VALUES (?, ?, ?) RETURNING id",
                 [data.nombre, data.descripcion, data.tipo])
    new_id = result.fetchone()[0]
    row = conn.execute("SELECT * FROM areas WHERE id = ?", [new_id]).fetchone()
    conn.close()
    return {"id": row[0], "nombre": row[1], "descripcion": row[2], "tipo": row[3]}


# ─── Procesos ────────────────────────────────────────────────────────────────
# Macroprocesos institucionales agrupados por ámbito (Académico, Financiero,
# etc.). Se vinculan a actividades del RAT mediante actividades_ids[].

@app.get("/api/procesos", response_model=list[ProcesoOut])
def listar_procesos(macroproceso: Optional[str] = None):
    """Lista procesos institucionales. Filtro opcional por macroproceso
    ('Académico', 'Financiero', etc.). Orden: macroproceso → nombre."""
    conn = get_connection()
    if macroproceso:
        rows = conn.execute("SELECT * FROM procesos WHERE macroproceso = ? ORDER BY nombre",
                            [macroproceso]).fetchall()
    else:
        rows = conn.execute("SELECT * FROM procesos ORDER BY macroproceso, nombre").fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "macroproceso": r[2], "descripcion": r[3],
             "actividades_ids": r[4] if r[4] else []} for r in rows]


@app.post("/api/procesos", response_model=ProcesoOut, status_code=201)
def crear_proceso(data: ProcesoCreate):
    """Crea un proceso institucional, opcionalmente vinculado a actividades
    del RAT mediante el campo actividades_ids."""
    conn = get_connection()
    result = conn.execute("INSERT INTO procesos (nombre, macroproceso, descripcion, actividades_ids) VALUES (?, ?, ?, ?) RETURNING id",
                 [data.nombre, data.macroproceso, data.descripcion, data.actividades_ids])
    new_id = result.fetchone()[0]
    row = conn.execute("SELECT * FROM procesos WHERE id = ?", [new_id]).fetchone()
    conn.close()
    return {"id": row[0], "nombre": row[1], "macroproceso": row[2], "descripcion": row[3],
            "actividades_ids": row[4] if row[4] else []}


# ─── Encargados ──────────────────────────────────────────────────────────────
# Destinatarios externos de datos (encargados del tratamiento).
# Cada uno puede tener un DPA generado. Filtro por país.

@app.get("/api/encargados", response_model=list[EncargadoOut])
def listar_encargados(pais: Optional[str] = None):
    """Lista encargados/destinatarios externos. Filtro opcional por país.
    Incluye indicador dpa_generado para identificar pendientes."""
    conn = get_connection()
    if pais:
        rows = conn.execute("SELECT * FROM encargados WHERE pais = ? ORDER BY nombre", [pais]).fetchall()
    else:
        rows = conn.execute("SELECT * FROM encargados ORDER BY nombre").fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "rut": r[2], "pais": r[3], "servicio": r[4],
             "dpa_generado": bool(r[5])} for r in rows]


@app.post("/api/encargados", response_model=EncargadoOut, status_code=201)
def crear_encargado(data: EncargadoCreate):
    """Registra un nuevo encargado/destinatario externo de datos personales.
    Campos: nombre, rut, país, servicio, dpa_generado."""
    conn = get_connection()
    result = conn.execute("INSERT INTO encargados (nombre, rut, pais, servicio, dpa_generado) VALUES (?, ?, ?, ?, ?) RETURNING id",
                 [data.nombre, data.rut, data.pais, data.servicio, data.dpa_generado])
    new_id = result.fetchone()[0]
    row = conn.execute("SELECT * FROM encargados WHERE id = ?", [new_id]).fetchone()
    conn.close()
    return {"id": row[0], "nombre": row[1], "rut": row[2], "pais": row[3], "servicio": row[4],
            "dpa_generado": bool(row[5])}


# ─── Reportes ────────────────────────────────────────────────────────────────
# Reportes agregados para fiscalización APDP y monitoreo interno.
# resumen: distribución por base legal, área y titular.
# dpa-pendientes: encargados extranjeros sin acuerdo firmado.

@app.get("/api/reportes/resumen")
def reporte_resumen():
    """Resumen ejecutivo del RAT para fiscalización."""
    conn = get_connection()
    total = conn.execute("SELECT count(*) FROM actividades").fetchone()[0]
    por_base = conn.execute(
        "SELECT base_licitud, count(*) as cnt FROM actividades GROUP BY base_licitud ORDER BY cnt DESC"
    ).fetchall()
    por_area = conn.execute(
        "SELECT t.area, count(*) as cnt FROM (SELECT UNNEST(ifnull(areas_intervienen, [])) as area FROM actividades) t WHERE t.area IS NOT NULL GROUP BY t.area ORDER BY cnt DESC"
    ).fetchall()
    por_titular = conn.execute(
        "SELECT t.titular, count(*) as cnt FROM (SELECT UNNEST(ifnull(categoria_titulares, [])) as titular FROM actividades) t WHERE t.titular IS NOT NULL GROUP BY t.titular ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {
        "total_actividades": total,
        "por_base_legal": {r[0]: r[1] for r in por_base},
        "por_area": {r[0]: r[1] for r in por_area},
        "por_titular": {r[0]: r[1] for r in por_titular},
    }


@app.get("/api/reportes/dpa-pendientes")
def reporte_dpa_pendientes():
    """Encargados externos que aún no tienen DPA generado."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM encargados WHERE dpa_generado = false AND pais != 'Chile' ORDER BY nombre"
    ).fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "rut": r[2], "pais": r[3], "servicio": r[4],
             "dpa_generado": bool(r[5])} for r in rows]


# ─── Evaluación de Riesgo ────────────────────────────────────────────────────
# Motor de reglas automático para clasificar nivel de riesgo
# (bajo → medio → alto → crítico) y calcular score de cumplimiento (0-100).
# Las reglas completas están documentadas en evaluar_riesgo_actividad().

def evaluar_riesgo_actividad(actividad: dict) -> dict:
    """Evalúa el nivel de riesgo y score de cumplimiento de una actividad."""
    cats = [d.lower() for d in actividad.get("categorias_datos", [])]
    titulares = [t.lower() for t in actividad.get("categoria_titulares", [])]
    transfer = actividad.get("transferencia_internacional", "").lower()
    decisions = actividad.get("decisiones_automatizadas", "").lower()
    sensibles = actividad.get("datos_sensibles", False)

    factores = []
    nivel = "bajo"

    # Reglas: crítico
    if any(p in " ".join(cats) for p in ["salud", "biométric", "biometric", "racial", "étnico", "etnico", "ideología", "ideologia", "sexual", "vida sexual"]):
        nivel = "crítico"
        factores.append("Datos sensibles (salud/biométricos/íntimos)")
    if any("nna" in t or "menor" in t or "niño" in t or "nino" in t for t in titulares):
        if nivel != "crítico":
            nivel = "crítico"
        factores.append("Involucra NNA (menores de edad)")
    if sensibles and transfer and transfer != "no aplica":
        if nivel != "crítico":
            nivel = "crítico"
        factores.append("Datos sensibles + transferencia internacional")

    # Reglas: alto
    if sensibles and nivel == "bajo":
        nivel = "alto"
        factores.append("Datos sensibles")
    if nivel == "bajo" and any("gran escala" in d or "financiero" in d for d in cats):
        nivel = "alto"
        factores.append("Posible gran escala")

    # Reglas: medio
    if transfer and transfer != "no aplica" and nivel == "bajo":
        nivel = "medio"
        factores.append("Transferencia internacional")
    if decisions and decisions != "no aplica" and nivel == "bajo":
        nivel = "medio"
        factores.append("Decisiones automatizadas")
    if actividad.get("requiere_eipd", False) and nivel == "bajo":
        nivel = "medio"
        factores.append("Requiere EIPD")

    # Score de cumplimiento (0-100)
    score = 100
    penalizaciones = {
        "crítico": 40,
        "alto": 25,
        "medio": 10,
        "bajo": 0,
    }
    score -= penalizaciones.get(nivel, 0)

    # Penalizaciones adicionales
    if not actividad.get("medidas_seguridad"):
        score -= 10
    if not actividad.get("plazo_conservacion"):
        score -= 10
    if not actividad.get("justificacion_conservacion"):
        score -= 5
    if not actividad.get("origen_fuente"):
        score -= 5
    if transfer and transfer != "no aplica" and not actividad.get("garantías_transferencia"):
        score -= 10

    score = max(0, min(100, score))

    return {
        "nivel_riesgo": nivel,
        "score_actividad": score,
        "factores": factores,
    }


@app.post("/api/actividades/{actividad_id}/evaluar-riesgo")
def evaluar_riesgo_endpoint(actividad_id: int):
    """Evalúa y actualiza el nivel de riesgo y score de una actividad."""
    conn = get_connection()
    actividad = fetch_one_dict(conn, "SELECT * FROM actividades WHERE id = ?", [actividad_id])
    if not actividad:
        conn.close()
        raise HTTPException(404, "Actividad no encontrada")

    resultado = evaluar_riesgo_actividad(actividad)
    conn.execute(
        "UPDATE actividades SET nivel_riesgo = ?, score_actividad = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        [resultado["nivel_riesgo"], resultado["score_actividad"], actividad_id]
    )
    conn.close()
    return resultado


@app.post("/api/actividades/evaluar-riesgo-todas")
def evaluar_riesgo_todas():
    """Evalúa riesgo de todas las actividades activas."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM actividades WHERE estado = 'activo'").fetchall()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM actividades WHERE estado = 'activo'").description]
    conn.close()

    results = []
    for row in rows:
        act = row_to_actividad(row, cols)
        res = evaluar_riesgo_actividad(act)
        conn = get_connection()
        conn.execute(
            "UPDATE actividades SET nivel_riesgo = ?, score_actividad = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            [res["nivel_riesgo"], res["score_actividad"], act["id"]]
        )
        conn.close()
        results.append({"id": act["id"], "actividad": act["actividad_tratamiento"], **res})

    return {"evaluadas": len(results), "resultados": results}


@app.get("/api/reportes/matriz-riesgo")
def matriz_riesgo():
    """Matriz de riesgo: distribución por nivel y por área."""
    conn = get_connection()
    por_nivel = conn.execute(
        "SELECT nivel_riesgo, count(*) as cnt FROM actividades GROUP BY nivel_riesgo ORDER BY cnt DESC"
    ).fetchall()

    por_area_nivel = conn.execute(
        "SELECT t.area, t.nivel, count(*) as cnt FROM "
        "(SELECT UNNEST(ifnull(areas_intervienen, [])) as area, nivel_riesgo as nivel FROM actividades) t "
        "WHERE t.area IS NOT NULL GROUP BY t.area, t.nivel ORDER BY t.area"
    ).fetchall()

    heatmap = {}
    for area, nivel, cnt in por_area_nivel:
        if area not in heatmap:
            heatmap[area] = {"crítico": 0, "alto": 0, "medio": 0, "bajo": 0}
        heatmap[area][nivel] = cnt

    conn.close()
    return {
        "por_nivel": {r[0]: r[1] for r in por_nivel},
        "heatmap": heatmap,
    }


@app.get("/api/reportes/score")
def reporte_score():
    """Score de cumplimiento global y por área."""
    conn = get_connection()
    # Score global
    scores = conn.execute("SELECT score_actividad FROM actividades WHERE score_actividad IS NOT NULL").fetchall()
    score_global = round(sum(s[0] for s in scores) / len(scores)) if scores else 0

    # Score por área
    por_area = conn.execute(
        "SELECT t.area, avg(a.score_actividad) as score_avg, count(*) as cnt "
        "FROM actividades a, LATERAL UNNEST(ifnull(a.areas_intervienen, [])) as t(area) "
        "WHERE a.score_actividad IS NOT NULL AND t.area IS NOT NULL "
        "GROUP BY t.area ORDER BY score_avg DESC"
    ).fetchall()

    # Score por nivel de riesgo
    por_riesgo = conn.execute(
        "SELECT nivel_riesgo, count(*) as cnt, avg(score_actividad) as score_avg "
        "FROM actividades WHERE nivel_riesgo IS NOT NULL "
        "GROUP BY nivel_riesgo ORDER BY "
        "CASE nivel_riesgo WHEN 'bajo' THEN 1 WHEN 'medio' THEN 2 WHEN 'alto' THEN 3 WHEN 'crítico' THEN 4 END"
    ).fetchall()

    conn.close()
    return {
        "score_global": score_global,
        "total_evaluadas": len(scores),
        "por_area": [{"area": r[0], "score": round(r[1]), "actividades": r[2]} for r in por_area],
        "por_nivel_riesgo": [{"nivel": r[0], "count": r[1], "score_promedio": round(r[2]) if r[2] else 0} for r in por_riesgo],
    }
 
 
# ─── EIPD ────────────────────────────────────────────────────────────────────
# Evaluación de Impacto en Protección de Datos. Flujo en 4 pasos:
#   1. Diagnóstico — ¿necesita EIPD? ¿motivo de activación?
#   2. Riesgo — clasificación de riesgo inherente y residual
#   3. Medidas — propuestas e implementadas
#   4. Firma — aprobación por el DPO
 
@app.get("/api/eipd", response_model=list[EipdOut])
def listar_eipd(actividad_id: Optional[int] = Query(None)):
    """Lista EIPDs, opcionalmente filtradas por actividad_id.
    Orden: más recientes primero."""
    conn = get_connection()
    if actividad_id:
        rows = conn.execute("SELECT * FROM eipd WHERE actividad_id = ? ORDER BY created_at DESC", [actividad_id]).fetchall()
    else:
        rows = conn.execute("SELECT * FROM eipd ORDER BY created_at DESC").fetchall()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM eipd LIMIT 0").description]
    conn.close()
    result = []
    for r in rows:
        d = {}
        for i, c in enumerate(cols):
            v = r[i]
            if v is None:
                d[c] = ""
            elif c in ("necesita_eipd",):
                d[c] = bool(v)
            else:
                d[c] = v
        result.append(d)
    return result
 
 
@app.post("/api/eipd", response_model=EipdOut, status_code=201)
def crear_eipd(data: EipdCreate):
    """Inicia una nueva EIPD para una actividad. Los 4 pasos se completan
    incrementalmente mediante PUT /api/eipd/{id}."""
    conn = get_connection()
    result = conn.execute("""INSERT INTO eipd (
        actividad_id, estado, necesita_eipd, motivo_activacion,
        riesgo_inherente, riesgo_residual, medidas_propuestas,
        medidas_implementadas, aprobado_por, fecha_aprobacion
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id""", (
        data.actividad_id, data.estado, data.necesita_eipd, data.motivo_activacion,
        data.riesgo_inherente, data.riesgo_residual, data.medidas_propuestas,
        data.medidas_implementadas, data.aprobado_por, data.fecha_aprobacion,
    ))
    new_id = result.fetchone()[0]
    row = conn.execute("SELECT * FROM eipd WHERE id = ?", [new_id]).fetchone()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM eipd LIMIT 0").description]
    conn.close()
    d = {}
    for i, c in enumerate(cols):
        v = row[i]
        if v is None:
            d[c] = ""
        elif c in ("necesita_eipd",):
            d[c] = bool(v)
        else:
            d[c] = v
    return d
 
 
@app.put("/api/eipd/{eipd_id}", response_model=EipdOut)
def actualizar_eipd(eipd_id: int, data: EipdUpdate):
    """Actualiza uno o más campos de una EIPD (avance de pasos).
    Solo los campos enviados se modifican; actualiza updated_at."""
    conn = get_connection()
    existente = conn.execute("SELECT * FROM eipd WHERE id = ?", [eipd_id]).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(404, "EIPD no encontrada")
    updates = []
    params = []
    for field, val in data.model_dump(exclude_unset=True).items():
        if val is not None:
            updates.append(f"{field} = ?")
            params.append(val)
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(eipd_id)
        conn.execute(f"UPDATE eipd SET {', '.join(updates)} WHERE id = ?", params)
    row = conn.execute("SELECT * FROM eipd WHERE id = ?", [eipd_id]).fetchone()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM eipd LIMIT 0").description]
    conn.close()
    d = {}
    for i, c in enumerate(cols):
        v = row[i]
        if v is None:
            d[c] = ""
        elif c in ("necesita_eipd",):
            d[c] = bool(v)
        else:
            d[c] = v
    return d
 
 
@app.get("/api/actividades/{actividad_id}/eipd", response_model=list[EipdOut])
def eipd_por_actividad(actividad_id: int):
    """Obtiene las EIPDs asociadas a una actividad."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM eipd WHERE actividad_id = ? ORDER BY created_at DESC", [actividad_id]).fetchall()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM eipd LIMIT 0").description]
    conn.close()
    result = []
    for r in rows:
        d = {}
        for i, c in enumerate(cols):
            v = r[i]
            if v is None:
                d[c] = ""
            elif c in ("necesita_eipd",):
                d[c] = bool(v)
            else:
                d[c] = v
        result.append(d)
    return result
 
 
# ─── Brechas ─────────────────────────────────────────────────────────────────
# Registro de incidentes de seguridad. Cada brecha registra:
# - Timeline de detección y notificación (alerta 72h Ley 21.719)
# - Severidad (baja → crítica), tipo de incidente, datos afectados
# - Medidas correctivas y estados de notificación a APDP y titulares
 
@app.get("/api/brechas", response_model=list[BrechaOut])
def listar_brechas(estado: Optional[str] = Query(None), severidad: Optional[str] = Query(None)):
    """Lista brechas de seguridad. Filtros opcionales por estado
    ('abierta', 'en_investigación', 'cerrada') y severidad."""
    conn = get_connection()
    where = ["1=1"]
    params = []
    if estado:
        where.append("estado = ?"); params.append(estado)
    if severidad:
        where.append("severidad = ?"); params.append(severidad)
    rows = conn.execute(f"SELECT * FROM brechas WHERE {' AND '.join(where)} ORDER BY created_at DESC", params).fetchall()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM brechas LIMIT 0").description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]
 
 
@app.post("/api/brechas", response_model=BrechaOut, status_code=201)
def crear_brecha(data: BrechaCreate):
    """Registra una nueva brecha de seguridad. Calcula automáticamente
    el plazo de notificación (fecha_deteccion + 72h) según Ley 21.719."""
    conn = get_connection()
    result = conn.execute("""INSERT INTO brechas (actividad_id, titulo, descripcion, severidad, tipo_incidente, datos_afectados, titulares_afectados, medidas_correctivas, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id""", (
        data.actividad_id, data.titulo, data.descripcion, data.severidad,
        data.tipo_incidente, data.datos_afectados, data.titulares_afectados,
        data.medidas_correctivas, data.estado))
    new_id = result.fetchone()[0]
    row = conn.execute("SELECT * FROM brechas WHERE id = ?", [new_id]).fetchone()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM brechas LIMIT 0").description]
    conn.close()
    return dict(zip(cols, row))
 
 
@app.put("/api/brechas/{brecha_id}", response_model=BrechaOut)
def actualizar_brecha(brecha_id: int, data: BrechaUpdate):
    """Actualiza una brecha (cambiar estado, agregar medidas correctivas,
    marcar notificaciones a APDP/titulares)."""
    conn = get_connection()
    existente = conn.execute("SELECT * FROM brechas WHERE id = ?", [brecha_id]).fetchone()
    if not existente: conn.close(); raise HTTPException(404, "Brecha no encontrada")
    updates = []; params = []
    for field, val in data.model_dump(exclude_unset=True).items():
        if val is not None: updates.append(f"{field} = ?"); params.append(val)
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP"); params.append(brecha_id)
        conn.execute(f"UPDATE brechas SET {', '.join(updates)} WHERE id = ?", params)
    row = conn.execute("SELECT * FROM brechas WHERE id = ?", [brecha_id]).fetchone()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM brechas LIMIT 0").description]
    conn.close()
    return dict(zip(cols, row))
 
 
# ─── ARCOP ───────────────────────────────────────────────────────────────────
# Portal de gestión de derechos ARCOP (Acceso, Rectificación, Cancelación,
# Oposición, Portabilidad, Bloqueo). Cada solicitud tiene:
# - SLA de 30 días desde fecha_solicitud
# - Estados: recibida → en_estudio → respondida → rechazada
 
@app.get("/api/arcop", response_model=list[ArcopOut])
def listar_arcop(estado: Optional[str] = Query(None)):
    """Lista solicitudes ARCOP. Filtro opcional por estado:
    'recibida', 'en_estudio', 'respondida', 'rechazada'."""
    conn = get_connection()
    if estado:
        rows = conn.execute("SELECT * FROM solicitudes_arcop WHERE estado = ? ORDER BY created_at DESC", [estado]).fetchall()
    else:
        rows = conn.execute("SELECT * FROM solicitudes_arcop ORDER BY created_at DESC").fetchall()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM solicitudes_arcop LIMIT 0").description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]
 
 
@app.post("/api/arcop", response_model=ArcopOut, status_code=201)
def crear_arcop(data: ArcopCreate):
    """Registra una nueva solicitud de derechos ARCOP. Calcula
    automáticamente fecha_vencimiento (fecha_solicitud + 30 días)."""
    conn = get_connection()
    result = conn.execute("""INSERT INTO solicitudes_arcop (tipo_derecho, solicitante_nombre, solicitante_email, solicitante_rut, descripcion, actividad_id)
        VALUES (?, ?, ?, ?, ?, ?) RETURNING id""", (
        data.tipo_derecho, data.solicitante_nombre, data.solicitante_email,
        data.solicitante_rut, data.descripcion, data.actividad_id))
    new_id = result.fetchone()[0]
    row = conn.execute("SELECT * FROM solicitudes_arcop WHERE id = ?", [new_id]).fetchone()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM solicitudes_arcop LIMIT 0").description]
    conn.close()
    return dict(zip(cols, row))
 
 
@app.put("/api/arcop/{arcop_id}", response_model=ArcopOut)
def actualizar_arcop(arcop_id: int, data: ArcopUpdate):
    """Responde una solicitud ARCOP: cambia estado y registra la respuesta
    con fecha de cierre."""
    conn = get_connection()
    existente = conn.execute("SELECT * FROM solicitudes_arcop WHERE id = ?", [arcop_id]).fetchone()
    if not existente: conn.close(); raise HTTPException(404, "Solicitud no encontrada")
    updates = []; params = []
    for field, val in data.model_dump(exclude_unset=True).items():
        if val is not None: updates.append(f"{field} = ?"); params.append(val)
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP"); params.append(arcop_id)
        conn.execute(f"UPDATE solicitudes_arcop SET {', '.join(updates)} WHERE id = ?", params)
    row = conn.execute("SELECT * FROM solicitudes_arcop WHERE id = ?", [arcop_id]).fetchone()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM solicitudes_arcop LIMIT 0").description]
    conn.close()
    return dict(zip(cols, row))
 
 
# ─── DPA ─────────────────────────────────────────────────────────────────────
# Data Processing Agreement (DPA) — acuerdo de encargo de tratamiento
# con terceros. Genera un placeholder textual; pendiente: PDF real con
# firma digital y hash SHA-256 para cadena de custodia.
 
@app.post("/api/dpa/generar/{encargado_id}")
def generar_dpa(encargado_id: int):
    """Genera un DPA (Data Processing Agreement) para un encargado externo.
    Marca dpa_generado=true en la tabla encargados.
    Pendiente: generar PDF real con firma digital."""
    conn = get_connection()
    enc = conn.execute("SELECT * FROM encargados WHERE id = ?", [encargado_id]).fetchone()
    if not enc: conn.close(); raise HTTPException(404, "Encargado no encontrado")
    conn.execute("UPDATE encargados SET dpa_generado = true WHERE id = ?", [encargado_id])
    conn.close()
    return {
        "mensaje": "DPA generado exitosamente",
        "encargado": enc[1],
        "contenido": f"Acuerdo de tratamiento de datos con {enc[1]} según Ley 21.719. País: {enc[3]}. Servicio: {enc[4]}."
    }
 
 
# ─── Fases de Implementación ────────────────────────────────────────────────
# Barra de progreso alineada con las 12 fases del modelo Kulvio.
# Cada fase se marca como completada según datos reales en la DB:
# hay actividades → fase 2-3, hay riesgos → fase 4, hay EIPD → fase 5, etc.
 
@app.get("/api/fases")
def fases_implementacion():
    """Retorna el progreso de las 12 fases de implementación (modelo Kulvio).
    Cada fase se evalúa contra datos reales en la base de datos."""
    conn = get_connection()
    total_acts = conn.execute("SELECT count(*) FROM actividades").fetchone()[0]
    has_riesgo = conn.execute("SELECT count(*) FROM actividades WHERE nivel_riesgo IS NOT NULL AND nivel_riesgo != 'bajo'").fetchone()[0]
    has_eipd = conn.execute("SELECT count(*) FROM eipd").fetchone()[0]
    has_brechas = conn.execute("SELECT count(*) FROM brechas").fetchone()[0]
    has_arcop = conn.execute("SELECT count(*) FROM solicitudes_arcop").fetchone()[0]
    conn.close()
    fases = [
        {"id": 1, "nombre": "Configuración Inicial", "completado": True},
        {"id": 2, "nombre": "Diagnóstico", "completado": total_acts > 0},
        {"id": 3, "nombre": "RAT", "completado": total_acts > 0},
        {"id": 4, "nombre": "Evaluación de Riesgo", "completado": has_riesgo > 0},
        {"id": 5, "nombre": "EIPD", "completado": has_eipd > 0},
        {"id": 6, "nombre": "Terceros / DPA", "completado": False},
        {"id": 7, "nombre": "Consentimientos", "completado": False},
        {"id": 8, "nombre": "ARCOP", "completado": has_arcop > 0},
        {"id": 9, "nombre": "Brechas", "completado": has_brechas > 0},
        {"id": 10, "nombre": "Denuncias", "completado": False},
        {"id": 11, "nombre": "Documentación", "completado": False},
        {"id": 12, "nombre": "Monitoreo", "completado": False},
    ]
    completadas = sum(1 for f in fases if f["completado"])
    return {"total": 12, "completadas": completadas, "progreso": round(completadas / 12 * 100), "fases": fases}
 
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# ─── Servir frontend estático (producción) ───────────────────────────────────
# En producción (Fly.io / Docker), la carpeta static/ contiene el build de React.
# FastAPI sirve la SPA después de todas las rutas API registradas.
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
