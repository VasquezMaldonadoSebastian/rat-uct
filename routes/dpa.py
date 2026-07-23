"""
RAT UCT — DPA (Data Processing Agreement)
===========================================

Data Processing Agreement (DPA) — acuerdo de encargo de tratamiento
con terceros. Genera un placeholder textual; pendiente: PDF real con
firma digital y hash SHA-256 para cadena de custodia.
"""

from fastapi import APIRouter, HTTPException

from database import get_connection

router = APIRouter(prefix="/api/dpa", tags=["DPA"])


@router.post("/generar/{encargado_id}")
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
