# Guía de Despliegue — RAT UCT

> **Proyecto:** Registro de Actividades de Tratamiento — Universidad Católica de Temuco
> **Versión:** 1.0.0 | **Fecha:** Julio 2026

---

## 1. Requisitos del Sistema

### Desarrollo Local

| Herramienta | Versión Mínima | Notas |
|-------------|---------------|-------|
| Python | ≥ 3.11 | Probado con 3.11 y 3.12 |
| Node.js | ≥ 18 | Para build del frontend |
| npm | ≥ 9 | Incluido con Node.js |
| Git | — | Control de versiones |

### Producción (Render / Fly.io / Docker)

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| RAM | 512 MB | 1 GB |
| CPU | 1 vCPU | 2 vCPU |
| Disco | 1 GB | 5 GB (para DuckDB) |
| SO | Linux (Debian/Ubuntu) | Alpine (Docker) o Debian |

DuckDB es extremadamente liviano; no requiere servidor de base de datos ni configuración de red.

---

## 2. Despliegue en Render

El proyecto está configurado para desplegarse en **Render** como Web Service. Sigue estos pasos:

### 2.1 Preparación

1. **Crear cuenta en [Render](https://render.com)**
2. **Conectar repositorio GitHub** con el proyecto RAT UCT

### 2.2 Configuración del Web Service

| Campo | Valor |
|-------|-------|
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free (Starter) o superior |

### 2.3 Variables de Entorno

| Variable | Valor | Propósito |
|----------|-------|-----------|
| `DB_PATH` | `/opt/render/project/src/rat_uct.db` | Ruta de la base de datos DuckDB |
| `PYTHON_VERSION` | `3.12.3` | Versión de Python (opcional) |

> **Nota:** En Render Free, el almacenamiento es efímero. La base de datos se perderá al redeployar. Para persistencia, considera:
> - Render Starter (persistencia de disco)
> - Subir/bajar el archivo `.db` manualmente desde la consola de Render
> - Migrar a PostgreSQL si la persistencia es crítica

### 2.4 Frontend Build

Render no tiene un paso separado para el build del frontend. Hay dos opciones:

**Opción A — Build local y commit del `static/`:**

```bash
# En tu máquina local
cd frontend
npm ci
npm run build
# Copiar el build a la raíz del proyecto
cp -r dist/* ../static/
# Commit y push
```

**Opción B — Usar el Dockerfile (multi-stage):**

Si usas Render con Docker runtime, el `Dockerfile` incluido construye automáticamente el frontend y lo copia al backend.

---

## 3. Build del Frontend

El frontend React se construye con Vite. El build de producción se sirve desde la carpeta `static/` en la raíz del proyecto.

### 3.1 Build Manual

```bash
cd frontend

# Instalar dependencias (una vez)
npm ci

# Build de producción → dist/
npm run build

# Copiar al backend (para servir con FastAPI)
cp -r dist/* ../static/
```

### 3.2 Desarrollo con Hot Reload

```bash
# Terminal 1: Backend
python app.py  # http://localhost:8000

# Terminal 2: Frontend con proxy
cd frontend
npm run dev   # http://localhost:5173 (proxy /api → :8000)
```

Vite está configurado para redirigir las llamadas a `/api` al backend en `localhost:8000` (ver `vite.config.js`):

```js
server: {
    port: 5173,
    proxy: {
        '/api': {
            target: 'http://localhost:8000',
            changeOrigin: true,
        }
    }
}
```

### 3.3 Linting

```bash
cd frontend
npm run lint  # oxlint
```

Backend (Python):

```bash
ruff check .   # Linting
ruff format .  # Formateo
```

---

## 4. Variables de Entorno

### `DB_PATH`

Define la ubicación del archivo DuckDB.

| Entorno | Valor típico |
|---------|-------------|
| **Desarrollo** | `rat_uct.db` (default, en la raíz del proyecto) |
| **Render** | `/opt/render/project/src/rat_uct.db` |
| **Docker** | `/data/rat_uct.db` (volumen montado) |
| **Fly.io** | `/data/rat_uct.db` (volume mount) |

```python
DB_PATH = Path(os.environ.get("DB_PATH", str(Path(__file__).parent / "rat_uct.db")))
```

### Otras variables (futuro)

| Variable | Propósito | Default |
|----------|-----------|---------|
| `HOST` | Host del servidor | `0.0.0.0` |
| `PORT` | Puerto del servidor | `8000` (Render asigna automáticamente) |

---

## 5. Docker

### 5.1 Dockerfile Existente

El proyecto incluye un `Dockerfile` multi-stage:

```dockerfile
# Stage 1: Build React frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend + serve static
FROM python:3.12-slim
WORKDIR /app

# DuckDB requiere libstdc++
RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend code
COPY main.py database.py models.py seed.py ./
COPY RAT_UCT_v1_Julio_2026.xlsx ./

# Frontend build
COPY --from=frontend-builder /app/frontend/dist ./static

# DuckDB data directory
RUN mkdir -p /data

EXPOSE 8080

CMD ["sh", "-c", "python seed.py && uvicorn main:app --host 0.0.0.0 --port 8080"]
```

> **Importante:** El Dockerfile actual apunta a `main:app` (versión monolítica original). Si usas la versión modularizada, cambia el CMD a `uvicorn app:app --host 0.0.0.0 --port 8080`.

### 5.2 Build y Ejecución Local

```bash
# Build de la imagen
docker build -t rat-uct .

# Ejecutar con volumen para persistencia de DB
docker run -d \
  --name rat-uct \
  -p 8080:8080 \
  -v $PWD/rat_uct.db:/data/rat_uct.db \
  -e DB_PATH=/data/rat_uct.db \
  rat-uct

# Verificar
curl http://localhost:8080/api/actividades/total
```

### 5.3 Docker Compose (opcional)

```yaml
version: '3.8'
services:
  rat-uct:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_PATH=/data/rat_uct.db
    volumes:
      - ./data:/data
    restart: unless-stopped
```

---

## 6. Tailscale para Acceso Remoto

Tailscale permite acceder al RAT UCT de forma segura desde cualquier lugar sin exponer puertos a internet.

### 6.1 Instalación en el servidor

```bash
# Instalar Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Autenticar
sudo tailscale up

# Verificar estado
tailscale status
```

### 6.2 Uso desde el equipo local

Una vez instalado Tailscale en ambos extremos:

```bash
# Desde tu laptop, accedes a la IP de Tailscale del servidor
curl http://100.x.y.z:8000/api/actividades/total
```

### 6.3 Ventajas

- **Red privada** — No expones puertos a internet público
- **Autenticación** — Integrada con SSO (Google, Microsoft, etc.)
- **Latencia** — Conexión directa (peer-to-peer) cuando es posible
- **Gratuito** — Hasta 3 usuarios en el plan Free

---

## 7. Comandos de Verificación Post-Deploy

### 7.1 Health Check Básico

```bash
# Server running
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/
# → 200 (SPA), 404 (si no hay static/, pero el server responde)
```

### 7.2 Verificar API

```bash
# Listar actividades
curl -s http://localhost:8000/api/actividades | head -c 200

# Estadísticas
curl -s http://localhost:8000/api/actividades/total | python -m json.tool

# Áreas sembradas
curl -s http://localhost:8000/api/areas | python -m json.tool

# Reporte resumen
curl -s http://localhost:8000/api/reportes/resumen | python -m json.tool

# Fases de implementación
curl -s http://localhost:8000/api/fases | python -m json.tool
```

### 7.3 Prueba de Creación

```bash
# Crear una actividad de prueba
curl -s -X POST http://localhost:8000/api/actividades \
  -H "Content-Type: application/json" \
  -d '{
    "actividad_tratamiento": "Prueba post-deploy",
    "finalidad": "Verificar que el despliegue funciona",
    "base_licitud": "Consentimiento",
    "plazo_conservacion": "1 año"
  }' | python -m json.tool
```

### 7.4 Verificar Frontend

```bash
# El frontend SPA debe servir el index.html
curl -s http://localhost:8000/ | head -5
# → <!doctype html>
# → <html lang="es">
# →   <head>
# →     <meta charset="UTF-8" />
# →     ...

# Verificar que los assets JS se sirven
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/src/main.jsx
# → 200 (si hay static/ con archivos)
```

### 7.5 Verificar Documentación OpenAPI

```bash
# Swagger UI
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs
# → 200

# OpenAPI JSON
curl -s http://localhost:8000/openapi.json | python -m json.tool | head -20
```

### 7.6 Evaluar Riesgo de Todas las Actividades

```bash
curl -s -X POST http://localhost:8000/api/actividades/evaluar-riesgo-todas \
  | python -m json.tool
```

### 7.7 Verificar Base de Datos

```bash
# Desde Python
python -c "
from database import get_connection
conn = get_connection()
print('Tablas:', conn.execute(
  \"SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'\"
).fetchall())
print('Actividades:', conn.execute('SELECT count(*) FROM actividades').fetchone()[0])
print('Áreas:', conn.execute('SELECT count(*) FROM areas').fetchone()[0])
conn.close()
"
```

---

## 8. Checklist de Despliegue

| # | Paso | Comando/Verificación |
|---|------|----------------------|
| 1 | ✅ Variables de entorno configuradas | `echo $DB_PATH` |
| 2 | ✅ Base de datos inicializada | Ver `rat_uct.db` existe |
| 3 | ✅ Áreas sembradas | `GET /api/areas` → 12 áreas |
| 4 | ✅ Frontend construido | `static/` existe con `index.html` |
| 5 | ✅ API responde | `GET /api/actividades/total` → JSON |
| 6 | ✅ Documentación OpenAPI | `GET /docs` → 200 |
| 7 | ✅ SPA se sirve | `GET /` → HTML en vez de 404 |
| 8 | ✅ Crear actividad de prueba | `POST /api/actividades` → 201 |
| 9 | ✅ Evaluar riesgo funcional | `POST /.../evaluar-riesgo` → JSON |
| 10 | ✅ Tailscale conectado (si aplica) | `tailscale status` |

---

## 9. Solución de Problemas

### Error: `duckdb.duckdb.CatalogException: Table with name actividades already exists`

El esquema se inicializa con `CREATE TABLE IF NOT EXISTS`, es seguro. Ignorar.

### Error: `ModuleNotFoundError: No module named 'routes'`

Asegúrate de ejecutar `python app.py` (modularizado) y no `python main.py` (monolito original).

### Error: Frontend no se sirve (404 en `/`)

```bash
# Verificar que la carpeta static/ existe y tiene contenido
ls -la static/
# Si está vacía, reconstruir:
cd frontend && npm run build && cp -r dist/* ../static/
```

### Error: `sqlite3.OperationalError` o problemas de permisos con DuckDB

```bash
# Asegurar permisos de escritura para el archivo .db
chmod 666 rat_uct.db
# O ejecutar como usuario con permisos en el directorio
```

### Error: Puerto ocupado

```bash
# Encontrar proceso usando el puerto
lsof -i :8000
# Matar proceso
kill -9 <PID>
# O usar puerto alternativo
PORT=8001 python app.py
```

### Error: CORS en desarrollo

Si el frontend Vite no puede conectar al backend:
1. Verificar que `vite.config.js` tenga el proxy correcto
2. O abrir CORS en el backend (ya configurado como `allow_origins=["*"]`)
3. O acceder directamente a `http://localhost:8000` en el navegador

---

## 10. Mantenimiento

### Respaldo de Base de Datos

```bash
# DuckDB es un solo archivo — copia simple
cp rat_uct.db rat_uct_backup_$(date +%Y%m%d).db
```

### Actualización

```bash
git pull origin main
cd frontend && npm ci && npm run build && cp -r dist/* ../static/
cd ..
python app.py  # Las migraciones se ejecutan automáticamente
```

### Monitoreo de Logs

```bash
# En producción (Render)
# Desde el dashboard de Render → Logs

# En desarrollo
python app.py 2>&1 | tee rat-uct.log

# Ver errores recientes
grep -i "error\|exception\|traceback" rat-uct.log | tail -20
```
