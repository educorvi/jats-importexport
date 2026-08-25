# Stage 1: build the virtual environment
FROM rockylinux/rockylinux:10-ubi-micro AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python

WORKDIR /app

# Install dependencies first (layer-cached until lockfile changes)
COPY applications/api/pyproject.toml uv.lock ./
COPY packages/jats-classes/pyproject.toml packages/jats-classes/pyproject.toml
COPY packages/jats-exporters/pyproject.toml packages/jats-exporters/pyproject.toml
COPY packages/jats-storage-adapters/pyproject.toml packages/jats-storage-adapters/pyproject.toml
COPY applications/api/pyproject.toml applications/api/pyproject.toml
RUN  --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable --no-install-workspace --package api

# Copy source and do the full install
COPY packages packages/
COPY applications/api/ applications/api/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable --package api


# WeasyPrint system dependencies
FROM rockylinux/rockylinux:10-ubi AS packages

ARG RUN_DEPS="pango harfbuzz gdk-pixbuf2 libffi-devel shadow-utils shared-mime-info"

RUN mkdir -p /micro-root \
    && dnf install -y \
        --installroot=/micro-root \
        --releasever=10 \
        --setopt=install_weak_deps=false \
        --setopt=keepcache=false \
        $RUN_DEPS \
    && rm -rf /micro-root/var/cache/dnf

# Stage 2: lean runtime image
FROM rockylinux/rockylinux:10-ubi-micro AS runtime

# WeasyPrint system dependencies
COPY --from=packages /micro-root/ /
COPY --from=builder /opt/uv-python /opt/uv-python

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
