#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-langgraph"
PORT="${LANGGRAPH_API_PORT:-2024}"
HOST="${LANGGRAPH_API_HOST:-0.0.0.0}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

rewrite_host() {
  local value="$1"
  value="${value//http:\/\/ollama:11434/http://127.0.0.1:11434}"
  value="${value//http:\/\/qdrant:6333/http://127.0.0.1:6333}"
  value="${value//redis:\/\/redis:6379/redis://127.0.0.1:6379}"
  value="${value//@postgres:5432/@127.0.0.1:5432}"
  printf '%s\n' "${value}"
}

require_tcp() {
  local label="$1"
  local host="$2"
  local port="$3"
  if ! python3 - "$host" "$port" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
with socket.socket() as sock:
    sock.settimeout(1.5)
    try:
        sock.connect((host, port))
    except OSError:
        raise SystemExit(1)
PY
  then
    echo "${label} is not reachable at ${host}:${port}."
    echo "Start the workstation services first with ./scripts/start-workstation.sh"
    exit 1
  fi
}

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to start LangGraph Studio."
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

export AGENT_ROUTING_CONFIG="${ROOT_DIR}/configs/model-routing.yaml"
export AGENT_MODELS_CONFIG="${ROOT_DIR}/configs/models.yaml"
export AGENT_WORKSPACE_ROOT="${ROOT_DIR}"
export OLLAMA_BASE_URL="$(rewrite_host "${OLLAMA_BASE_URL:-http://127.0.0.1:11434}")"
export QDRANT_URL="$(rewrite_host "${QDRANT_URL:-http://127.0.0.1:6333}")"
export REDIS_URL="$(rewrite_host "${REDIS_URL:-redis://127.0.0.1:6379/0}")"
if [[ -n "${POSTGRES_USER:-}" && -n "${POSTGRES_PASSWORD:-}" ]]; then
  export POSTGRES_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:5432/agents"
else
  export POSTGRES_URL="$(rewrite_host "${POSTGRES_URL:-postgresql://agentuser:change_me@127.0.0.1:5432/agents}")"
fi

require_tcp "Ollama" "127.0.0.1" "11434"
require_tcp "Qdrant" "127.0.0.1" "6333"
require_tcp "Postgres" "127.0.0.1" "5432"

python -m pip install --upgrade pip >/dev/null
python -m pip install -r "${ROOT_DIR}/agent_server/requirements.txt" "langgraph-cli[inmem]" >/dev/null

cd "${ROOT_DIR}"
echo "LangGraph API server starting on http://${HOST}:${PORT}"
echo "Config: ${ROOT_DIR}/langgraph.json"
echo "Use LangGraph Studio to connect to this local server."

exec langgraph dev --config "${ROOT_DIR}/langgraph.json" --host "${HOST}" --port "${PORT}"
