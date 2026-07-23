"""
RAT UCT — Conexión y esquema DuckDB
====================================

Gestiona la base de datos DuckDB embebida (rat_uct.db) con 8 tablas:
  1. actividades     — 30 columnas, tabla principal del RAT
  2. areas           — Catálogo de unidades UCT (12 sembradas)
  3. procesos        — Macroprocesos institucionales
  4. encargados      — Destinatarios externos de datos
  5. bitacora        — Trazabilidad de cambios (auditoría)
  6. eipd            — Evaluaciones de Impacto (4 pasos)
  7. brechas         — Incidentes de seguridad (alerta 72h)
  8. solicitudes_arsop — Derechos ARCOP (SLA 30 días)

Basado en la planilla RAT_UCT_v1_Julio_2026.xlsx (15 columnas originales
+ 11 columnas agregadas: riesgo, score, EIPD, brechas, ARCOP, DPA).

Uso:
    python database.py   # Inicializa/esquema + seed de áreas
"""

import duckdb
import os
from pathlib import Path

DB_PATH = Path(os.environ.get("DB_PATH", str(Path(__file__).parent / "rat_uct.db")))


def get_connection():
    """Obtiene conexión DuckDB (singleton por proceso)."""
    conn = duckdb.connect(str(DB_PATH))
    conn.execute("SET TimeZone = 'America/Santiago'")
    return conn


def init_db(conn=None):
    """Inicializa el esquema completo de la base de datos.

    Crea las 8 tablas si no existen y ejecuta migraciones incrementales
    para columnas agregadas después del despliegue inicial (nivel_riesgo,
    score_actividad). Es idempotente: puede ejecutarse múltiples veces
    sin pérdida de datos.

    Tablas creadas:
      1. actividades — Actividades de tratamiento (30 columnas)
      2. areas — Catálogo de unidades UCT
      3. procesos — Macroprocesos institucionales
      4. encargados — Destinatarios externos
      5. bitacora — Trazabilidad de cambios
      6. eipd — Evaluaciones de Impacto (4 pasos)
      7. brechas — Incidentes de seguridad
      |      8. solicitudes_arsop — Derechos ARSOP

    Retorna la conexión DuckDB activa."""
    if conn is None:
        conn = get_connection()

    # Tabla principal: actividades de tratamiento
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_actividades START 1;
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
            actividad_tratamiento VARCHAR NOT NULL,
            responsable_tratamiento VARCHAR DEFAULT 'UCT — Universidad Católica de Temuco',
            responsable_rut VARCHAR DEFAULT 'XX.XXX.XXX-X',
            responsable_domicilio VARCHAR DEFAULT 'Manuel Montt 56, Temuco, Chile',
            responsable_representante VARCHAR DEFAULT 'Rector UCT',
            dpo_contacto VARCHAR DEFAULT 'dpo@uct.cl',
            areas_intervienen VARCHAR[],  -- Array de áreas/unidades
            finalidad VARCHAR NOT NULL,
            descripcion VARCHAR,
            categoria_titulares VARCHAR[],
            categorias_datos VARCHAR[],
            datos_sensibles BOOLEAN DEFAULT FALSE,
            origen_fuente VARCHAR,
            categoria_destinatarios VARCHAR[],
            base_licitud VARCHAR NOT NULL,
            transferencia_internacional VARCHAR DEFAULT 'No aplica',
            pais_destino VARCHAR,
            garantías_transferencia VARCHAR,
            plazo_conservacion VARCHAR NOT NULL,
            justificacion_conservacion VARCHAR,
            medidas_seguridad VARCHAR,
            decisiones_automatizadas VARCHAR DEFAULT 'No aplica',
            requiere_eipd BOOLEAN DEFAULT FALSE,
            nivel_riesgo VARCHAR DEFAULT 'bajo',  -- bajo, medio, alto, crítico
            score_actividad INTEGER DEFAULT NULL,  -- 0-100
            estado VARCHAR DEFAULT 'activo',  -- activo, revisión, archivado
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Catálogo de áreas/unidades UCT
    conn.execute("""
        CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
            nombre VARCHAR NOT NULL UNIQUE,
            descripcion VARCHAR,
            tipo VARCHAR DEFAULT 'unidad'  -- facultad, dirección, unidad, carrera
        );
    """)

    # Catálogo de procesos institucionales
    conn.execute("""
        CREATE TABLE IF NOT EXISTS procesos (
            id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
            nombre VARCHAR NOT NULL,
            macroproceso VARCHAR,  -- ej: Académico, Financiero, Gestión de Personas
            descripcion VARCHAR,
            actividades_ids INTEGER[]  -- IDs de actividades RAT asociadas
        );
    """)

    # Catálogo de encargados externos (destinatarios externos frecuentes)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS encargados (
            id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
            nombre VARCHAR NOT NULL UNIQUE,
            rut VARCHAR,
            pais VARCHAR DEFAULT 'Chile',
            servicio VARCHAR,
            dpa_generado BOOLEAN DEFAULT FALSE,  -- Data Processing Agreement
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Bitácora de cambios
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bitacora (
            id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
            actividad_id INTEGER,
            campo_modificado VARCHAR,
            valor_anterior VARCHAR,
            valor_nuevo VARCHAR,
            modificado_por VARCHAR DEFAULT 'sistema',
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # EIPD — Evaluación de Impacto en Protección de Datos
    conn.execute("""
        CREATE TABLE IF NOT EXISTS eipd (
            id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
            actividad_id INTEGER NOT NULL,
            estado VARCHAR DEFAULT 'borrador',
            necesita_eipd BOOLEAN,
            motivo_activacion VARCHAR,
            riesgo_inherente VARCHAR,
            riesgo_residual VARCHAR,
            medidas_propuestas VARCHAR,
            medidas_implementadas VARCHAR,
            aprobado_por VARCHAR,
            fecha_aprobacion DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Brechas de seguridad
    conn.execute("""
        CREATE TABLE IF NOT EXISTS brechas (
            id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
            actividad_id INTEGER,
            titulo VARCHAR NOT NULL,
            descripcion VARCHAR,
            fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_notificacion TIMESTAMP,
            plazo_notificacion TIMESTAMP,
            severidad VARCHAR DEFAULT 'media',
            tipo_incidente VARCHAR,
            datos_afectados VARCHAR,
            titulares_afectados INTEGER,
            medidas_correctivas VARCHAR,
            notificado_apdp BOOLEAN DEFAULT FALSE,
            notificado_titulares BOOLEAN DEFAULT FALSE,
            estado VARCHAR DEFAULT 'abierta',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Solicitudes ARCOP
    conn.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes_arsop (
            id INTEGER PRIMARY KEY DEFAULT nextval('seq_actividades'),
            tipo_derecho VARCHAR NOT NULL,
            solicitante_nombre VARCHAR,
            solicitante_email VARCHAR,
            solicitante_rut VARCHAR,
            descripcion VARCHAR,
            actividad_id INTEGER,
            fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_vencimiento TIMESTAMP,
            estado VARCHAR DEFAULT 'recibida',
            respuesta VARCHAR,
            fecha_respuesta TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    print("✅ Esquema inicializado correctamente")

    # Migraciones (columnas nuevas añadidas después de la creación inicial)
    try:
        conn.execute("ALTER TABLE actividades ADD COLUMN nivel_riesgo VARCHAR DEFAULT 'bajo'")
        print("  ↪ migración: nivel_riesgo agregada")
    except Exception:
        pass  # ya existe
    try:
        conn.execute("ALTER TABLE actividades ADD COLUMN score_actividad INTEGER DEFAULT NULL")
        print("  ↪ migración: score_actividad agregada")
    except Exception:
        pass
    # Migración: solicitudes_arcop → solicitudes_arsop
    try:
        conn.execute("ALTER TABLE solicitudes_arcop RENAME TO solicitudes_arsop")
        print("  ↪ migración: solicitudes_arcop → solicitudes_arsop")
    except Exception:
        pass
    return conn


def seed_areas_uct(conn):
    """Siembra 12 áreas/unidades típicas de la Universidad Católica de Temuco.

    Solo ejecuta si la tabla está vacía (idempotente). Las áreas sembradas son:
    CERETI, Admisión, Finanzas, TI, RRHH, Investigación, Biblioteca,
    Bienestar Estudiantil, Docencia, Vinculación, Marketing, Jurídica.

    Cada área tiene: nombre, descripción y tipo (dirección/unidad/vicerrectoría)."""
    areas_existentes = conn.execute("SELECT count(*) FROM areas").fetchone()[0]
    if areas_existentes > 0:
        print("ℹ️  Áreas ya existen, saltando seed")
        return

    areas = [
        ("CERETI", "Centro de Recursos para Estudiantes con Discapacidad", "unidad"),
        ("Admisión", "Dirección de Admisión y Registro Académico", "dirección"),
        ("Finanzas", "Dirección de Finanzas", "dirección"),
        ("TI", "Dirección de Tecnologías de Información", "dirección"),
        ("RRHH", "Dirección de Gestión de Personas", "dirección"),
        ("Investigación", "Dirección de Investigación", "dirección"),
        ("Biblioteca", "Sistema de Bibliotecas UCT", "unidad"),
        ("Bienestar Estudiantil", "Dirección de Asuntos Estudiantiles", "dirección"),
        ("Docencia", "Vicerrectoría Académica", "vicerrectoría"),
        ("Vinculación", "Dirección de Vinculación con el Medio", "dirección"),
        ("Marketing", "Dirección de Comunicaciones y Marketing", "dirección"),
        ("Jurídica", "Dirección Jurídica", "dirección"),
    ]
    conn.executemany(
        "INSERT INTO areas (nombre, descripcion, tipo) VALUES (?, ?, ?)",
        areas
    )
    print(f"✅ {len(areas)} áreas sembradas")


if __name__ == "__main__":
    conn = init_db()
    seed_areas_uct(conn)
    print("📦 Base de datos lista en:", DB_PATH)
    conn.close()
