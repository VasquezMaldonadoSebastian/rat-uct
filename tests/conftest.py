"""
RAT UCT — Pytest fixtures y configuración de tests
===================================================

Configura una base DuckDB en memoria (:memory:) con datos de prueba
y un TestClient de FastAPI para todos los tests.
"""

import os
os.environ["DB_PATH"] = ":memory:"

import duckdb
import pytest
from fastapi.testclient import TestClient


# ── Wrapper para evitar que los handlers cierren la singleton ──────────────
class _NoCloseConn:
    """Delega todos los atributos a DuckDBConnection, pero ignora close()."""
    def __init__(self, conn):
        object.__setattr__(self, "_conn", conn)

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_conn"), name)

    def close(self):
        pass  # no-op: no cerrar la singleton


# ── Singleton in-memory DuckDB ──────────────────────────────────────────────
_raw_conn = duckdb.connect(":memory:")
_test_conn = _NoCloseConn(_raw_conn)

# Parcheamos get_connection ANTES de importar routes
import database

database.get_connection = lambda: _test_conn

# Importamos app (routes cargarán get_connection ya parcheado)
from app import app  # noqa: E402
from database import init_db, seed_areas_uct  # noqa: E402


# ── Helpers para IDs dinámicos ──────────────────────────────────────────────
def _get_actividad_id(conn, idx: int = 0) -> int:
    """Retorna el ID de la idx-ésima actividad (0 = primera)."""
    return conn.execute(
        "SELECT id FROM actividades ORDER BY id LIMIT 1 OFFSET ?", [idx]
    ).fetchone()[0]


def _get_eipd_id(conn, idx: int = 0) -> int:
    return conn.execute(
        "SELECT id FROM eipd ORDER BY id LIMIT 1 OFFSET ?", [idx]
    ).fetchone()[0]


def _get_brecha_id(conn, idx: int = 0) -> int:
    return conn.execute(
        "SELECT id FROM brechas ORDER BY id LIMIT 1 OFFSET ?", [idx]
    ).fetchone()[0]


def _get_arsop_id(conn, idx: int = 0) -> int:
    return conn.execute(
        "SELECT id FROM solicitudes_arsop ORDER BY id LIMIT 1 OFFSET ?", [idx]
    ).fetchone()[0]


# ── Seed de datos de prueba ─────────────────────────────────────────────────
def _seed_data(conn):
    """Inserta datos de prueba usando IDs explícitos para evitar
    la interferencia del sequence compartido entre tablas."""
    # Actividades con IDs explícitos
    conn.execute(
        """INSERT INTO actividades (
            id, actividad_tratamiento, finalidad, descripcion, base_licitud,
            plazo_conservacion, estado, areas_intervienen, categoria_titulares,
            categorias_datos
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            1,
            "Gestión de matrícula estudiantil",
            "Gestión académica y administrativa de matrícula",
            "Registro y control de matrícula de estudiantes",
            "Consentimiento",
            "5 años",
            "activo",
            ["Admisión", "TI"],
            ["Estudiantes"],
            ["Nombre", "RUT", "Dirección"],
        ],
    )
    conn.execute(
        """INSERT INTO actividades (
            id, actividad_tratamiento, finalidad, descripcion, base_licitud,
            plazo_conservacion, estado, datos_sensibles,
            transferencia_internacional, pais_destino, areas_intervienen,
            categoria_titulares, categorias_datos
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            2,
            "Investigación científica",
            "Fomento de la investigación y publicaciones",
            "Gestión de proyectos de investigación",
            "Interés legítimo",
            "10 años",
            "activo",
            True,
            "Sí - Unión Europea",
            "España",
            ["Investigación"],
            ["Investigadores", "Estudiantes"],
            ["Nombre", "RUT", "Publicaciones"],
        ],
    )

    # 1 área adicional con ID explícito
    conn.execute(
        "INSERT INTO areas (id, nombre, descripcion, tipo) VALUES (?, ?, ?, ?)",
        [100, "Test Area", "Área de prueba para tests", "unidad"],
    )

    # 1 EIPD con ID explícito
    conn.execute(
        "INSERT INTO eipd (id, actividad_id, estado, necesita_eipd, motivo_activacion) "
        "VALUES (?, ?, ?, ?, ?)",
        [1, 1, "borrador", True, "Tratamiento de datos sensibles a gran escala"],
    )

    # 1 Brecha con ID explícito
    conn.execute(
        "INSERT INTO brechas (id, actividad_id, titulo, descripcion, severidad, estado) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [1, 1, "Acceso no autorizado", "Posible fuga por credenciales expuestas",
         "alta", "abierta"],
    )

    # 1 ARSOP con ID explícito
    conn.execute(
        "INSERT INTO solicitudes_arsop (id, tipo_derecho, solicitante_nombre, "
        "solicitante_email, descripcion, estado) VALUES (?, ?, ?, ?, ?, ?)",
        [1, "Acceso", "Juan Pérez", "juan@example.com",
         "Solicita acceso a sus datos personales", "recibida"],
    )

    # La sequence no se modifica aquí; las tablas dependen de ella.
    # Los nuevos registros creados por los tests usarán el sequence,
    # que continúa desde donde quedó tras seed_areas_uct.


def _reset_db():
    """Elimina todo y recrea esquema + seed."""
    # Drop child tables first (FK constraints)
    _raw_conn.execute("DROP TABLE IF EXISTS taxonomia_asignaciones")
    _raw_conn.execute("DROP TABLE IF EXISTS categorias_datos_catalog")
    _raw_conn.execute("DROP TABLE IF EXISTS finalidades_catalog")
    _raw_conn.execute("DROP TABLE IF EXISTS bases_licitud_catalog")
    _raw_conn.execute("DROP TABLE IF EXISTS actividades")
    _raw_conn.execute("DROP TABLE IF EXISTS areas")
    _raw_conn.execute("DROP TABLE IF EXISTS procesos")
    _raw_conn.execute("DROP TABLE IF EXISTS encargados")
    _raw_conn.execute("DROP TABLE IF EXISTS bitacora")
    _raw_conn.execute("DROP TABLE IF EXISTS eipd")
    _raw_conn.execute("DROP TABLE IF EXISTS brechas")
    _raw_conn.execute("DROP TABLE IF EXISTS solicitudes_arsop")
    _raw_conn.execute("DROP SEQUENCE IF EXISTS seq_actividades")

    init_db(_test_conn)
    seed_areas_uct(_test_conn)
    _seed_data(_test_conn)


# ── Fixtures compartidos ────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def setup_db():
    """Antes de cada test, resetea la base y siembra datos de prueba."""
    _reset_db()
    yield


@pytest.fixture
def client():
    """TestClient de FastAPI con base en memoria."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_conn():
    """Acceso directo a la conexión DuckDB para asserts y consulta de IDs."""
    return _raw_conn


@pytest.fixture
def act_id(db_conn):
    """ID de la primera actividad de prueba."""
    return _get_actividad_id(db_conn, 0)


@pytest.fixture
def act_id2(db_conn):
    """ID de la segunda actividad de prueba."""
    return _get_actividad_id(db_conn, 1)


@pytest.fixture
def eipd_id(db_conn):
    """ID de la EIPD de prueba."""
    return _get_eipd_id(db_conn, 0)


@pytest.fixture
def brecha_id(db_conn):
    """ID de la brecha de prueba."""
    return _get_brecha_id(db_conn, 0)


@pytest.fixture
def arsop_id(db_conn):
    """ID de la solicitud ARSOP de prueba."""
    return _get_arsop_id(db_conn, 0)
