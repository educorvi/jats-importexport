# Stage 1: build the virtual environment
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Install dependencies first (layer-cached until lockfile changes)
COPY applications/api/pyproject.toml uv.lock ./
COPY packages/jats-classes/pyproject.toml packages/jats-classes/pyproject.toml
COPY packages/jats-exporters/pyproject.toml packages/jats-exporters/pyproject.toml
COPY packages/jats-storage-adapters/pyproject.toml packages/jats-storage-adapters/pyproject.toml
COPY applications/api/pyproject.toml applications/api/pyproject.toml
RUN uv sync --frozen --no-dev --no-editable --no-install-workspace --package api

# Copy source and do the full install
COPY packages packages/
COPY applications/api/ applications/api/
RUN uv sync --frozen --no-dev --no-editable --package api


# Stage 2: lean runtime image
FROM python:3.13-slim AS runtime

# WeasyPrint system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    API_RELOAD=false

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

USER appuser

EXPOSE 8000

CMD ["start-api"]
