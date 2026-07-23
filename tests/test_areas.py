"""
RAT UCT — Tests del catálogo de áreas
======================================

Cubre los endpoints de /api/areas:
- GET /api/areas → listar todas
- POST /api/areas → crear nueva
"""


class TestListarAreas:
    """GET /api/areas"""

    def test_listar_todas(self, client):
        """Lista todas las áreas (12 seed + 1 test)."""
        resp = client.get("/api/areas")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 13  # 12 seed + 1 test
        nombres = [a["nombre"] for a in data]
        assert "CERETI" in nombres
        assert "Test Area" in nombres

    def test_listar_por_tipo(self, client):
        """Filtro por tipo."""
        resp = client.get("/api/areas?tipo=dirección")
        assert resp.status_code == 200
        data = resp.json()
        assert all(a["tipo"] == "dirección" for a in data)
        assert len(data) >= 8  # varias direcciones en seed

    def test_listar_tipo_sin_resultados(self, client):
        """Filtro sin resultados retorna []."""
        resp = client.get("/api/areas?tipo=inexistente")
        assert resp.status_code == 200
        assert resp.json() == []


class TestCrearArea:
    """POST /api/areas"""

    def test_crear_area_valida(self, client):
        """Crear área con datos mínimos."""
        resp = client.post("/api/areas", json={
            "nombre": "Nueva Área Test",
            "descripcion": "Descripción de prueba",
            "tipo": "unidad",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Nueva Área Test"
        assert data["tipo"] == "unidad"

    def test_crear_area_sin_nombre(self, client):
        """Omisión de campo obligatorio 'nombre' → 422."""
        resp = client.post("/api/areas", json={
            "descripcion": "Sin nombre",
        })
        assert resp.status_code == 422
