#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

load_repo_env
require_command ssh

WORKSTATION_USER="${1:-${WORKSTATION_USER}}"
WORKSTATION_HOST="${2:-${WORKSTATION_HOST}}"
LOCAL_PORT="${3:-${LOCAL_OLLAMA_PORT}}"
REMOTE_PORT="${4:-${OLLAMA_PORT}}"

if [[ "${WORKSTATION_USER}" == "YOUR_WORKSTATION_USER" ]] || [[ "${WORKSTATION_HOST}" == "WORKSTATION_HOST_OR_IP" ]]; then
  echo "Usage: $0 [workstation-user] [workstation-host] [local-port] [remote-port]"
  echo "Set WORKSTATION_USER and WORKSTATION_HOST in .env, or pass them explicitly."
  echo "Example: $0 youruser workstation.local 11434 11434"
  exit 1
fi

print_client_settings

echo "[INFO] Opening SSH tunnel:"
echo "       localhost:${LOCAL_PORT} -> ${WORKSTATION_HOST}:localhost:${REMOTE_PORT}"

exec ssh \
  -N \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" \
  "${WORKSTATION_USER}@${WORKSTATION_HOST}"
