"""
RAT UCT — Tests del CRUD de actividades
========================================

Cubre los 8 endpoints del router /api/actividades:
lista paginada, búsqueda, detalle, creación, actualización,
eliminación y estadísticas.
"""


class TestListarActividades:
    """GET /api/actividades"""

    def test_lista_paginada(self, client):
        """Debe retornar lista paginada de actividades."""
        resp = client.get("/api/actividades")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_lista_con_search(self, client):
        """Filtro por búsqueda textual (ILIKE)."""
        resp = client.get("/api/actividades?search=matrícula")
        assert resp.status_code == 200
        data = resp.json()
        assert any("matrícula" in a["actividad_tratamiento"].lower()
                   for a in data)

    def test_lista_search_sin_resultados(self, client):
        """Búsqueda sin resultados retorna lista vacía."""
        resp = client.get("/api/actividades?search=zzzznoexistezzz")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_lista_con_limit(self, client):
        """Parámetros limit y offset funcionan."""
        resp = client.get("/api/actividades?limit=1&offset=0")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestObtenerActividad:
    """GET /api/actividades/{id}"""

    def test_obtener_existente(self, client, act_id):
        """Obtener actividad por ID retorna todos los campos."""
        resp = client.get(f"/api/actividades/{act_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == act_id
        assert data["actividad_tratamiento"] == "Gestión de matrícula estudiantil"
        assert data["finalidad"] == "Gestión académica y administrativa de matrícula"
        assert data["base_licitud"] == "Consentimiento"
        assert data["plazo_conservacion"] == "5 años"
        assert data["estado"] == "activo"

    def test_obtener_inexistente(self, client):
        """Actividad que no existe → 404."""
        resp = client.get("/api/actividades/9999")
        assert resp.status_code == 404


class TestCrearActividad:
    """POST /api/actividades"""

    VALID_DATA = {
        "actividad_tratamiento": "Nueva actividad de prueba",
        "finalidad": "Probar la creación",
        "base_licitud": "Consentimiento",
        "plazo_conservacion": "3 años",
    }

    def test_crear_valida(self, client):
        """Creación con datos mínimos válidos."""
        resp = client.post("/api/actividades", json=self.VALID_DATA)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] > 0  # ID asignado por sequence
        assert data["actividad_tratamiento"] == "Nueva actividad de prueba"
        assert data["estado"] == "activo"

    def test_crear_sin_finalidad(self, client):
        """Omisión de campo obligatorio 'finalidad' → 422."""
        data = {
            "actividad_tratamiento": "Sin finalidad",
            "base_licitud": "Consentimiento",
            "plazo_conservacion": "1 año",
        }
        resp = client.post("/api/actividades", json=data)
        assert resp.status_code == 422

    def test_crear_sin_base_licitud(self, client):
        """Omisión de 'base_licitud' → 422."""
        data = {
            "actividad_tratamiento": "Sin base",
            "finalidad": "Test",
            "plazo_conservacion": "1 año",
        }
        resp = client.post("/api/actividades", json=data)
        assert resp.status_code == 422

    def test_crear_con_datos_completos(self, client):
        """Creación con todos los campos opcionales."""
        data = {
            **self.VALID_DATA,
            "responsable_tratamiento": "Test",
            "descripcion": "Descripción completa",
            "datos_sensibles": True,
            "areas_intervienen": ["TI", "RRHH"],
            "categoria_titulares": ["Empleados"],
            "categorias_datos": ["Nombre", "RUT"],
            "origen_fuente": "Formulario web",
            "categoria_destinatarios": ["Empresa externa"],
            "transferencia_internacional": "No aplica",
            "pais_destino": "",
            "garantías_transferencia": "",
            "justificacion_conservacion": "Obligación legal",
            "medidas_seguridad": "Cifrado AES-256",
            "decisiones_automatizadas": "No aplica",
            "requiere_eipd": False,
            "nivel_riesgo": "bajo",
            "estado": "activo",
        }
        resp = client.post("/api/actividades", json=data)
        assert resp.status_code == 201
        created = resp.json()
        assert created["descripcion"] == "Descripción completa"
        assert created["datos_sensibles"] is True


class TestActualizarActividad:
    """PUT /api/actividades/{id}"""

    def test_actualizar_parcial(self, client, act_id):
        """Actualización parcial de campos."""
        resp = client.put(f"/api/actividades/{act_id}", json={
            "finalidad": "Finalidad actualizada",
            "descripcion": "Descripción modificada",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["finalidad"] == "Finalidad actualizada"
        assert data["descripcion"] == "Descripción modificada"
        # Campos no modificados deben conservar valor original
        assert data["actividad_tratamiento"] == "Gestión de matrícula estudiantil"

    def test_actualizar_inexistente(self, client):
        """Actualizar actividad que no existe → 404."""
        resp = client.put("/api/actividades/9999", json={"finalidad": "N/A"})
        assert resp.status_code == 404

    def test_actualizar_estado(self, client, act_id):
        """Cambiar estado de una actividad."""
        resp = client.put(f"/api/actividades/{act_id}", json={"estado": "archivado"})
        assert resp.status_code == 200
        assert resp.json()["estado"] == "archivado"


class TestEliminarActividad:
    """DELETE /api/actividades/{id}"""

    def test_eliminar_existente(self, client, act_id):
        """Eliminación retorna 204."""
        resp = client.delete(f"/api/actividades/{act_id}")
        assert resp.status_code == 204

    def test_eliminar_y_verificar(self, client, act_id):
        """Tras eliminar, GET retorna 404."""
        client.delete(f"/api/actividades/{act_id}")
        resp = client.get(f"/api/actividades/{act_id}")
        assert resp.status_code == 404


class TestTotalActividades:
    """GET /api/actividades/total"""

    def test_total_stats(self, client):
        """Estadísticas rápidas del RAT."""
        resp = client.get("/api/actividades/total")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        assert isinstance(data["datos_sensibles"], int)
        assert isinstance(data["transferencias_internacionales"], int)
        assert "activo" in data["por_estado"]
