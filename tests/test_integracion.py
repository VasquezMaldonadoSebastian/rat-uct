"""
RAT UCT — Tests de integración (flujos completos)
==================================================

Prueba flujos completos multi-paso que atraviesan varios endpoints
y verifican el estado combinado del sistema.

Requiere conftest.py con fixtures: client, db_conn, act_id, act_id2.
"""

import pytest
from fastapi.testclient import TestClient


# ─── test_flujo_completo_actividad_a_reporte ────────────────────────────────

class TestFlujoCompleto:
    """Flujo completo: actividad → riesgo → EIPD → brecha → ARSOP → reporte."""

    def test_flujo_completo_actividad_a_reporte(self, client: TestClient):
        """Recorre la cadena completa de creación de datos y verifica
        que el reporte resumen los refleje."""
        # ----------------------------------------------------------------
        # 1. Crear actividad con datos sensibles
        # ----------------------------------------------------------------
        resp = client.post("/api/actividades", json={
            "actividad_tratamiento": "Campaña de vacunación UCT",
            "finalidad": "Gestión de salud estudiantil",
            "descripcion": "Registro de vacunación COVID-19",
            "base_licitud": "Consentimiento",
            "plazo_conservacion": "5 años",
            "datos_sensibles": True,
            "categorias_datos": ["Nombre", "RUT", "Estado de salud"],
            "categoria_titulares": ["Estudiantes"],
            "areas_intervienen": ["Bienestar Estudiantil", "TI"],
            "medidas_seguridad": "Acceso restringido",
        })
        assert resp.status_code == 201, f"Crear actividad falló: {resp.text}"
        act = resp.json()
        act_id = act["id"]
        assert act["actividad_tratamiento"] == "Campaña de vacunación UCT"

        # ----------------------------------------------------------------
        # 2. Evaluar riesgo
        # ----------------------------------------------------------------
        resp = client.post(f"/api/actividades/{act_id}/evaluar-riesgo")
        assert resp.status_code == 200, f"Evaluar riesgo falló: {resp.text}"
        riesgo = resp.json()

        # 3. Verificar nivel_riesgo y score en la respuesta
        assert "nivel_riesgo" in riesgo, "Falta nivel_riesgo en respuesta"
        assert "score_actividad" in riesgo, "Falta score_actividad en respuesta"
        assert riesgo["nivel_riesgo"] in ("alto", "crítico"), \
            f"Riesgo debe ser alto/crítico: {riesgo['nivel_riesgo']}"
        assert isinstance(riesgo["score_actividad"], int)
        assert 0 <= riesgo["score_actividad"] <= 100

        # ----------------------------------------------------------------
        # 4. Crear EIPD para esta actividad
        # ----------------------------------------------------------------
        resp = client.post("/api/eipd", json={
            "actividad_id": act_id,
            "estado": "borrador",
            "necesita_eipd": True,
            "motivo_activacion": "Tratamiento de datos de salud de estudiantes",
            "fecha_aprobacion": None,
        })
        assert resp.status_code == 201, f"Crear EIPD falló: {resp.text}"
        assert resp.json()["actividad_id"] == act_id
        assert resp.json()["estado"] == "borrador"

        # ----------------------------------------------------------------
        # 5. Crear brecha para esta actividad
        # ----------------------------------------------------------------
        resp = client.post("/api/brechas", json={
            "actividad_id": act_id,
            "titulo": "Acceso no autorizado a registros de vacunación",
            "descripcion": "Posible fuga detectada en logs del servidor",
            "severidad": "alta",
            "estado": "abierta",
        })
        assert resp.status_code == 201, f"Crear brecha falló: {resp.text}"
        assert resp.json()["actividad_id"] == act_id
        assert resp.json()["estado"] == "abierta"

        # ----------------------------------------------------------------
        # 6. Crear solicitud ARSOP
        # ----------------------------------------------------------------
        resp = client.post("/api/arsop", json={
            "tipo_derecho": "Acceso",
            "solicitante_nombre": "María González",
            "solicitante_email": "maria@uct.cl",
            "descripcion": "Solicita acceso a sus datos de vacunación",
            "actividad_id": act_id,
        })
        assert resp.status_code == 201, f"Crear ARSOP falló: {resp.text}"
        assert resp.json()["tipo_derecho"] == "Acceso"
        assert resp.json()["estado"] == "recibida"

        # ----------------------------------------------------------------
        # 7. Verificar reporte resumen
        # ----------------------------------------------------------------
        resp = client.get("/api/reportes/resumen")
        assert resp.status_code == 200
        reporte = resp.json()

        # Seed tiene 2 actividades + 1 creada = 3
        assert reporte["total_actividades"] == 3, \
            f"Esperado 3 actividades, obtenido {reporte['total_actividades']}"
        # La nueva actividad usa base_licitud=Consentimiento
        assert "Consentimiento" in reporte["por_base_legal"]
        assert reporte["por_base_legal"]["Consentimiento"] >= 1
        # Aparecen las áreas de la nueva actividad
        assert "Bienestar Estudiantil" in reporte["por_area"], \
            "Falta área Bienestar Estudiantil en reporte"
        assert "TI" in reporte["por_area"], "Falta área TI en reporte"


# ─── test_flujo_eipd_completo ──────────────────────────────────────────────

class TestFlujoEipd:
    """Flujo completo de creación y avance de EIPD paso a paso."""

    def test_flujo_eipd_completo(self, client: TestClient):
        """Crea actividad con datos sensibles, evalúa riesgo, crea EIPD
        y la avanza paso a paso hasta completarla."""
        # ----------------------------------------------------------------
        # 1. Crear actividad con datos sensibles
        # ----------------------------------------------------------------
        resp = client.post("/api/actividades", json={
            "actividad_tratamiento": "Evaluación psicológica estudiantes",
            "finalidad": "Salud mental estudiantil",
            "base_licitud": "Consentimiento",
            "plazo_conservacion": "10 años",
            "datos_sensibles": True,
            "categorias_datos": ["Nombre", "RUT", "Salud mental"],
            "categoria_titulares": ["Estudiantes"],
        })
        assert resp.status_code == 201, f"Crear actividad falló: {resp.text}"
        act_id = resp.json()["id"]

        # ----------------------------------------------------------------
        # 2. Evaluar riesgo — debe ser alto o crítico
        # ----------------------------------------------------------------
        resp = client.post(f"/api/actividades/{act_id}/evaluar-riesgo")
        assert resp.status_code == 200, f"Evaluar riesgo falló: {resp.text}"
        riesgo = resp.json()
        assert riesgo["nivel_riesgo"] in ("alto", "crítico"), \
            f"Esperado alto/crítico, obtuvo {riesgo['nivel_riesgo']}"

        # ----------------------------------------------------------------
        # 3. Crear EIPD en estado borrador
        # ----------------------------------------------------------------
        resp = client.post("/api/eipd", json={
            "actividad_id": act_id,
            "estado": "borrador",
            "necesita_eipd": True,
            "motivo_activacion": "Evaluación de salud mental de estudiantes",
            "fecha_aprobacion": None,
        })
        assert resp.status_code == 201, f"Crear EIPD falló: {resp.text}"
        eipd = resp.json()
        eipd_id = eipd["id"]
        assert eipd["estado"] == "borrador"

        # ----------------------------------------------------------------
        # 4. Avanzar EIPD paso a paso vía PUT
        # ----------------------------------------------------------------
        # Paso 1: Riesgo inherente
        resp = client.put(f"/api/eipd/{eipd_id}", json={
            "riesgo_inherente": "alto",
        })
        assert resp.status_code == 200, f"Paso 1 falló: {resp.text}"
        assert resp.json()["riesgo_inherente"] == "alto"

        # Paso 2: Riesgo residual
        resp = client.put(f"/api/eipd/{eipd_id}", json={
            "riesgo_residual": "medio",
        })
        assert resp.status_code == 200, f"Paso 2 falló: {resp.text}"
        assert resp.json()["riesgo_residual"] == "medio"

        # Paso 3: Medidas propuestas e implementadas
        resp = client.put(f"/api/eipd/{eipd_id}", json={
            "medidas_propuestas": "Cifrado de datos, control de acceso, formación del personal",
            "medidas_implementadas": "Cifrado AES-256 implementado, logs de acceso activados",
        })
        assert resp.status_code == 200, f"Paso 3 falló: {resp.text}"
        d = resp.json()
        assert "Cifrado" in d["medidas_propuestas"]
        assert "Cifrado" in d["medidas_implementadas"]

        # Paso 4: Completar — firma del DPO
        resp = client.put(f"/api/eipd/{eipd_id}", json={
            "estado": "completada",
            "aprobado_por": "Juan Pérez, DPO",
            "fecha_aprobacion": "2026-07-23",
        })
        assert resp.status_code == 200, f"Paso 4 falló: {resp.text}"
        assert resp.json()["estado"] == "completada"

        # ----------------------------------------------------------------
        # 5. Verificar GET /api/eipd refleja el estado final
        # ----------------------------------------------------------------
        resp = client.get(f"/api/eipd?actividad_id={act_id}")
        assert resp.status_code == 200
        resultados = resp.json()
        our_eipd = next((e for e in resultados if e["id"] == eipd_id), None)
        assert our_eipd is not None, "EIPD no encontrada en listado"
        assert our_eipd["estado"] == "completada"
        assert our_eipd["aprobado_por"] == "Juan Pérez, DPO"
        assert our_eipd["riesgo_inherente"] == "alto"
        assert our_eipd["riesgo_residual"] == "medio"


# ─── test_flujo_brecha_con_notificacion ────────────────────────────────────

class TestFlujoBrecha:
    """Flujo: crear actividad → reportar brecha → actualizar con notificación."""

    def test_flujo_brecha_con_notificacion(self, client: TestClient):
        # ----------------------------------------------------------------
        # 1. Crear actividad
        # ----------------------------------------------------------------
        resp = client.post("/api/actividades", json={
            "actividad_tratamiento": "Sistema de gestión de becas",
            "finalidad": "Gestión de becas y beneficios estudiantiles",
            "base_licitud": "Consentimiento",
            "plazo_conservacion": "5 años",
        })
        assert resp.status_code == 201
        act_id = resp.json()["id"]

        # ----------------------------------------------------------------
        # 2. Reportar brecha
        # ----------------------------------------------------------------
        resp = client.post("/api/brechas", json={
            "actividad_id": act_id,
            "titulo": "Intento de phishing masivo a estudiantes",
            "descripcion": "Correos fraudulentos solicitando credenciales",
            "severidad": "media",
            "tipo_incidente": "Phishing",
            "datos_afectados": "Credenciales de acceso",
            "estado": "abierta",
        })
        assert resp.status_code == 201, f"Crear brecha falló: {resp.text}"
        brecha_id = resp.json()["id"]

        # ----------------------------------------------------------------
        # 3. Actualizar brecha: notificar APDP y agregar medidas
        # ----------------------------------------------------------------
        resp = client.put(f"/api/brechas/{brecha_id}", json={
            "notificado_apdp": True,
            "medidas_correctivas": "Bloqueo de cuentas sospechosas, "
                                   "campaña de concientización",
            "estado": "en_investigacion",
        })
        assert resp.status_code == 200, f"Actualizar brecha falló: {resp.text}"
        brecha_resp = resp.json()
        assert brecha_resp["notificado_apdp"] is True
        assert "Bloqueo" in brecha_resp["medidas_correctivas"]
        assert brecha_resp["estado"] == "en_investigacion"

        # ----------------------------------------------------------------
        # 4. Verificar GET /api/brechas refleja los cambios
        # ----------------------------------------------------------------
        resp = client.get("/api/brechas")
        assert resp.status_code == 200
        brechas = resp.json()
        our = next((b for b in brechas if b["id"] == brecha_id), None)
        assert our is not None, "Brecha no encontrada en listado"
        assert our["notificado_apdp"] is True
        assert "Bloqueo" in our["medidas_correctivas"]
        assert our["estado"] == "en_investigacion"


# ─── test_flujo_arsop_respuesta ────────────────────────────────────────────

class TestFlujoArsop:
    """Flujo: crear solicitud ARSOP → responder → verificar."""

    def test_flujo_arsop_respuesta(self, client: TestClient):
        # ----------------------------------------------------------------
        # 1. Crear solicitud ARSOP
        # ----------------------------------------------------------------
        resp = client.post("/api/arsop", json={
            "tipo_derecho": "Rectificación",
            "solicitante_nombre": "Pedro López",
            "solicitante_email": "pedro@example.com",
            "descripcion": "Solicita rectificar su dirección registrada",
        })
        assert resp.status_code == 201, f"Crear ARSOP falló: {resp.text}"
        arsop = resp.json()
        arsop_id = arsop["id"]
        assert arsop["estado"] == "recibida"
        assert arsop["tipo_derecho"] == "Rectificación"

        # ----------------------------------------------------------------
        # 2. Responder solicitud
        # ----------------------------------------------------------------
        resp = client.put(f"/api/arsop/{arsop_id}", json={
            "estado": "respondida",
            "respuesta": "Se ha procedido a rectificar la dirección "
                         "en nuestros registros.",
        })
        assert resp.status_code == 200, f"Responder ARSOP falló: {resp.text}"
        arsop_resp = resp.json()
        assert arsop_resp["estado"] == "respondida"
        assert "rectificar" in arsop_resp["respuesta"].lower()

        # ----------------------------------------------------------------
        # 3. Verificar GET /api/arsop refleja la respuesta
        # ----------------------------------------------------------------
        resp = client.get("/api/arsop")
        assert resp.status_code == 200
        solicitudes = resp.json()
        our = next((s for s in solicitudes if s["id"] == arsop_id), None)
        assert our is not None, "ARSOP no encontrada en listado"
        assert our["estado"] == "respondida"
        assert "rectificar" in our["respuesta"].lower()


# ─── test_catalogo_basico ──────────────────────────────────────────────────

class TestCatalogo:
    """Catálogo de áreas: listar → crear → verificar."""

    def test_catalogo_basico(self, client: TestClient):
        # ----------------------------------------------------------------
        # 1. GET /api/areas lista áreas
        # ----------------------------------------------------------------
        resp = client.get("/api/areas")
        assert resp.status_code == 200
        areas = resp.json()
        initial_count = len(areas)
        # 12 áreas del seed + 1 área de prueba en _seed_data
        assert initial_count == 13, \
            f"Esperado 13 áreas, obtenido {initial_count}"
        nombres = [a["nombre"] for a in areas]
        assert "TI" in nombres
        assert "Admisión" in nombres
        assert "Test Area" in nombres  # área de prueba del conftest

        # ----------------------------------------------------------------
        # 2. POST /api/areas crea una nueva
        # ----------------------------------------------------------------
        resp = client.post("/api/areas", json={
            "nombre": "Nueva Área de Integración",
            "descripcion": "Creada durante test de integración",
            "tipo": "unidad",
        })
        assert resp.status_code == 201, f"Crear área falló: {resp.text}"
        nueva = resp.json()
        assert nueva["nombre"] == "Nueva Área de Integración"
        assert nueva["tipo"] == "unidad"
        assert nueva["descripcion"] == "Creada durante test de integración"

        # ----------------------------------------------------------------
        # 3. GET /api/areas incluye la nueva
        # ----------------------------------------------------------------
        resp = client.get("/api/areas")
        assert resp.status_code == 200
        areas = resp.json()
        assert len(areas) == initial_count + 1, \
            f"Esperado {initial_count + 1} áreas, obtenido {len(areas)}"
        nombres = [a["nombre"] for a in areas]
        assert "Nueva Área de Integración" in nombres


# ─── test_estadisticas_inicio ──────────────────────────────────────────────

class TestEstadisticas:
    """Verificar estadísticas iniciales con los datos del seed."""

    def test_estadisticas_inicio(self, client: TestClient):
        """Después del reset automático (setup_db), verificar que
        GET /api/actividades/total retorna stats correctas."""
        resp = client.get("/api/actividades/total")
        assert resp.status_code == 200
        stats = resp.json()

        # Seed de conftest.py inserta 2 actividades
        assert stats["total"] == 2, \
            f"Esperado 2 actividades, obtenido {stats['total']}"

        # Actividad 2 tiene datos_sensibles=true
        assert stats["datos_sensibles"] == 1, \
            f"Esperado 1 con sensibles, obtenido {stats['datos_sensibles']}"

        # Actividad 2 tiene transferencia_internacional="Sí - Unión Europea"
        assert stats["transferencias_internacionales"] == 1, \
            f"Esperado 1 con transferencia, obtenido {stats['transferencias_internacionales']}"

        # Ambas actividades están activas
        assert "activo" in stats["por_estado"]
        assert stats["por_estado"]["activo"] == 2
