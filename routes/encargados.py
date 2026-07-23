"""
RAT UCT — Encargados (destinatarios externos de datos)
========================================================

Destinatarios externos de datos (encargados del tratamiento).
Cada uno puede tener un DPA generado. Filtro por país.
"""

from fastapi import APIRouter
from typing import Optional

from database import get_connection
from models import EncargadoCreate, EncargadoOut

router = APIRouter(prefix="/api/encargados", tags=["Encargados"])


@router.get("", response_model=list[EncargadoOut])
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


@router.post("", response_model=EncargadoOut, status_code=201)
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
