#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

load_repo_env
require_command curl

LOCAL_CHECK_HOST="${LOCAL_OLLAMA_BIND_HOST}"
if [[ "${LOCAL_CHECK_HOST}" == "0.0.0.0" ]]; then
  LOCAL_CHECK_HOST="127.0.0.1"
fi

BASE_URL="${1:-http://${LOCAL_CHECK_HOST}:${LOCAL_OLLAMA_PORT}}"

echo "[INFO] Querying ${BASE_URL}/api/tags"
curl -sS "${BASE_URL}/api/tags" | sed 's/},{/},\n{/g'
echo
