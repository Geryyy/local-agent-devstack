#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:11434}"

echo "[INFO] Querying ${BASE_URL}/api/tags"
curl -sS "${BASE_URL}/api/tags" | sed 's/},{/},\n{/g'
echo
