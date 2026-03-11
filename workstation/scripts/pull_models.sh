#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

load_repo_env
require_command ollama
print_ollama_settings

echo "[INFO] Pulling primary code model: ${OLLAMA_CODE_MODEL}"
ollama pull "${OLLAMA_CODE_MODEL}"

echo "[INFO] Pulling reasoning model: ${OLLAMA_REASON_MODEL}"
ollama pull "${OLLAMA_REASON_MODEL}"

echo "[INFO] Pulling lightweight fallback model: ${OLLAMA_FALLBACK_MODEL}"
ollama pull "${OLLAMA_FALLBACK_MODEL}"

if [[ "${OLLAMA_PULL_EXPERIMENTAL}" == "true" ]]; then
  echo "[INFO] Pulling larger experimental model: ${OLLAMA_EXPERIMENTAL_MODEL}"
  ollama pull "${OLLAMA_EXPERIMENTAL_MODEL}"
else
  echo "[INFO] Skipping larger experimental model. Set OLLAMA_PULL_EXPERIMENTAL=true to enable it."
fi

echo "[INFO] Installed models:"
ollama list
