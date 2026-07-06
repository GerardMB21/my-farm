# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12-slim
ARG POETRY_VERSION=2.4.1

FROM python:${PYTHON_VERSION} AS builder

ARG POETRY_VERSION
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PIP_NO_CACHE_DIR=1

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

# Installed before the app source is copied so this layer is only
# invalidated when dependencies actually change.
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-interaction --no-ansi

COPY app ./app


FROM python:${PYTHON_VERSION} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}" \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    APP_LOG_LEVEL=info

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder --chown=app:app /app/.venv ./.venv
COPY --chown=app:app app ./app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"APP_PORT\"]}/health', timeout=2)"

# Reload is a dev-only concern (see manage.py); production scales via
# container replicas at the orchestrator level, not in-process workers.
CMD ["sh", "-c", "uvicorn app.main:app --host $APP_HOST --port $APP_PORT --log-level $APP_LOG_LEVEL"]
