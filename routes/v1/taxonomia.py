"""
RAT UCT — Taxonomía de Datos (Fides Taxonomy)
==============================================

Catálogos Fides y asignación de taxonomía a actividades de tratamiento:
  - Categorías de datos personales: ej. Salud, Biométricos, RUT, Dirección
  - Finalidades de tratamiento: ej. Gestión académica, Investigación
  - Bases de licitud: ej. Consentimiento, Interés legítimo, Obligación legal
  - Asignaciones: puente actividad -> categoría + finalidad + base
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from database import get_connection
from models import (
    CategoriaDatoCreate, CategoriaDatoOut,
    FinalidadCreate, FinalidadOut,
    BaseLicitudCreate, BaseLicitudOut,
    TaxonomiaAsignacionCreate, TaxonomiaAsignacionOut,
)

router = APIRouter(prefix="/api/v1/taxonomia", tags=["Taxonomia v1"])


# ─── Categorías de Datos ───────────────────────────────────────────────────


@router.get("/categorias", response_model=list[CategoriaDatoOut])
def listar_categorias(tipo_dato: Optional[str] = Query(None)):
    """Lista el catálogo de categorías de datos personales.
    Filtro opcional por tipo_dato: 'personal', 'sensible', 'biométrico', 'financiero'."""
    conn = get_connection()
    if tipo_dato:
        rows = conn.execute(
            "SELECT * FROM categorias_datos_catalog WHERE tipo_dato = ? ORDER BY nombre",
            [tipo_dato]
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM categorias_datos_catalog ORDER BY nombre").fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "descripcion": r[2], "tipo_dato": r[3]} for r in rows]


@router.post("/categorias", response_model=CategoriaDatoOut, status_code=201)
def crear_categoria(data: CategoriaDatoCreate):
    """Agrega una nueva categoría de dato personal al catálogo Fides."""
    conn = get_connection()
    try:
        result = conn.execute(
            "INSERT INTO categorias_datos_catalog (nombre, descripcion, tipo_dato) VALUES (?, ?, ?) RETURNING id",
            [data.nombre, data.descripcion, data.tipo_dato]
        )
        new_id = result.fetchone()[0]
        row = conn.execute("SELECT * FROM categorias_datos_catalog WHERE id = ?", [new_id]).fetchone()
        conn.close()
        return {"id": row[0], "nombre": row[1], "descripcion": row[2], "tipo_dato": row[3]}
    except Exception as e:
        conn.close()
        raise HTTPException(400, f"Error al crear categoría: {str(e)}")


# ─── Finalidades ───────────────────────────────────────────────────────────


@router.get("/finalidades", response_model=list[FinalidadOut])
def listar_finalidades():
    """Lista el catálogo de finalidades de tratamiento."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM finalidades_catalog ORDER BY nombre").fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "descripcion": r[2]} for r in rows]


@router.post("/finalidades", response_model=FinalidadOut, status_code=201)
def crear_finalidad(data: FinalidadCreate):
    """Agrega una nueva finalidad de tratamiento al catálogo."""
    conn = get_connection()
    try:
        result = conn.execute(
            "INSERT INTO finalidades_catalog (nombre, descripcion) VALUES (?, ?) RETURNING id",
            [data.nombre, data.descripcion]
        )
        new_id = result.fetchone()[0]
        row = conn.execute("SELECT * FROM finalidades_catalog WHERE id = ?", [new_id]).fetchone()
        conn.close()
        return {"id": row[0], "nombre": row[1], "descripcion": row[2]}
    except Exception as e:
        conn.close()
        raise HTTPException(400, f"Error al crear finalidad: {str(e)}")


# ─── Bases de Licitud ─────────────────────────────────────────────────────


@router.get("/bases", response_model=list[BaseLicitudOut])
def listar_bases():
    """Lista el catálogo de bases de licitud para tratamiento de datos."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM bases_licitud_catalog ORDER BY nombre").fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "descripcion": r[2], "referencia_legal": r[3]} for r in rows]


@router.post("/bases", response_model=BaseLicitudOut, status_code=201)
def crear_base(data: BaseLicitudCreate):
    """Agrega una nueva base de licitud al catálogo."""
    conn = get_connection()
    try:
        result = conn.execute(
            "INSERT INTO bases_licitud_catalog (nombre, descripcion, referencia_legal) VALUES (?, ?, ?) RETURNING id",
            [data.nombre, data.descripcion, data.referencia_legal]
        )
        new_id = result.fetchone()[0]
        row = conn.execute("SELECT * FROM bases_licitud_catalog WHERE id = ?", [new_id]).fetchone()
        conn.close()
        return {"id": row[0], "nombre": row[1], "descripcion": row[2], "referencia_legal": row[3]}
    except Exception as e:
        conn.close()
        raise HTTPException(400, f"Error al crear base de licitud: {str(e)}")


# ─── Asignaciones (Taxonomía por Actividad) ───────────────────────────────


@router.get("/asignaciones", response_model=list[TaxonomiaAsignacionOut])
def listar_asignaciones(actividad_id: Optional[int] = Query(None)):
    """Obtiene las asignaciones de taxonomía para una actividad.
    Si no se especifica actividad_id, retorna todas las asignaciones."""
    conn = get_connection()
    if actividad_id:
        rows = conn.execute(
            "SELECT * FROM taxonomia_asignaciones WHERE actividad_id = ? ORDER BY id",
            [actividad_id]
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM taxonomia_asignaciones ORDER BY id").fetchall()
    conn.close()
    return [{"id": r[0], "actividad_id": r[1], "categoria_id": r[2], "finalidad_id": r[3], "base_id": r[4]} for r in rows]


@router.post("/asignaciones", response_model=TaxonomiaAsignacionOut, status_code=201)
def crear_asignacion(data: TaxonomiaAsignacionCreate):
    """Asigna una combinación de categoría + finalidad + base de licitud a una actividad."""
    conn = get_connection()

    # Validar que la actividad existe
    act = conn.execute("SELECT id FROM actividades WHERE id = ?", [data.actividad_id]).fetchone()
    if not act:
        conn.close()
        raise HTTPException(404, f"Actividad {data.actividad_id} no encontrada")

    # Validar que los IDs de catálogo existen
    cat = conn.execute("SELECT id FROM categorias_datos_catalog WHERE id = ?", [data.categoria_id]).fetchone()
    if not cat:
        conn.close()
        raise HTTPException(404, f"Categoría de datos {data.categoria_id} no encontrada")

    fin = conn.execute("SELECT id FROM finalidades_catalog WHERE id = ?", [data.finalidad_id]).fetchone()
    if not fin:
        conn.close()
        raise HTTPException(404, f"Finalidad {data.finalidad_id} no encontrada")

    base = conn.execute("SELECT id FROM bases_licitud_catalog WHERE id = ?", [data.base_id]).fetchone()
    if not base:
        conn.close()
        raise HTTPException(404, f"Base de licitud {data.base_id} no encontrada")

    try:
        result = conn.execute(
            """INSERT INTO taxonomia_asignaciones (actividad_id, categoria_id, finalidad_id, base_id)
               VALUES (?, ?, ?, ?) RETURNING id""",
            [data.actividad_id, data.categoria_id, data.finalidad_id, data.base_id]
        )
        new_id = result.fetchone()[0]
        row = conn.execute("SELECT * FROM taxonomia_asignaciones WHERE id = ?", [new_id]).fetchone()
        conn.close()
        return {"id": row[0], "actividad_id": row[1], "categoria_id": row[2], "finalidad_id": row[3], "base_id": row[4]}
    except Exception as e:
        conn.close()
        raise HTTPException(400, f"Error al crear asignación: {str(e)}")
