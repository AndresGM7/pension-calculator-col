# ============================================================
# Multi-stage Dockerfile - pension-calculator
# Stage 1: builder  ->  instala dependencias en un venv limpio
# Stage 2: runtime  ->  imagen minima, sin root, sin build tools
# ============================================================

# ── Stage 1: builder ────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Instalar dependencias de sistema solo para compilacion
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Crear venv aislado
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar codigo fuente y pyproject.toml para que setuptools pueda construir el paquete
COPY pyproject.toml ./
COPY src/ ./src/
# Instalar solo deps minimas (sin extras pagos/db/cache por ahora)
RUN pip install --upgrade pip && \
    pip install .

# ── Stage 2: runtime ────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app

WORKDIR /app

# Copiar dependencias del builder
COPY --from=builder /opt/venv /opt/venv

# Copiar codigo
COPY --chown=app:app src/ ./src/
COPY --chown=app:app pyproject.toml ./
COPY --chown=app:app data/ ./data/

# Crear usuario no-root y dar ownership
RUN useradd -m -u 1000 app 2>/dev/null || true && \
    chown -R app:app /app
USER app

EXPOSE 8000

# Comando de inicio (1 worker, Fly.io escala horizontal)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
