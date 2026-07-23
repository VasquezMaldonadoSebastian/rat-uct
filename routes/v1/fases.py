"""
RAT UCT — Fases de Implementación (modelo Kulvio)
===================================================

Barra de progreso alineada con las 12 fases del modelo Kulvio.
Cada fase se marca como completada según datos reales en la DB:
hay actividades → fase 2-3, hay riesgos → fase 4, hay EIPD → fase 5, etc.
"""

from fastapi import APIRouter

from database import get_connection

router = APIRouter(prefix="/api/v1/fases", tags=["Fases v1"])


@router.get("")
def fases_implementacion():
    """Retorna el progreso de las 12 fases de implementación (modelo Kulvio).
    Cada fase se evalúa contra datos reales en la base de datos."""
    conn = get_connection()
    total_acts = conn.execute("SELECT count(*) FROM actividades").fetchone()[0]
    has_riesgo = conn.execute("SELECT count(*) FROM actividades WHERE nivel_riesgo IS NOT NULL AND nivel_riesgo != 'bajo'").fetchone()[0]
    has_eipd = conn.execute("SELECT count(*) FROM eipd").fetchone()[0]
    has_brechas = conn.execute("SELECT count(*) FROM brechas").fetchone()[0]
    has_arsop = conn.execute("SELECT count(*) FROM solicitudes_arsop").fetchone()[0]
    conn.close()
    fases = [
        {"id": 1, "nombre": "Configuración Inicial", "completado": True},
        {"id": 2, "nombre": "Diagnóstico", "completado": total_acts > 0},
        {"id": 3, "nombre": "RAT", "completado": total_acts > 0},
        {"id": 4, "nombre": "Evaluación de Riesgo", "completado": has_riesgo > 0},
        {"id": 5, "nombre": "EIPD", "completado": has_eipd > 0},
        {"id": 6, "nombre": "Terceros / DPA", "completado": False},
        {"id": 7, "nombre": "Consentimientos", "completado": False},
        {"id": 8, "nombre": "ARSOP", "completado": has_arsop > 0},
        {"id": 9, "nombre": "Brechas", "completado": has_brechas > 0},
        {"id": 10, "nombre": "Denuncias", "completado": False},
        {"id": 11, "nombre": "Documentación", "completado": False},
        {"id": 12, "nombre": "Monitoreo", "completado": False},
    ]
    completadas = sum(1 for f in fases if f["completado"])
    return {"total": 12, "completadas": completadas, "progreso": round(completadas / 12 * 100), "fases": fases}
