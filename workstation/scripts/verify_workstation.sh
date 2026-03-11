#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

load_repo_env
require_command curl
require_command ollama

BASE_URL="$(ollama_base_url)"
PROMPT="${1:-ping}"

print_ollama_settings

echo "[INFO] Checking Ollama service status"
if command -v systemctl >/dev/null 2>&1; then
  if systemctl is-active --quiet ollama; then
    echo "[INFO] systemd service 'ollama' is active"
  else
    echo "[ERROR] systemd service 'ollama' is not active"
    echo "[ERROR] Try: sudo systemctl start ollama"
    exit 1
  fi
else
  echo "[WARN] systemctl not available. Skipping service manager check."
fi

echo "[INFO] Checking Ollama API reachability at ${BASE_URL}/api/tags"
TAGS_RESPONSE="$(curl -fsS "${BASE_URL}/api/tags")"

for model in "${OLLAMA_CODE_MODEL}" "${OLLAMA_REASON_MODEL}" "${OLLAMA_FALLBACK_MODEL}"; do
  if grep -Fq "\"name\":\"${model}\"" <<<"${TAGS_RESPONSE}"; then
    echo "[INFO] Model available: ${model}"
  else
    echo "[ERROR] Model missing: ${model}"
    echo "[ERROR] Run: ./workstation/scripts/pull_models.sh"
    exit 1
  fi
done

echo "[INFO] Running generation smoke test against ${OLLAMA_CODE_MODEL}"
GENERATE_RESPONSE="$(curl -fsS "${BASE_URL}/api/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${OLLAMA_CODE_MODEL}\",
    \"prompt\": \"${PROMPT}\",
    \"stream\": false
  }")"

if grep -Fq '"response":"' <<<"${GENERATE_RESPONSE}"; then
  echo "[INFO] Generation smoke test succeeded."
else
  echo "[ERROR] Generation smoke test failed."
  echo "[ERROR] Raw response: ${GENERATE_RESPONSE}"
  exit 1
fi

echo "[INFO] Workstation validation complete."
