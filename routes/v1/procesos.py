"""
RAT UCT — Procesos (macroprocesos institucionales)
====================================================

Macroprocesos institucionales agrupados por ámbito (Académico, Financiero,
etc.). Se vinculan a actividades del RAT mediante actividades_ids[].
"""

from fastapi import APIRouter
from typing import Optional

from database import get_connection
from models import ProcesoCreate, ProcesoOut

router = APIRouter(prefix="/api/v1/procesos", tags=["Procesos v1"])


@router.get("", response_model=list[ProcesoOut])
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


@router.post("", response_model=ProcesoOut, status_code=201)
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
