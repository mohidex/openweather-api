FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
ENV AIOHTTP_NO_EXTENSIONS 1

WORKDIR /app

# Runtime dependencies
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        dumb-init \
        netcat-openbsd \
        libpq-dev \
        binutils \
        libproj-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential


# Application dependencies
ADD requirements.txt /app/
RUN pip install -r requirements.txt


COPY ./scripts /app/scripts

COPY ./src /app/

RUN chmod +x /app/scripts/wait-for-it.sh
RUN chmod +x /app/scripts/docker-entrypoint.sh

# Collect static files
RUN set -ex \
    && mkdir -p /var/www/django-static \
    && cd /app \
    && python manage.py collectstatic --no-input


ENTRYPOINT ["dumb-init", "/app/scripts/docker-entrypoint.sh"]
