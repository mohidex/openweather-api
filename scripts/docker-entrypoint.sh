#!/bin/bash

set -e

WAIT_FLAGS="${WAIT_FLAGS:=-t 120}"

if [ -n "$PG_HOST" ]; then
    /app/scripts/wait-for-it.sh "$PG_HOST" 5432 "$WAIT_FLAGS"
fi

if [ -n "$REDIS_HOST" ]; then
    /app/scripts/wait-for-it.sh "$REDIS_HOST" 6379 "$WAIT_FLAGS"
fi


if [ "$MIGRATE_ON_STARTUP" = "True" -o "$MIGRATE_ON_STARTUP" = "true" ]; then
    echo "Running Django migrate command:"
    python /app/manage.py migrate
fi

exec "$@"