#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

VENV_DIR="${ROOT_DIR}/.venv-roo-mcp"
export AGENT_API_BASE_URL="${AGENT_API_BASE_URL:-http://127.0.0.1:2024}"

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  echo "[INFO] Creating Roo MCP virtualenv at ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
  echo "[INFO] Installing MCP bridge dependencies"
  "${VENV_DIR}/bin/pip" install -r agent_server/requirements.txt
fi

exec "${VENV_DIR}/bin/python" -m agent_server.roo_mcp_server
