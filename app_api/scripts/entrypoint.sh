#!/usr/bin/env sh
set -e

# apply migrations
litestar database upgrade --no-prompt

# bootstrap db (only runs when db in empty)
PYTHONPATH=. python scripts/bootstrap_db.py

litestar run \
  --host 0.0.0.0 \
  --port 8000 \
  --wc "${LITESTAR_WORKERS:-1}"
