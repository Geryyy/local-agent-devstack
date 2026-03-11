#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

load_repo_env
require_command curl

LOCAL_BASE_URL="${1:-http://127.0.0.1:${LOCAL_OLLAMA_PORT}}"
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
  echo "[WARN] This is expected unless you are running on the laptop host with host.docker.internal configured."
fi

echo "[INFO] Client path validation complete."
