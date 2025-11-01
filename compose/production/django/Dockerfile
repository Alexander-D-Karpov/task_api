ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION} as python

FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=production

RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential \
  libpq-dev

FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=production
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

# Create venv and install dependencies (no dev dependencies)
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -e .

ENV PATH="/venv/bin:$PATH"

# Create django user
RUN addgroup --system django && \
    adduser --system --ingroup django django

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown django /start

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker
RUN chown django /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat
RUN chown django /start-celerybeat

COPY ./compose/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower
RUN chown django /start-flower

RUN chown -R django:django ${APP_HOME}

USER django

ENTRYPOINT ["/entrypoint"]
