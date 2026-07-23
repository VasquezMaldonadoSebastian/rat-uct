u"""
RAT UCT - Funciones helper compartidas para la API
===================================================

Constantes, conversores de filas, sanitizacion generica y motor de evaluacion de riesgo.
"""

import datetime


# --- Sanitizacion generica de filas DuckDB ---


def sanitize_row(cols, row, defaults=None, coerce_bool=None):
    """Convierte una fila DuckDB (tupla) a dict, sanitizando NULLs y tipos.

    Args:
        cols: Lista de nombres de columnas.
        row: Tupla de valores DuckDB.
        defaults: Dict {nombre_campo: valor_default} para campos NULL.
        coerce_bool: Set de campos que deben convertirse a bool explicitamente.

    Returns:
        Dict con valores sanitizados para Pydantic.
    """
    if defaults is None:
        defaults = {}
    if coerce_bool is None:
        coerce_bool = set()

    d = {}
    for i, c in enumerate(cols):
        v = row[i] if i < len(row) else None
        if v is None:
            d[c] = defaults.get(c, v)
        elif c in coerce_bool:
            d[c] = bool(v)
        elif isinstance(v, datetime.date):
            d[c] = v.isoformat()
        elif isinstance(v, list):
            d[c] = list(v)
        else:
            d[c] = v
    return d


# --- Constantes de serializacion ---

COLUMNAS_ACTIVIDADES = [
    "id", "actividad_tratamiento", "responsable_tratamiento", "responsable_rut",
    "responsable_domicilio", "responsable_representante", "dpo_contacto",
    "areas_intervienen", "finalidad", "descripcion",
    "categoria_titulares", "categorias_datos", "datos_sensibles",
    "origen_fuente", "categoria_destinatarios", "base_licitud",
    "transferencia_internacional", "pais_destino", "garantias_transferencia",
    "plazo_conservacion", "justificacion_conservacion", "medidas_seguridad",
    "decisiones_automatizadas", "requiere_eipd", "nivel_riesgo",
    "score_actividad", "estado",
    "created_at", "updated_at",
]

# Valores por defecto cuando el campo es NULL
DEFAULT_NULL = {
    "descripcion": "", "origen_fuente": "", "medidas_seguridad": "",
    "justificacion_conservacion": "", "responsable_rut": "",
    "responsable_domicilio": "", "responsable_representante": "",
    "pais_destino": "", "garant\u00edas_transferencia": "",
}
DEFAULT_EMPTY_LIST = {"areas_intervienen", "categoria_titulares", "categorias_datos", "categoria_destinatarios"}
DEFAULT_FALSE = {"datos_sensibles", "requiere_eipd"}
DEFAULT_NO_APLICA = {"transferencia_internacional", "decisiones_automatizadas"}


# --- Conversores de filas ---

def row_to_actividad(row, columns=None):
    """Convierte una fila DuckDB (tupla) a dict serializable."""
    if row is None:
        return None
    if columns is None:
        columns = COLUMNAS_ACTIVIDADES
    d = {}
    for i, k in enumerate(columns):
        val = row[i] if i < len(row) else None
        if isinstance(val, list):
            d[k] = list(val)
        elif val is None:
            if k in DEFAULT_NULL:
                d[k] = ""
            elif k in DEFAULT_EMPTY_LIST:
                d[k] = []
            elif k in DEFAULT_FALSE:
                d[k] = False
            elif k in DEFAULT_NO_APLICA:
                d[k] = "No aplica"
            elif k == "estado":
                d[k] = "activo"
            else:
                d[k] = val
        else:
            d[k] = val
    return d


def fetch_one_dict(conn, sql, params=None, columns=None):
    """Ejecuta SELECT y retorna un dict."""
    if params:
        result = conn.execute(sql, params)
    else:
        result = conn.execute(sql)
    cols = [desc[0] for desc in result.description]
    row = result.fetchone()
    return row_to_actividad(row, cols) if row else None


def fetch_all_dict(conn, sql, params=None, columns=None):
    """Ejecuta SELECT y retorna lista de dicts."""
    if params:
        result = conn.execute(sql, params)
    else:
        result = conn.execute(sql)
    cols = [desc[0] for desc in result.description]
    return [row_to_actividad(r, cols) for r in result.fetchall()]


# --- Motor de evaluacion de riesgo ---

def evaluar_riesgo_actividad(actividad: dict) -> dict:
    """Evalúa el nivel de riesgo y score de cumplimiento de una actividad."""
    cats = [d.lower() for d in actividad.get("categorias_datos", [])]
    titulares = [t.lower() for t in actividad.get("categoria_titulares", [])]
    transfer = actividad.get("transferencia_internacional", "").lower()
    decisions = actividad.get("decisiones_automatizadas", "").lower()
    sensibles = actividad.get("datos_sensibles", False)

    factores = []
    nivel = "bajo"

    # Reglas: crítico
    if any(p in " ".join(cats) for p in ["salud", "biométric", "biometric", "racial", "étnico", "etnico", "ideología", "ideologia", "sexual", "vida sexual"]):
        nivel = "crítico"
        factores.append("Datos sensibles (salud/biométricos/íntimos)")
    if any("nna" in t or "menor" in t or "niño" in t or "nino" in t for t in titulares):
        if nivel != "crítico":
            nivel = "crítico"
        factores.append("Involucra NNA (menores de edad)")
    if sensibles and transfer and transfer != "no aplica":
        if nivel != "crítico":
            nivel = "crítico"
        factores.append("Datos sensibles + transferencia internacional")

    # Reglas: alto
    if sensibles and nivel == "bajo":
        nivel = "alto"
        factores.append("Datos sensibles")
    if nivel == "bajo" and any("gran escala" in d or "financiero" in d for d in cats):
        nivel = "alto"
        factores.append("Posible gran escala")

    # Reglas: medio
    if transfer and transfer != "no aplica" and nivel == "bajo":
        nivel = "medio"
        factores.append("Transferencia internacional")
    if decisions and decisions != "no aplica" and nivel == "bajo":
        nivel = "medio"
        factores.append("Decisiones automatizadas")
    if actividad.get("requiere_eipd", False) and nivel == "bajo":
        nivel = "medio"
        factores.append("Requiere EIPD")

    # Score de cumplimiento (0-100)
    score = 100
    penalizaciones = {
        "crítico": 40,
        "alto": 25,
        "medio": 10,
        "bajo": 0,
    }
    score -= penalizaciones.get(nivel, 0)

    # Penalizaciones adicionales
    if not actividad.get("medidas_seguridad"):
        score -= 10
    if not actividad.get("plazo_conservacion"):
        score -= 10
    if not actividad.get("justificacion_conservacion"):
        score -= 5
    if not actividad.get("origen_fuente"):
        score -= 5
    if transfer and transfer != "no aplica" and not actividad.get("garantias_transferencia"):
        score -= 10

    score = max(0, min(100, score))

    return {
        "nivel_riesgo": nivel,
        "score_actividad": score,
        "factores": factores,
    }
