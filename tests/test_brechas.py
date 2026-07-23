"""
RAT UCT — Tests del módulo Brechas
===================================

CRUD completo de brechas de seguridad y filtro por estado.

NOTA: GET /api/brechas tiene el mismo bug que ARSOP:
los campos notificado_apdp/notificado_titulares pueden ser NULL en DB
pero BrechaOut.notificado_apdp es bool (no Optional).
"""

import pytest


class TestCrearBrecha:
    """POST /api/brechas"""

    def test_crear_brecha_valida(self, client):
        """Crear brecha con datos mínimos."""
        resp = client.post("/api/brechas", json={
            "titulo": "Intento de phishing",
            "descripcion": "Correo sospechoso detectado",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["titulo"] == "Intento de phishing"
        assert data["estado"] == "abierta"
        assert data["severidad"] == "media"

    def test_crear_brecha_completa(self, client, act_id):
        """Crear brecha con todos los campos."""
        resp = client.post("/api/brechas", json={
            "actividad_id": act_id,
            "titulo": "Filtración de base de datos",
            "descripcion": "Datos expuestos en servidor público",
            "severidad": "crítica",
            "tipo_incidente": "Filtración",
            "datos_afectados": "Nombres, RUTs, emails",
            "titulares_afectados": 150,
            "medidas_correctivas": "Rotación de credenciales",
            "estado": "en_investigación",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["severidad"] == "crítica"
        assert data["titulares_afectados"] == 150
        assert data["estado"] == "en_investigación"


class TestListarBrechas:
    """GET /api/brechas"""

    def test_listar_todas(self, client):
        """Listar todas las brechas."""
        resp = client.get("/api/brechas")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_filtrar_por_estado(self, client):
        """Filtro por estado."""
        resp = client.get("/api/brechas?estado=abierta")
        assert resp.status_code == 200
        data = resp.json()
        assert all(b["estado"] == "abierta" for b in data)

    def test_filtrar_por_estado_sin_resultados(self, client):
        """Filtro sin resultados retorna []."""
        resp = client.get("/api/brechas?estado=cerrada")
        assert resp.status_code == 200
        assert resp.json() == []


class TestActualizarBrecha:
    """PUT /api/brechas/{id}"""

    def test_actualizar_brecha(self, client):
        """Actualizar estado y medidas de una brecha."""
        post = client.post("/api/brechas", json={
            "titulo": "Brecha de prueba",
            "descripcion": "Descripción inicial",
        })
        brecha_id = post.json()["id"]

        resp = client.put(f"/api/brechas/{brecha_id}", json={
            "estado": "cerrada",
            "medidas_correctivas": "Parche aplicado",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "cerrada"
        assert data["medidas_correctivas"] == "Parche aplicado"

    def test_actualizar_inexistente(self, client):
        """Actualizar brecha que no existe → 404."""
        resp = client.put("/api/brechas/9999", json={"estado": "cerrada"})
        assert resp.status_code == 404
