"""
RAT UCT - EIPD (Evaluacion de Impacto en Proteccion de Datos)
===============================================================

Flujo en 4 pasos:
  1. Diagnostico - ¿necesita EIPD? ¿motivo de activacion?
  2. Riesgo - clasificacion de riesgo inherente y residual
  3. Medidas - propuestas e implementadas
  4. Firma - aprobacion por el DPO
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from database import get_connection
from models import EipdCreate, EipdUpdate, EipdOut
from utils import sanitize_row

router = APIRouter(prefix="/api/v1/eipd", tags=["EIPD v1"])

# Para EIPD, queremos que todos los NULL opcionales se envien como ""
# y necesita_eipd se coercea a bool explicitamente
_DEFAULTS = {
    "motivo_activacion": "",
    "riesgo_inherente": "",
    "riesgo_residual": "",
    "medidas_propuestas": "",
    "medidas_implementadas": "",
    "aprobado_por": "",
    "fecha_aprobacion": "",
}
_COERCE_BOOL = {"necesita_eipd"}


def _rows_to_eipd(cols, rows):
    return [sanitize_row(cols, r, _DEFAULTS, _COERCE_BOOL) for r in rows]


def _row_to_eipd(cols, row):
    return sanitize_row(cols, row, _DEFAULTS, _COERCE_BOOL)


@router.get("", response_model=list[EipdOut])
def listar_eipd(actividad_id: Optional[int] = Query(None)):
    """Lista EIPDs, opcionalmente filtradas por actividad_id.
    Orden: mas recientes primero."""
    conn = get_connection()
    if actividad_id:
        rows = conn.execute("SELECT * FROM eipd WHERE actividad_id = ? ORDER BY created_at DESC", [actividad_id]).fetchall()
    else:
        rows = conn.execute("SELECT * FROM eipd ORDER BY created_at DESC").fetchall()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM eipd LIMIT 0").description]
    conn.close()
    return _rows_to_eipd(cols, rows)


@router.post("", response_model=EipdOut, status_code=201)
def crear_eipd(data: EipdCreate):
    """Inicia una nueva EIPD para una actividad. Los 4 pasos se completan
    incrementalmente mediante PUT /api/v1/eipd/{id}."""
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
    return _row_to_eipd(cols, row)


@router.put("/{eipd_id}", response_model=EipdOut)
def actualizar_eipd(eipd_id: int, data: EipdUpdate):
    """Actualiza uno o mas campos de una EIPD (avance de pasos).
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
    return _row_to_eipd(cols, row)
