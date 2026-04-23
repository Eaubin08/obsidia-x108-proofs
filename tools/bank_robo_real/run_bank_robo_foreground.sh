#!/usr/bin/env bash
set -euo pipefail

REPO_PATH="${1:?repo path required}"
ENV_FILE="${2:?env file required}"
PORT_VALUE="${3:-3018}"

cd "$REPO_PATH"

set -a
. "$ENV_FILE"
set +a

export NODE_ENV=development
export PORT="$PORT_VALUE"

pnpm exec tsx server/_core/index.ts