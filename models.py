"""
RAT UCT — Modelos Pydantic para validación de API
==================================================

Define los esquemas de datos para los 22 endpoints de la API FastAPI.
Cada modelo tiene tres variantes:
  - Create: campos requeridos para crear un recurso (POST)
  - Update: todos opcionales, solo lo enviado se modifica (PUT)
  - Out: respuesta completa con id y timestamps (GET)

Modelos:
  - ActividadCreate/Update/Out  — 26 campos del RAT
  - AreaCreate/Out              — Catálogo de unidades UCT
  - ProcesoCreate/Out           — Macroprocesos institucionales
  - EncargadoCreate/Out         — Destinatarios externos
  - EipdCreate/Update/Out       — Evaluación de Impacto (4 pasos)
  - BrechaCreate/Update/Out     — Incidentes de seguridad
  - ArsopCreate/Update/Out      — Solicitudes ARSOP
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ActividadCreate(BaseModel):
    actividad_tratamiento: str
    responsable_tratamiento: str = "UCT — Universidad Católica de Temuco"
    responsable_rut: str = ""
    responsable_domicilio: str = ""
    responsable_representante: str = ""
    dpo_contacto: str = "dpo@uct.cl"
    areas_intervienen: list[str] = []
    finalidad: str
    descripcion: str = ""
    categoria_titulares: list[str] = []
    categorias_datos: list[str] = []
    datos_sensibles: bool = False
    origen_fuente: str = ""
    categoria_destinatarios: list[str] = []
    base_licitud: str
    transferencia_internacional: str = "No aplica"
    pais_destino: str = ""
    garantías_transferencia: str = ""
    plazo_conservacion: str
    justificacion_conservacion: str = ""
    medidas_seguridad: str = ""
    decisiones_automatizadas: str = "No aplica"
    requiere_eipd: bool = False
    nivel_riesgo: str = "bajo"
    score_actividad: Optional[int] = None
    estado: str = "activo"


class ActividadUpdate(BaseModel):
    actividad_tratamiento: Optional[str] = None
    responsable_tratamiento: Optional[str] = None
    responsable_rut: Optional[str] = None
    responsable_domicilio: Optional[str] = None
    responsable_representante: Optional[str] = None
    dpo_contacto: Optional[str] = None
    areas_intervienen: Optional[list[str]] = None
    finalidad: Optional[str] = None
    descripcion: Optional[str] = None
    categoria_titulares: Optional[list[str]] = None
    categorias_datos: Optional[list[str]] = None
    datos_sensibles: Optional[bool] = None
    origen_fuente: Optional[str] = None
    categoria_destinatarios: Optional[list[str]] = None
    base_licitud: Optional[str] = None
    transferencia_internacional: Optional[str] = None
    pais_destino: Optional[str] = None
    garantías_transferencia: Optional[str] = None
    plazo_conservacion: Optional[str] = None
    justificacion_conservacion: Optional[str] = None
    medidas_seguridad: Optional[str] = None
    decisiones_automatizadas: Optional[str] = None
    requiere_eipd: Optional[bool] = None
    nivel_riesgo: Optional[str] = None
    score_actividad: Optional[int] = None
    estado: Optional[str] = None


class ActividadOut(BaseModel):
    id: int
    actividad_tratamiento: str
    responsable_tratamiento: str
    responsable_rut: str
    responsable_domicilio: str
    responsable_representante: str
    dpo_contacto: str
    areas_intervienen: list[str]
    finalidad: str
    descripcion: str
    categoria_titulares: list[str]
    categorias_datos: list[str]
    datos_sensibles: bool
    origen_fuente: str
    categoria_destinatarios: list[str]
    base_licitud: str
    transferencia_internacional: str
    pais_destino: str
    garantías_transferencia: str
    plazo_conservacion: str
    justificacion_conservacion: str
    medidas_seguridad: str
    decisiones_automatizadas: str
    requiere_eipd: bool
    nivel_riesgo: str
    score_actividad: Optional[int] = None
    estado: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AreaCreate(BaseModel):
    nombre: str
    descripcion: str = ""
    tipo: str = "unidad"


class AreaOut(BaseModel):
    id: int
    nombre: str
    descripcion: str
    tipo: str


class ProcesoCreate(BaseModel):
    nombre: str
    macroproceso: str = ""
    descripcion: str = ""
    actividades_ids: list[int] = []


class ProcesoOut(BaseModel):
    id: int
    nombre: str
    macroproceso: str
    descripcion: str
    actividades_ids: list[int]


class EncargadoCreate(BaseModel):
    nombre: str
    rut: str = ""
    pais: str = "Chile"
    servicio: str = ""
    dpa_generado: bool = False


class EncargadoOut(BaseModel):
    id: int
    nombre: str
    rut: str
    pais: str
    servicio: str
    dpa_generado: bool


# ─── EIPD ────────────────────────────────────────────────────────────────────

class EipdCreate(BaseModel):
    actividad_id: int
    estado: str = "borrador"
    necesita_eipd: Optional[bool] = None
    motivo_activacion: Optional[str] = ""
    riesgo_inherente: Optional[str] = ""
    riesgo_residual: Optional[str] = ""
    medidas_propuestas: Optional[str] = ""
    medidas_implementadas: Optional[str] = ""
    aprobado_por: Optional[str] = ""
    fecha_aprobacion: Optional[str] = ""


class EipdUpdate(BaseModel):
    estado: Optional[str] = None
    necesita_eipd: Optional[bool] = None
    motivo_activacion: Optional[str] = None
    riesgo_inherente: Optional[str] = None
    riesgo_residual: Optional[str] = None
    medidas_propuestas: Optional[str] = None
    medidas_implementadas: Optional[str] = None
    aprobado_por: Optional[str] = None
    fecha_aprobacion: Optional[str] = None


class EipdOut(BaseModel):
    id: int
    actividad_id: int
    estado: str
    necesita_eipd: Optional[bool] = None
    motivo_activacion: Optional[str] = ""
    riesgo_inherente: Optional[str] = ""
    riesgo_residual: Optional[str] = ""
    medidas_propuestas: Optional[str] = ""
    medidas_implementadas: Optional[str] = ""
    aprobado_por: Optional[str] = ""
    fecha_aprobacion: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ─── Brechas ─────────────────────────────────────────────────────────────────

class BrechaCreate(BaseModel):
    actividad_id: Optional[int] = None
    titulo: str
    descripcion: str = ""
    severidad: str = "media"
    tipo_incidente: str = ""
    datos_afectados: str = ""
    titulares_afectados: Optional[int] = None
    medidas_correctivas: str = ""
    estado: str = "abierta"


class BrechaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    severidad: Optional[str] = None
    tipo_incidente: Optional[str] = None
    datos_afectados: Optional[str] = None
    titulares_afectados: Optional[int] = None
    medidas_correctivas: Optional[str] = None
    notificado_apdp: Optional[bool] = None
    notificado_titulares: Optional[bool] = None
    estado: Optional[str] = None


class BrechaOut(BaseModel):
    id: int
    actividad_id: Optional[int] = None
    titulo: str
    descripcion: str
    severidad: str
    tipo_incidente: str
    datos_afectados: str
    titulares_afectados: Optional[int] = None
    medidas_correctivas: str
    notificado_apdp: bool = False
    notificado_titulares: bool = False
    estado: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ─── ARSOP ──────────────────────────────────────────────────────────────────

class ArsopCreate(BaseModel):
    tipo_derecho: str
    solicitante_nombre: str = ""
    solicitante_email: str = ""
    solicitante_rut: str = ""
    descripcion: str = ""
    actividad_id: Optional[int] = None


class ArsopUpdate(BaseModel):
    estado: Optional[str] = None
    respuesta: Optional[str] = None
    fecha_respuesta: Optional[str] = None


class ArsopOut(BaseModel):
    id: int
    tipo_derecho: str
    solicitante_nombre: str
    solicitante_email: str
    solicitante_rut: str
    descripcion: str
    actividad_id: Optional[int] = None
    fecha_solicitud: Optional[datetime] = None
    fecha_vencimiento: Optional[str] = None
    estado: str
    respuesta: str = ""
    fecha_respuesta: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
