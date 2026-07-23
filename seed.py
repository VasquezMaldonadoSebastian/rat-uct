"""
Seed: Carga la actividad de ejemplo del Excel RAT_UCT_v1 al DuckDB
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from database import get_connection, init_db, seed_areas_uct


def seed_from_excel(excel_path: str):
    """Carga actividades desde el Excel RAT."""
    conn = get_connection()
    init_db(conn)
    seed_areas_uct(conn)

    # Verificar si ya hay datos
    count = conn.execute("SELECT count(*) FROM actividades").fetchone()[0]
    if count > 0:
        print(f"ℹ️  Ya existen {count} actividades. Para recargar, ejecuta con --force")
        if "--force" not in sys.argv:
            conn.close()
            return

    df = pd.read_excel(excel_path, sheet_name="RAT", header=0)

    # Mapeo de columnas del Excel a columnas DB
    col_map = {
        "ACTIVIDAD DE TRATAMIENTO": "actividad_tratamiento",
        "RESPONSABLE DEL TRATAMIENTO": "responsable_tratamiento",
        "DELEGADO DE PROTECCIÓN DE DATOS (DPO)": "dpo_contacto",
        "ÁREAS QUE INTERVIENEN": "areas_intervienen",
        "FINALIDAD DEL TRATAMIENTO": "finalidad",
        "DESCRIPCIÓN DE LA ACTIVIDAD": "descripcion",
        "CATEGORÍA DE TITULARES": "categoria_titulares",
        "CATEGORÍAS DE DATOS TRATADOS": "categorias_datos",
        "ORIGEN O FUENTE DE LOS DATOS": "origen_fuente",
        "CATEGORÍA DE DESTINATARIOS": "categoria_destinatarios",
        "BASE DE LICITUD": "base_licitud",
        "TRANSFERENCIA INTERNACIONAL": "transferencia_internacional",
        "PLAZO DE CONSERVACIÓN": "plazo_conservacion",
        "MEDIDAS DE SEGURIDAD": "medidas_seguridad",
        "DECISIONES AUTOMATIZADAS": "decisiones_automatizadas",
    }

    insertadas = 0
    for _, row in df.iterrows():
        if pd.isna(row.iloc[0]):  # Saltar filas vacías
            continue

        # Construir dict para insert
        vals = {}
        for excel_col, db_col in col_map.items():
            raw = row.get(excel_col, "")
            if pd.isna(raw):
                vals[db_col] = ""
            elif db_col in ("areas_intervienen", "categoria_titulares",
                            "categorias_datos", "categoria_destinatarios"):
                # Convertir strings separados por comas a listas
                if isinstance(raw, str):
                    vals[db_col] = [x.strip() for x in raw.split(",") if x.strip()]
                else:
                    vals[db_col] = [str(raw)]
            else:
                vals[db_col] = str(raw).strip()

        # Determinar si tiene datos sensibles
        cat_datos = vals.get("categorias_datos", [])
        tiene_sensibles = any("sensible" in d.lower() for d in cat_datos) if isinstance(cat_datos, list) else False

        conn.execute("""
            INSERT INTO actividades (
                actividad_tratamiento, responsable_tratamiento, dpo_contacto,
                areas_intervienen, finalidad, descripcion,
                categoria_titulares, categorias_datos, datos_sensibles,
                origen_fuente, categoria_destinatarios, base_licitud,
                transferencia_internacional, plazo_conservacion,
                medidas_seguridad, decisiones_automatizadas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vals.get("actividad_tratamiento", ""),
            vals.get("responsable_tratamiento", "UCT — Universidad Católica de Temuco"),
            vals.get("dpo_contacto", "dpo@uct.cl"),
            vals.get("areas_intervienen", []),
            vals.get("finalidad", ""),
            vals.get("descripcion", ""),
            vals.get("categoria_titulares", []),
            vals.get("categorias_datos", []),
            tiene_sensibles,
            vals.get("origen_fuente", ""),
            vals.get("categoria_destinatarios", []),
            vals.get("base_licitud", ""),
            vals.get("transferencia_internacional", "No aplica"),
            vals.get("plazo_conservacion", ""),
            vals.get("medidas_seguridad", ""),
            vals.get("decisiones_automatizadas", "No aplica"),
        ))
        insertadas += 1
        print(f"  ✅ {vals.get('actividad_tratamiento', '?')}")

    conn.close()
    print(f"\n📦 {insertadas} actividades cargadas desde el Excel")


if __name__ == "__main__":
    excel_path = os.path.join(os.path.dirname(__file__), "RAT_UCT_v1_Julio_2026.xlsx")
    if not os.path.exists(excel_path):
        print(f"❌ No se encuentra el Excel en: {excel_path}")
        sys.exit(1)
    seed_from_excel(excel_path)
