# ─── Stage 1: Build React frontend ───────────────────────────────────────────
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Seed data preparation (separada de runtime) ────────────────────
# Crea una base DuckDB pre-sembrada en build time.
# En producción, seed.py se ejecuta en CMD pero salta
# automáticamente si ya encuentra datos (es idempotente).
FROM python:3.12-slim AS seed-stage
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY seed.py RAT_UCT_v1_Julio_2026.xlsx ./
RUN python seed.py

# ─── Stage 3: Runtime image ──────────────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# ── System dependencies (capa única fusionada) ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ──
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Backend code (archivos específicos, sin wildcards) ──
COPY app.py utils.py database.py models.py seed.py ./
COPY routes/ ./routes/

# ── Frontend build ──
COPY --from=frontend-builder /app/frontend/dist ./static

# ── Pre-seeded database (fallback si no hay volumen montado) ──
COPY --from=seed-stage /app/rat_uct.db ./

# ── Excel necesario para sembrar bases nuevas (volúmenes limpios) ──
COPY RAT_UCT_v1_Julio_2026.xlsx ./

# ── Data directory para volúmenes persistentes ──
RUN mkdir -p /data

# ── Non-root user ──
RUN adduser --system --disabled-password --no-create-home appuser && \
    chown -R appuser:appuser /app /data

USER appuser

EXPOSE 8080

# ── Healthcheck: verifica que la API responde ──
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/api/fases || exit 1

# ── Init DB + seed (idempotente: salta si ya hay datos) y arranca servidor ──
CMD ["sh", "-c", "python seed.py && uvicorn app:app --host 0.0.0.0 --port 8080"]
