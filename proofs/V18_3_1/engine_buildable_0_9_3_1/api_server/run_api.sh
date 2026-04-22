#!/usr/bin/env bash
set -euo pipefail

# Local only (default):
#   export OBSIDIA_BIND=local
# LAN:
#   export OBSIDIA_BIND=lan
# Public:
#   export OBSIDIA_BIND=public

BIND="${OBSIDIA_BIND:-local}"
PORT="${OBSIDIA_PORT:-8000}"

HOST="127.0.0.1"
if [ "$BIND" = "lan" ]; then
  HOST="0.0.0.0"
elif [ "$BIND" = "public" ]; then
  HOST="0.0.0.0"
fi

python -m uvicorn api_server.main:app --host "$HOST" --port "$PORT"
