"""
RAT UCT — Tests del motor de evaluación de riesgo
==================================================

Cubre:
- POST /api/actividades/{id}/evaluar-riesgo (endpoint)
- evaluar_riesgo_actividad() en utils.py (tests unitarios directos)
"""

import pytest
from utils import evaluar_riesgo_actividad


class TestEvaluarRiesgoEndpoint:
    """POST /api/actividades/{id}/evaluar-riesgo"""

    def test_evaluar_actividad_existente(self, client, act_id):
        """Evaluar riesgo de una actividad existente."""
        resp = client.post(f"/api/actividades/{act_id}/evaluar-riesgo")
        assert resp.status_code == 200
        data = resp.json()
        assert "nivel_riesgo" in data
        assert "score_actividad" in data
        assert "factores" in data
        assert isinstance(data["score_actividad"], int)
        assert 0 <= data["score_actividad"] <= 100

    def test_evaluar_actividad_inexistente(self, client):
        """Evaluar actividad que no existe → 404."""
        resp = client.post("/api/actividades/9999/evaluar-riesgo")
        assert resp.status_code == 404

    def test_evaluar_actividad_2_nivel_critico(self, client, act_id2):
        """Actividad 2 (datos sensibles + transferencia) → crítico."""
        resp = client.post(f"/api/actividades/{act_id2}/evaluar-riesgo")
        assert resp.status_code == 200
        data = resp.json()
        # datos_sensibles=True + transferencia_internacional="Sí - Unión Europea"
        assert data["nivel_riesgo"] == "crítico"
        assert data["score_actividad"] <= 60  # penalización 40 por crítico

    def test_evaluar_persiste_en_db(self, client, act_id2, db_conn):
        """La evaluación persiste nivel_riesgo y score en la BD."""
        client.post(f"/api/actividades/{act_id2}/evaluar-riesgo")
        row = db_conn.execute(
            "SELECT nivel_riesgo, score_actividad FROM actividades WHERE id = ?",
            [act_id2],
        ).fetchone()
        assert row[0] == "crítico"
        assert row[1] is not None


class TestEvaluarRiesgoDirecto:
    """Tests unitarios directos de evaluar_riesgo_actividad()"""

    def test_datos_sensibles_salud_critico(self):
        """Categorías de datos que incluyen 'salud' → nivel crítico."""
        actividad = {
            "categorias_datos": ["Nombre", "Historial médico", "Diagnóstico salud"],
            "categoria_titulares": ["Pacientes"],
            "datos_sensibles": True,
            "transferencia_internacional": "No aplica",
            "decisiones_automatizadas": "No aplica",
            "requiere_eipd": False,
            "medidas_seguridad": "Cifrado",
            "plazo_conservacion": "5 años",
            "justificacion_conservacion": "Legal",
            "origen_fuente": "Formulario",
            "garantías_transferencia": "",
        }
        resultado = evaluar_riesgo_actividad(actividad)
        assert resultado["nivel_riesgo"] == "crítico"
        assert "salud" in str(resultado["factores"]).lower()

    def test_datos_sensibles_biometricos_critico(self):
        """Datos biométricos → nivel crítico."""
        actividad = {
            "categorias_datos": ["Nombre", "Datos biométricos", "Huella digital"],
            "categoria_titulares": ["Empleados"],
            "datos_sensibles": True,
            "transferencia_internacional": "No aplica",
            "decisiones_automatizadas": "No aplica",
            "requiere_eipd": False,
            "medidas_seguridad": "",
            "plazo_conservacion": "",
            "justificacion_conservacion": "",
            "origen_fuente": "",
            "garantías_transferencia": "",
        }
        resultado = evaluar_riesgo_actividad(actividad)
        assert resultado["nivel_riesgo"] == "crítico"

    def test_transferencia_internacional_medio(self):
        """Transferencia internacional sin datos sensibles → nivel medio."""
        actividad = {
            "categorias_datos": ["Nombre", "Email"],
            "categoria_titulares": ["Usuarios"],
            "datos_sensibles": False,
            "transferencia_internacional": "Sí - Estados Unidos",
            "decisiones_automatizadas": "No aplica",
            "requiere_eipd": False,
            "medidas_seguridad": "",
            "plazo_conservacion": "",
            "justificacion_conservacion": "",
            "origen_fuente": "",
            "garantías_transferencia": "",
        }
        resultado = evaluar_riesgo_actividad(actividad)
        assert resultado["nivel_riesgo"] == "medio"
        assert "Transferencia internacional" in resultado["factores"]

    def test_sin_datos_sensibles_ni_transferencia_bajo(self):
        """Sin datos sensibles ni transferencia → nivel bajo."""
        actividad = {
            "categorias_datos": ["Nombre", "Email"],
            "categoria_titulares": ["Usuarios"],
            "datos_sensibles": False,
            "transferencia_internacional": "No aplica",
            "decisiones_automatizadas": "No aplica",
            "requiere_eipd": False,
            "medidas_seguridad": "",
            "plazo_conservacion": "",
            "justificacion_conservacion": "",
            "origen_fuente": "",
            "garantías_transferencia": "",
        }
        resultado = evaluar_riesgo_actividad(actividad)
        assert resultado["nivel_riesgo"] == "bajo"

    def test_nna_involucrados_critico(self):
        """Menores de edad (NNA) → nivel crítico."""
        actividad = {
            "categorias_datos": ["Nombre", "Edad"],
            "categoria_titulares": ["Niños", "Estudiantes menores de edad"],
            "datos_sensibles": False,
            "transferencia_internacional": "No aplica",
            "decisiones_automatizadas": "No aplica",
            "requiere_eipd": False,
            "medidas_seguridad": "",
            "plazo_conservacion": "",
            "justificacion_conservacion": "",
            "origen_fuente": "",
            "garantías_transferencia": "",
        }
        resultado = evaluar_riesgo_actividad(actividad)
        assert resultado["nivel_riesgo"] == "crítico"

    def test_score_penalizaciones(self):
        """Score se penaliza por campos faltantes."""
        actividad = {
            "categorias_datos": [],
            "categoria_titulares": [],
            "datos_sensibles": False,
            "transferencia_internacional": "No aplica",
            "decisiones_automatizadas": "No aplica",
            "requiere_eipd": False,
            "medidas_seguridad": "",       # -10
            "plazo_conservacion": "",       # -10
            "justificacion_conservacion": "",  # -5
            "origen_fuente": "",            # -5
            "garantías_transferencia": "",
        }
        resultado = evaluar_riesgo_actividad(actividad)
        assert resultado["nivel_riesgo"] == "bajo"
        assert resultado["score_actividad"] == 70  # 100 - 10 - 10 - 5 - 5

    def test_score_completo(self):
        """Todos los campos completos → score máximo."""
        actividad = {
            "categorias_datos": ["Nombre"],
            "categoria_titulares": ["Usuarios"],
            "datos_sensibles": False,
            "transferencia_internacional": "No aplica",
            "decisiones_automatizadas": "No aplica",
            "requiere_eipd": False,
            "medidas_seguridad": "Cifrado",
            "plazo_conservacion": "5 años",
            "justificacion_conservacion": "Obligación legal",
            "origen_fuente": "Formulario web",
            "garantías_transferencia": "",
        }
        resultado = evaluar_riesgo_actividad(actividad)
        assert resultado["score_actividad"] == 100

    def test_decisiones_automatizadas_medio(self):
        """Decisiones automatizadas sin otros factores → nivel medio."""
        actividad = {
            "categorias_datos": ["Nombre"],
            "categoria_titulares": ["Usuarios"],
            "datos_sensibles": False,
            "transferencia_internacional": "No aplica",
            "decisiones_automatizadas": "Sí - perfilado automatizado",
            "requiere_eipd": False,
            "medidas_seguridad": "",
            "plazo_conservacion": "",
            "justificacion_conservacion": "",
            "origen_fuente": "",
            "garantías_transferencia": "",
        }
        resultado = evaluar_riesgo_actividad(actividad)
        assert resultado["nivel_riesgo"] == "medio"
