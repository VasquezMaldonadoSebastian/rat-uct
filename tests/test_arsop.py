"""
RAT UCT - Tests del modulo ARSOP
==================================

CRUD completo de solicitudes ARSOP y filtro por estado.
"""

import pytest


class TestCrearArsop:
    """POST /api/arsop"""

    def test_crear_arsop_valida(self, client):
        """Crear solicitud ARSOP con datos minimos."""
        resp = client.post("/api/arsop", json={
            "tipo_derecho": "Acceso",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["tipo_derecho"] == "Acceso"
        assert data["estado"] == "recibida"

    def test_crear_arsop_completa(self, client):
        """Crear ARSOP con todos los campos."""
        resp = client.post("/api/arsop", json={
            "tipo_derecho": "Rectificacion",
            "solicitante_nombre": "Maria Garcia",
            "solicitante_email": "maria@example.com",
            "solicitante_rut": "12.345.678-9",
            "descripcion": "Solicita rectificar direccion",
            "actividad_id": 1,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["tipo_derecho"] == "Rectificacion"
        assert data["solicitante_nombre"] == "Maria Garcia"
        assert data["estado"] == "recibida"

    def test_crear_arsop_sin_tipo(self, client):
        """Omision de campo obligatorio tipo_derecho -> 422."""
        resp = client.post("/api/arsop", json={
            "solicitante_nombre": "Test",
        })
        assert resp.status_code == 422


class TestListarArsop:
    """GET /api/arsop"""

    def test_listar_todas(self, client):
        """Listar todas las solicitudes ARSOP."""
        resp = client.get("/api/arsop")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_filtrar_por_estado(self, client):
        """Filtro por estado."""
        resp = client.get("/api/arsop?estado=recibida")
        assert resp.status_code == 200
        data = resp.json()
        assert all(a["estado"] == "recibida" for a in data)

    def test_filtrar_por_estado_sin_resultados(self, client):
        """Filtro sin resultados retorna []."""
        resp = client.get("/api/arsop?estado=respondida")
        assert resp.status_code == 200
        assert resp.json() == []


class TestActualizarArsop:
    """PUT /api/arsop/{id}"""

    def test_responder_solicitud(self, client):
        """Responder una solicitud ARSOP."""
        post = client.post("/api/arsop", json={
            "tipo_derecho": "Cancelacion",
            "solicitante_nombre": "Test",
        })
        assert post.status_code == 201
        arcop_id = post.json()["id"]

        resp = client.put(f"/api/arsop/{arcop_id}", json={
            "estado": "respondida",
            "respuesta": "Solicitud procesada exitosamente",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "respondida"
        assert data["respuesta"] == "Solicitud procesada exitosamente"

    def test_actualizar_inexistente(self, client):
        """Actualizar solicitud que no existe -> 404."""
        resp = client.put("/api/arsop/9999", json={"estado": "respondida"})
        assert resp.status_code == 404

    def test_actualizar_sin_cambios(self, client):
        """PUT sin datos retorna la solicitud sin cambios."""
        post = client.post("/api/arsop", json={
            "tipo_derecho": "Oposicion",
        })
        assert post.status_code == 201
        arcop_id = post.json()["id"]
        resp = client.put(f"/api/arsop/{arcop_id}", json={})
        assert resp.status_code == 200
