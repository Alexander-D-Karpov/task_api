ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION} as python

FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local

RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential \
  libpq-dev

FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y \
  libpq-dev \
  gettext \
  curl \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ${APP_HOME}/
COPY . ${APP_HOME}

# Create venv and install dependencies
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -e ".[dev]"

ENV PATH="/venv/bin:$PATH"

# Copy and setup scripts
RUN cp /app/compose/production/django/entrypoint /entrypoint && \
    sed -i 's/\r$//g' /entrypoint && \
    chmod +x /entrypoint

RUN cp /app/compose/local/django/start /start && \
    sed -i 's/\r$//g' /start && \
    chmod +x /start

RUN cp /app/compose/local/django/celery/worker/start /start-celeryworker && \
    sed -i 's/\r$//g' /start-celeryworker && \
    chmod +x /start-celeryworker

RUN cp /app/compose/local/django/celery/beat/start /start-celerybeat && \
    sed -i 's/\r$//g' /start-celerybeat && \
    chmod +x /start-celerybeat

RUN cp /app/compose/local/django/celery/flower/start /start-flower && \
    sed -i 's/\r$//g' /start-flower && \
    chmod +x /start-flower

ENTRYPOINT ["/entrypoint"]
