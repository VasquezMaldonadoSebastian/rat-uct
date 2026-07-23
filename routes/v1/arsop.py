"""
RAT UCT - ARSOP (derechos de titulares)
=========================================

Portal de gestion de derechos ARSOP (Acceso, Rectificacion, Supresion,
Oposicion, Portabilidad). Cada solicitud tiene:
- SLA de 30 dias desde fecha_solicitud
- Estados: recibida -> en_estudio -> respondida -> rechazada
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from database import get_connection
from models import ArsopCreate, ArsopUpdate, ArsopOut
from utils import sanitize_row

router = APIRouter(prefix="/api/v1/arsop", tags=["ARSOP v1"])

# Defaults para campos VARCHAR que pueden ser NULL en DB
_DEFAULTS = {
    "respuesta": "",
    "solicitante_nombre": "",
    "solicitante_email": "",
    "solicitante_rut": "",
    "descripcion": "",
}


def _rows_to_arsop(cols, rows):
    return [sanitize_row(cols, r, _DEFAULTS) for r in rows]


def _row_to_arsop(cols, row):
    return sanitize_row(cols, row, _DEFAULTS)


@router.get("", response_model=list[ArsopOut])
def listar_arsop(estado: Optional[str] = Query(None)):
    """Lista solicitudes ARSOP. Filtro opcional por estado:
    'recibida', 'en_estudio', 'respondida', 'rechazada'."""
    conn = get_connection()
    if estado:
        rows = conn.execute("SELECT * FROM solicitudes_arsop WHERE estado = ? ORDER BY created_at DESC", [estado]).fetchall()
    else:
        rows = conn.execute("SELECT * FROM solicitudes_arsop ORDER BY created_at DESC").fetchall()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM solicitudes_arsop LIMIT 0").description]
    conn.close()
    return _rows_to_arsop(cols, rows)


@router.post("", response_model=ArsopOut, status_code=201)
def crear_arsop(data: ArsopCreate):
    """Registra una nueva solicitud de derechos ARSOP. Calcula
    automaticamente fecha_vencimiento (fecha_solicitud + 30 dias)."""
    conn = get_connection()
    result = conn.execute("""INSERT INTO solicitudes_arsop (tipo_derecho, solicitante_nombre, solicitante_email, solicitante_rut, descripcion, actividad_id)
        VALUES (?, ?, ?, ?, ?, ?) RETURNING id""", (
            data.tipo_derecho, data.solicitante_nombre, data.solicitante_email,
            data.solicitante_rut, data.descripcion, data.actividad_id))
    new_id = result.fetchone()[0]
    row = conn.execute("SELECT * FROM solicitudes_arsop WHERE id = ?", [new_id]).fetchone()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM solicitudes_arsop LIMIT 0").description]
    conn.close()
    return _row_to_arsop(cols, row)


@router.put("/{arsop_id}", response_model=ArsopOut)
def actualizar_arsop(arsop_id: int, data: ArsopUpdate):
    """Responde una solicitud ARSOP: cambia estado y registra la respuesta
    con fecha de cierre."""
    conn = get_connection()
    existente = conn.execute("SELECT * FROM solicitudes_arsop WHERE id = ?", [arsop_id]).fetchone()
    if not existente: conn.close(); raise HTTPException(404, "Solicitud no encontrada")
    updates = []; params = []
    for field, val in data.model_dump(exclude_unset=True).items():
        if val is not None: updates.append(f"{field} = ?"); params.append(val)
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP"); params.append(arsop_id)
        conn.execute(f"UPDATE solicitudes_arsop SET {', '.join(updates)} WHERE id = ?", params)
    row = conn.execute("SELECT * FROM solicitudes_arsop WHERE id = ?", [arsop_id]).fetchone()
    cols = [desc[0] for desc in conn.execute("SELECT * FROM solicitudes_arsop LIMIT 0").description]
    conn.close()
    return _row_to_arsop(cols, row)
