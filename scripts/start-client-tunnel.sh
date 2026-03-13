#!/usr/bin/env bash
set -euo pipefail

WORKSTATION_USER="${1:-user}"
WORKSTATION_HOST="${2:-workstation}"

echo "[INFO] Opening SSH tunnels to ${WORKSTATION_USER}@${WORKSTATION_HOST}"
echo "[INFO] Recommended for LangGraph Studio browser access because Studio connects cleanly to http://127.0.0.1:2024."

exec ssh \
  -N \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -L 3000:localhost:3000 \
  -L 2024:localhost:2024 \
  -L 8001:localhost:8001 \
  -L 11434:localhost:11434 \
  -L 6333:localhost:6333 \
  "${WORKSTATION_USER}@${WORKSTATION_HOST}"
