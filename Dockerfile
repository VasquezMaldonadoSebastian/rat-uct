# ─── Stage 1: Build React frontend ───────────────────────────────────────────
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Python backend + serve static ──────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# DuckDB requires libstdc++
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

# DuckDB data directory (mounted as volume in production)
RUN mkdir -p /data

EXPOSE 8080

# Use /data for persistent DuckDB, serve static from ./static
# Init DB + seed data from Excel, then start server
CMD ["sh", "-c", "python seed.py && uvicorn main:app --host 0.0.0.0 --port 8080"]
