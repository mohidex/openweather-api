# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV AIOHTTP_NO_EXTENSIONS 1

WORKDIR /app

ARG UID=10001
RUN adduser --system --uid "${UID}" --home /var/empty --shell /bin/nologin appuser \
    && addgroup --system appuser

# Runtime dependencies
RUN --mount=type=cache,target=/var/lib/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && apt-get install -y --no-install-recommends \
        dumb-init \
        netcat-openbsd \
        libpq-dev \
        binutils \
        gettext \
        libproj-dev \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


FROM base AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Application dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

FROM base AS production

COPY --from=builder --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code
COPY ./src /app/
COPY ./docs /docs

# Copy the scripts files
COPY ./scripts /scripts
RUN chmod +x /scripts/wait-for-it.sh /scripts/docker-entrypoint.sh

# Copy the locale files
COPY ./locale /app/locale

# Collect static files
RUN set -ex \
    && mkdir -p /var/www/django-static \
    && cd /app \
    && python manage.py collectstatic --no-input

# Run compilation step for i18n
RUN set -x \
    && python /app/manage.py compilemessages

# Run the application as a non-root user
USER appuser
ENTRYPOINT ["dumb-init", "/scripts/docker-entrypoint.sh"]
