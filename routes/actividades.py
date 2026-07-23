"""
RAT UCT — Actividades CRUD (6 + 3 endpoints)
==============================================

CRUD completo de la tabla 'actividades' (30 columnas) con filtros avanzados,
evaluación de riesgo y consulta de EIPDs asociadas.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from database import get_connection
from models import ActividadCreate, ActividadUpdate, ActividadOut, EipdOut
from utils import row_to_actividad, fetch_one_dict, evaluar_riesgo_actividad

router = APIRouter(prefix="/api/actividades", tags=["Actividades"])


@router.get("", response_model=list[ActividadOut])
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


@router.get("/total")
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


@router.get("/{actividad_id}", response_model=ActividadOut)
def obtener_actividad(actividad_id: int):
    """Obtiene una actividad de tratamiento por su ID con todos los campos
    incluyendo nivel_riesgo y score_actividad calculados."""
    conn = get_connection()
    row = fetch_one_dict(conn, "SELECT * FROM actividades WHERE id = ?", [actividad_id])
    conn.close()
    if not row:
        raise HTTPException(404, "Actividad no encontrada")
    return row


@router.post("", response_model=ActividadOut, status_code=201)
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


@router.put("/{actividad_id}", response_model=ActividadOut)
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


@router.delete("/{actividad_id}", status_code=204)
def eliminar_actividad(actividad_id: int):
    """Elimina una actividad de tratamiento por su ID.
    Retorna 204 No Content."""
    conn = get_connection()
    conn.execute("DELETE FROM actividades WHERE id = ?", [actividad_id])
    conn.close()
    return None


# ─── Evaluación de Riesgo ───────────────────────────────────────────────────

@router.post("/{actividad_id}/evaluar-riesgo")
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


@router.post("/evaluar-riesgo-todas")
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


# ─── EIPD por actividad (ruta anidada) ──────────────────────────────────────

@router.get("/{actividad_id}/eipd", response_model=list[EipdOut])
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
