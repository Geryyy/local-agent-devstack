#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

load_repo_env
require_command curl

MODEL="${1:-${OLLAMA_CODE_MODEL}}"
BASE_URL="$(ollama_base_url)"

echo "[INFO] Sending warm-up request to ${MODEL} via ${BASE_URL}"
curl -sS "${BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${MODEL}\",
    \"messages\": [{\"role\": \"user\", \"content\": \"ping\"}],
    \"stream\": false
  }" >/dev/null

echo "[INFO] Warm-up request complete."
