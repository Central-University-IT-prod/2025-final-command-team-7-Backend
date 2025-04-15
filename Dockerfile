FROM docker.io/python:3.13.2-alpine3.21 as builder

COPY --from=ghcr.io/astral-sh/uv:0.5.30 /uv /uvx /opt/uv/bin/

WORKDIR /tmp/backend
ENV PYTHONOPTIMIZE=2 \
    UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1 \
    UV_NO_CACHE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/backend \
    UV_PYTHON=/usr/local/bin/python
COPY pyproject.toml uv.lock .
RUN /opt/uv/bin/uv sync --no-dev --no-install-project
COPY src src
RUN /opt/uv/bin/uv sync --no-dev --no-editable


FROM docker.io/python:3.13.2-alpine3.21

COPY --from=builder /opt/backend /opt/backend
COPY alembic.ini /opt/backend/alembic.ini

RUN addgroup -S backend \
    && adduser -G backend -S -D -H backend
USER backend

ENV PYTHONOPTIMIZE=2 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LITESTAR_APP=backend.main.app:create_app \
    LITESTAR_HOST=0.0.0.0 \
    LITESTAR_PORT=8080 \
    ALEMBIC_CONFIG=/opt/backend/alembic.ini \
    PATH="/opt/backend/bin:$PATH"

CMD ["litestar", "run"]
