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

  export WORKSTATION_HOST="${WORKSTATION_HOST:-WORKSTATION_HOST_OR_IP}"
  export WORKSTATION_USER="${WORKSTATION_USER:-YOUR_WORKSTATION_USER}"
  export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1}"
  export OLLAMA_PORT="${OLLAMA_PORT:-11434}"
  export LOCAL_OLLAMA_PORT="${LOCAL_OLLAMA_PORT:-11434}"
}

require_command() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "[ERROR] Required command not found: ${cmd}"
    exit 1
  fi
}

print_client_settings() {
  echo "[INFO] Workstation SSH target: ${WORKSTATION_USER}@${WORKSTATION_HOST}"
  echo "[INFO] Laptop local forward port: ${LOCAL_OLLAMA_PORT}"
  echo "[INFO] Workstation Ollama endpoint: ${OLLAMA_HOST}:${OLLAMA_PORT}"
}
