"""
RAT UCT — Áreas (catálogo de unidades UCT)
============================================

Catálogo de unidades UCT. 12 áreas sembradas: CERETI, Admisión, Finanzas,
TI, RRHH, Investigación, Biblioteca, Bienestar, Docencia, Vinculación,
Marketing, Jurídica. Agrupables por tipo (dirección, unidad, vicerrectoría).
"""

from fastapi import APIRouter
from typing import Optional

from database import get_connection
from models import AreaCreate, AreaOut

router = APIRouter(prefix="/api/v1/areas", tags=["Áreas v1"])


@router.get("", response_model=list[AreaOut])
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


@router.post("", response_model=AreaOut, status_code=201)
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
