"""
Middleware de logging estructurado para RAT UCT
================================================

Provee:
- RequestID único por petición (uuid4 hex)
- Medición de tiempo de respuesta
- Logging estructurado al finalizar cada request
- Header X-Request-ID en la respuesta
- Captura y log de excepciones no manejadas
"""

import logging
import sys
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


def setup_logging() -> None:
    """Configura logging estructurado a stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Evitar duplicar handlers si se llama más de una vez
    if not root.handlers:
        root.addHandler(handler)
    else:
        # Reemplazar el primer handler (o todos) si ya existen
        root.handlers.clear()
        root.addHandler(handler)


logger = logging.getLogger("rat-uct")


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware que asigna un RequestID único a cada petición,
    mide el tiempo de respuesta y loggea la información estructurada.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Generar ID único por request
        request_id = uuid.uuid4().hex

        # Adjuntar el request_id al request state para que otros
        # componentes puedan accederlo si es necesario
        request.state.request_id = request_id

        # Marcar tiempo de inicio
        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            # Capturar tiempo antes de relanzar
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "Unhandled exception | %s %s | duration_ms=%.1f | request_id=%s",
                request.method,
                request.url.path,
                duration_ms,
                request_id,
            )
            raise

        # Calcular duración
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Loggear información estructurada
        logger.info(
            "%s %s | status=%d | duration_ms=%.1f | request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        # Agregar header X-Request-ID a la respuesta
        response.headers["X-Request-ID"] = request_id

        return response
