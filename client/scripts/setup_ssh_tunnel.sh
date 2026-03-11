#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <workstation-user> <workstation-host> [local-port] [remote-port]"
  echo "Example: $0 youruser workstation.local 11434 11434"
  exit 1
fi

WORKSTATION_USER="$1"
WORKSTATION_HOST="$2"
LOCAL_PORT="${3:-11434}"
REMOTE_PORT="${4:-11434}"

echo "[INFO] Opening SSH tunnel:"
echo "       localhost:${LOCAL_PORT} -> ${WORKSTATION_HOST}:localhost:${REMOTE_PORT}"

exec ssh -N   -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}"   "${WORKSTATION_USER}@${WORKSTATION_HOST}"
