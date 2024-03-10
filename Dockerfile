# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV AIOHTTP_NO_EXTENSIONS 1

WORKDIR /app

ARG UID=10001
RUN adduser --system --uid "${UID}" --home /var/empty --shell /bin/nologin appuser \
    && addgroup --system appuser

# Runtime dependencies
RUN \
    --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        dumb-init \
        netcat-openbsd \
        libpq-dev \
        binutils \
        gettext \
        libproj-dev \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Application dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the application code
COPY ./src /app/
COPY ./docs /docs

# Copy the scripts files
COPY ./scripts /scripts
RUN chmod +x /scripts/wait-for-it.sh /scripts/docker-entrypoint.sh

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
