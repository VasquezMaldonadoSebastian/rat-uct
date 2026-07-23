"""
RAT UCT - Brechas de seguridad (incidentes)
=============================================

Registro de incidentes de seguridad. Cada brecha registra:
- Timeline de deteccion y notificacion (alerta 72h Ley 21.719)
- Severidad (baja -> critica), tipo de incidente, datos afectados
- Medidas correctivas y estados de notificacion a APDP y titulares
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from database import get_connection
from models import BrechaCreate, BrechaUpdate, BrechaOut
from utils import sanitize_row

router = APIRouter(prefix="/api/v1/brechas", tags=["Brechas v1"])

# Defaults para campos que pueden ser NULL en DB
_DEFAULTS = {
    "descripcion": "",
    "tipo_incidente": "",
    "datos_afectados": "",
    "medidas_correctivas": "",
}
_COERCE_BOOL = {"notificado_apdp", "notificado_titulares"}


def _rows_to_brechas(cols, rows):
    """Convierte filas DuckDB a lista de dicts sanitizados."""
    return [sanitize_row(cols, r, _DEFAULTS, _COERCE_BOOL) for r in rows]


def _row_to_brecha(cols, row):
    """Convierte una fila DuckDB a dict sanitizado."""
    return sanitize_row(cols, row, _DEFAULTS, _COERCE_BOOL)


@router.get("", response_model=list[BrechaOut])
def listar_brechas(estado: Optional[str] = Query(None), severidad: Optional[str] = Query(None)):
    """Lista brechas de seguridad. Filtros opcionales por estado
    ('abierta', 'en_investigacion', 'cerrada') y severidad."""
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
    return _rows_to_brechas(cols, rows)


@router.post("", response_model=BrechaOut, status_code=201)
def crear_brecha(data: BrechaCreate):
    """Registra una nueva brecha de seguridad. Calcula automaticamente
    el plazo de notificacion (fecha_deteccion + 72h) segun Ley 21.719."""
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
    return _row_to_brecha(cols, row)


@router.put("/{brecha_id}", response_model=BrechaOut)
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
    return _row_to_brecha(cols, row)
