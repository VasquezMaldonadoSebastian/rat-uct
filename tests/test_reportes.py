"""
RAT UCT — Tests de reportes
============================

Cubre los endpoints de reportes agregados:
- GET /api/reportes/resumen
- GET /api/reportes/matriz-riesgo
- GET /api/reportes/score
"""


class TestReporteResumen:
    """GET /api/reportes/resumen"""

    def test_resumen_estructura(self, client):
        """Resumen ejecutivo retorna los campos esperados."""
        resp = client.get("/api/reportes/resumen")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_actividades" in data
        assert "por_base_legal" in data
        assert "por_area" in data
        assert "por_titular" in data
        assert data["total_actividades"] >= 2

    def test_resumen_por_base_legal(self, client):
        """Distribución por base de licitud."""
        resp = client.get("/api/reportes/resumen")
        data = resp.json()
        por_base = data["por_base_legal"]
        assert isinstance(por_base, dict)
        assert "Consentimiento" in por_base
        assert "Interés legítimo" in por_base

    def test_resumen_por_area(self, client):
        """Distribución por área."""
        resp = client.get("/api/reportes/resumen")
        data = resp.json()
        por_area = data["por_area"]
        assert isinstance(por_area, dict)
        assert len(por_area) >= 2  # Admisión, TI, Investigación


class TestMatrizRiesgo:
    """GET /api/reportes/matriz-riesgo"""

    def test_matriz_estructura(self, client):
        """Matriz de riesgo retorna los campos esperados."""
        resp = client.get("/api/reportes/matriz-riesgo")
        assert resp.status_code == 200
        data = resp.json()
        assert "por_nivel" in data
        assert "heatmap" in data

    def test_matriz_con_datos_vacios(self, client):
        """Sin evaluaciones de riesgo, matriz tiene ceros."""
        resp = client.get("/api/reportes/matriz-riesgo")
        data = resp.json()
        # Seed data tiene nivel_riesgo='bajo' por defecto
        assert "bajo" in data["por_nivel"]
        assert isinstance(data["heatmap"], dict)


class TestReporteScore:
    """GET /api/reportes/score"""

    def test_score_sin_evaluaciones(self, client):
        """Sin actividades evaluadas, score_global = 0."""
        resp = client.get("/api/reportes/score")
        assert resp.status_code == 200
        data = resp.json()
        assert data["score_global"] == 0
        assert data["total_evaluadas"] == 0

    def test_score_despues_de_evaluar(self, client, act_id, act_id2):
        """Tras evaluar riesgo, score refleja los valores."""
        client.post(f"/api/actividades/{act_id}/evaluar-riesgo")
        client.post(f"/api/actividades/{act_id2}/evaluar-riesgo")

        resp = client.get("/api/reportes/score")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_evaluadas"] >= 2
        assert data["score_global"] > 0
        assert len(data["por_area"]) >= 1
        assert len(data["por_nivel_riesgo"]) >= 1
