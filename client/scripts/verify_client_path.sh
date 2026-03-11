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

LOCAL_BASE_URL="${1:-http://${LOCAL_CHECK_HOST}:${LOCAL_OLLAMA_PORT}}"
DEVCONTAINER_BASE_URL="${2:-http://host.docker.internal:${LOCAL_OLLAMA_PORT}}"

print_client_settings

echo "[INFO] Checking laptop-local tunnel endpoint: ${LOCAL_BASE_URL}/api/tags"
curl -fsS "${LOCAL_BASE_URL}/api/tags" >/dev/null
echo "[INFO] Laptop-local tunnel is reachable."

echo "[INFO] Checking devcontainer-facing endpoint: ${DEVCONTAINER_BASE_URL}/api/tags"
if curl -fsS "${DEVCONTAINER_BASE_URL}/api/tags" >/dev/null; then
  echo "[INFO] Devcontainer-facing endpoint is reachable."
else
  echo "[WARN] Devcontainer-facing endpoint is not reachable from this machine."
  if [[ "${LOCAL_OLLAMA_BIND_HOST}" == "127.0.0.1" ]]; then
    echo "[WARN] The SSH tunnel is bound to host loopback only."
    echo "[WARN] A bridge-network devcontainer cannot reach that via host.docker.internal."
    echo "[WARN] Set LOCAL_OLLAMA_BIND_HOST to the Docker bridge IP or 0.0.0.0, then reopen the tunnel."
  else
    echo "[WARN] This is expected unless you are running on the laptop host with host.docker.internal configured."
  fi
fi

echo "[INFO] Client path validation complete."
