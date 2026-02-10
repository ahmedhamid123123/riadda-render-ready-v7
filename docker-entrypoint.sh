#!/usr/bin/env bash
set -e

echo "Starting entrypoint..."

# Allow disabling migrations/static collection (useful for one-off tasks)
if [ "${SKIP_MIGRATE:-}" = "1" ]; then
  echo "SKIP_MIGRATE=1 set, skipping migrate/collectstatic"
  exec "$@"
fi

# Determine whether we are using Postgres.
USE_POSTGRES=0
if [ -n "${DATABASE_URL:-}" ]; then
  case "${DATABASE_URL}" in
    postgres:*|postgresql:* ) USE_POSTGRES=1 ;;
  esac
elif [ -n "${DJANGO_DB_ENGINE:-}" ]; then
  case "${DJANGO_DB_ENGINE}" in
    *postgres* ) USE_POSTGRES=1 ;;
  esac
fi

if [ "${USE_POSTGRES}" = "1" ]; then
  HOST=${DJANGO_DB_HOST:-db}
  PORT=${DJANGO_DB_PORT:-5432}
  echo "Waiting for database at ${HOST}:${PORT}..."
  # Don't block forever: fail fast if DB isn't reachable.
  for i in $(seq 1 ${DB_WAIT_MAX_SECONDS:-60}); do
    if nc -z "${HOST}" "${PORT}"; then
      echo "Database is up"
      break
    fi
    if [ "$i" = "${DB_WAIT_MAX_SECONDS:-60}" ]; then
      echo "Database not reachable after ${DB_WAIT_MAX_SECONDS:-60}s" >&2
      exit 1
    fi
    sleep 1
  done
else
  echo "Postgres not detected (using SQLite or external DB config). Skipping DB wait."
fi

echo "Running migrations"
python manage.py migrate --noinput

echo "Collecting static files"
python manage.py collectstatic --noinput

echo "Entrypoint finished, executing CMD"
exec "$@"
