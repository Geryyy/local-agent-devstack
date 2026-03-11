#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

load_repo_env() {
  if [[ -f "${REPO_ROOT}/.env" ]]; then
    echo "[INFO] Loading ${REPO_ROOT}/.env"
    set -a
    # shellcheck disable=SC1091
    source "${REPO_ROOT}/.env"
    set +a
  fi

  export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1}"
  export OLLAMA_PORT="${OLLAMA_PORT:-11434}"
  export OLLAMA_CODE_MODEL="${OLLAMA_CODE_MODEL:-gpt-oss:20b}"
  export OLLAMA_REASON_MODEL="${OLLAMA_REASON_MODEL:-gpt-oss:20b}"
  export OLLAMA_FALLBACK_MODEL="${OLLAMA_FALLBACK_MODEL:-qwen2.5-coder:7b}"
  export OLLAMA_PULL_EXPERIMENTAL="${OLLAMA_PULL_EXPERIMENTAL:-false}"
  export OLLAMA_EXPERIMENTAL_MODEL="${OLLAMA_EXPERIMENTAL_MODEL:-qwen3-coder:30b}"
}

ollama_base_url() {
  printf 'http://%s:%s' "${OLLAMA_HOST}" "${OLLAMA_PORT}"
}

print_ollama_settings() {
  echo "[INFO] Ollama endpoint: $(ollama_base_url)"
  echo "[INFO] Code model: ${OLLAMA_CODE_MODEL}"
  echo "[INFO] Reasoning model: ${OLLAMA_REASON_MODEL}"
  echo "[INFO] Fallback model: ${OLLAMA_FALLBACK_MODEL}"
  echo "[INFO] Pull experimental model: ${OLLAMA_PULL_EXPERIMENTAL}"
  if [[ "${OLLAMA_PULL_EXPERIMENTAL}" == "true" ]]; then
    echo "[INFO] Experimental model: ${OLLAMA_EXPERIMENTAL_MODEL}"
  fi
}

require_command() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "[ERROR] Required command not found: ${cmd}"
    exit 1
  fi
}
