#!/bin/sh
set -eu

db_path="${SISP_DB_PATH:-/app/data/sisp.sqlite3}"
db_dir="$(dirname "$db_path")"
mkdir -p "$db_dir"
chown sisp:sisp "$db_dir"
if [ -f "$db_path" ]; then
  chown sisp:sisp "$db_path"
fi

port="${PORT:-${SISP_PORT:-8000}}"
exec gosu sisp gunicorn \
  --bind "0.0.0.0:${port}" \
  --workers 1 \
  --threads 4 \
  --timeout 60 \
  --graceful-timeout 30 \
  --access-logfile - \
  --error-logfile - \
  wsgi:application
