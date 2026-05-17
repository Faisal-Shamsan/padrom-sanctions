# Multi-stage build — keeps the runtime image lean (~200 MB vs ~800 MB).
# Stage 1: install deps with uv into a venv.
# Stage 2: copy only the venv + source into a slim runtime image.

# ── builder ──────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv from the official distroless image (no pip needed)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency manifests first so Docker can cache this layer
COPY pyproject.toml uv.lock* ./

# --no-dev: skip dev deps in the production image
# --frozen: fail if uv.lock is out of sync with pyproject.toml
RUN uv sync --frozen --no-dev

# ── runtime ──────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Non-root user: least-privilege principle
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copy the venv (with compiled C extensions) from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source
COPY src/ ./src/

# Prepend venv bin so uvicorn / python resolve from the venv
ENV PATH="/app/.venv/bin:$PATH"

USER app

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
