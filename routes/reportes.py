"""
RAT UCT — Reportes (resumen ejecutivo y monitoreo)
====================================================

Reportes agregados para fiscalización APDP y monitoreo interno.
Incluye matriz de riesgo y score de cumplimiento global.
"""

from fastapi import APIRouter

from database import get_connection

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])


@router.get("/resumen")
def reporte_resumen():
    """Resumen ejecutivo del RAT para fiscalización."""
    conn = get_connection()
    total = conn.execute("SELECT count(*) FROM actividades").fetchone()[0]
    por_base = conn.execute(
        "SELECT base_licitud, count(*) as cnt FROM actividades GROUP BY base_licitud ORDER BY cnt DESC"
    ).fetchall()
    por_area = conn.execute(
        "SELECT t.area, count(*) as cnt FROM (SELECT UNNEST(ifnull(areas_intervienen, [])) as area FROM actividades) t WHERE t.area IS NOT NULL GROUP BY t.area ORDER BY cnt DESC"
    ).fetchall()
    por_titular = conn.execute(
        "SELECT t.titular, count(*) as cnt FROM (SELECT UNNEST(ifnull(categoria_titulares, [])) as titular FROM actividades) t WHERE t.titular IS NOT NULL GROUP BY t.titular ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {
        "total_actividades": total,
        "por_base_legal": {r[0]: r[1] for r in por_base},
        "por_area": {r[0]: r[1] for r in por_area},
        "por_titular": {r[0]: r[1] for r in por_titular},
    }


@router.get("/dpa-pendientes")
def reporte_dpa_pendientes():
    """Encargados externos que aún no tienen DPA generado."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM encargados WHERE dpa_generado = false AND pais != 'Chile' ORDER BY nombre"
    ).fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "rut": r[2], "pais": r[3], "servicio": r[4],
             "dpa_generado": bool(r[5])} for r in rows]


@router.get("/matriz-riesgo")
def matriz_riesgo():
    """Matriz de riesgo: distribución por nivel y por área."""
    conn = get_connection()
    por_nivel = conn.execute(
        "SELECT nivel_riesgo, count(*) as cnt FROM actividades GROUP BY nivel_riesgo ORDER BY cnt DESC"
    ).fetchall()

    por_area_nivel = conn.execute(
        "SELECT t.area, t.nivel, count(*) as cnt FROM "
        "(SELECT UNNEST(ifnull(areas_intervienen, [])) as area, nivel_riesgo as nivel FROM actividades) t "
        "WHERE t.area IS NOT NULL GROUP BY t.area, t.nivel ORDER BY t.area"
    ).fetchall()

    heatmap = {}
    for area, nivel, cnt in por_area_nivel:
        if area not in heatmap:
            heatmap[area] = {"crítico": 0, "alto": 0, "medio": 0, "bajo": 0}
        heatmap[area][nivel] = cnt

    conn.close()
    return {
        "por_nivel": {r[0]: r[1] for r in por_nivel},
        "heatmap": heatmap,
    }


@router.get("/score")
def reporte_score():
    """Score de cumplimiento global y por área."""
    conn = get_connection()
    # Score global
    scores = conn.execute("SELECT score_actividad FROM actividades WHERE score_actividad IS NOT NULL").fetchall()
    score_global = round(sum(s[0] for s in scores) / len(scores)) if scores else 0

    # Score por área
    por_area = conn.execute(
        "SELECT t.area, avg(a.score_actividad) as score_avg, count(*) as cnt "
        "FROM actividades a, LATERAL UNNEST(ifnull(a.areas_intervienen, [])) as t(area) "
        "WHERE a.score_actividad IS NOT NULL AND t.area IS NOT NULL "
        "GROUP BY t.area ORDER BY score_avg DESC"
    ).fetchall()

    # Score por nivel de riesgo
    por_riesgo = conn.execute(
        "SELECT nivel_riesgo, count(*) as cnt, avg(score_actividad) as score_avg "
        "FROM actividades WHERE nivel_riesgo IS NOT NULL "
        "GROUP BY nivel_riesgo ORDER BY "
        "CASE nivel_riesgo WHEN 'bajo' THEN 1 WHEN 'medio' THEN 2 WHEN 'alto' THEN 3 WHEN 'crítico' THEN 4 END"
    ).fetchall()

    conn.close()
    return {
        "score_global": score_global,
        "total_evaluadas": len(scores),
        "por_area": [{"area": r[0], "score": round(r[1]), "actividades": r[2]} for r in por_area],
        "por_nivel_riesgo": [{"nivel": r[0], "count": r[1], "score_promedio": round(r[2]) if r[2] else 0} for r in por_riesgo],
    }
