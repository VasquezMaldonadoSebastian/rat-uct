"""
RAT UCT — FastAPI Backend (entry point)
=========================================

Punto de entrada de la aplicación. Inicializa DB, registra routers,
configura CORS, sirve estáticos y arranca uvicorn.

Uso:
    python app.py               # Arranca en http://0.0.0.0:8000
    http://localhost:8000/docs   # Documentación OpenAPI interactiva
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import get_connection, init_db, seed_areas_uct
from routes.actividades import router as actividades_router
from routes.areas import router as areas_router
from routes.procesos import router as procesos_router
from routes.encargados import router as encargados_router
from routes.reportes import router as reportes_router
from routes.eipd import router as eipd_router
from routes.brechas import router as brechas_router
from routes.arsop import router as arsop_router
from routes.dpa import router as dpa_router
from routes.fases import router as fases_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa DB al arrancar."""
    conn = get_connection()
    init_db(conn)
    seed_areas_uct(conn)
    conn.close()
    yield


app = FastAPI(
    title="RAT UCT — Registro de Actividades de Tratamiento",
    description="API para gestionar el RAT institucional de la Universidad Católica de Temuco (Ley 21.719)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Registrar routers ──────────────────────────────────────────────────────
app.include_router(actividades_router)
app.include_router(areas_router)
app.include_router(procesos_router)
app.include_router(encargados_router)
app.include_router(reportes_router)
app.include_router(eipd_router)
app.include_router(brechas_router)
app.include_router(arsop_router)
app.include_router(dpa_router)
app.include_router(fases_router)

# ─── Servir frontend estático (producción) ──────────────────────────────────
# En producción (Fly.io / Docker), la carpeta static/ contiene el build de React.
# FastAPI sirve la SPA después de todas las rutas API registradas.
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
