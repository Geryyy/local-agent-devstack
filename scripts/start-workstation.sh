#!/usr/bin/env bash
set -euo pipefail

match_env_var() {
  local pattern="$1"
  local file="$2"
  if command -v rg >/dev/null 2>&1; then
    rg -q "$pattern" "$file"
  else
    grep -Eq "$pattern" "$file"
  fi
}

if [[ ! -f ".env" ]]; then
  echo "No .env found. Copy .env.example to .env first."
  exit 1
fi

set -a
source .env
set +a

required_vars=(
  POSTGRES_USER
  POSTGRES_PASSWORD
  OLLAMA_BASE_URL
  OLLAMA_LOCAL_MODEL
  AGENT_ROUTING_CONFIG
  AGENT_MODELS_CONFIG
)

missing_vars=()
for var_name in "${required_vars[@]}"; do
  if ! match_env_var "^${var_name}=.+$" ".env"; then
    missing_vars+=("${var_name}")
  fi
done

if (( ${#missing_vars[@]} > 0 )); then
  echo "Your .env is missing required Compose variables:"
  printf '  - %s\n' "${missing_vars[@]}"
  echo
  echo "Refresh .env from .env.example and re-run this script."
  exit 1
fi

default_services=(
  ollama
  qdrant
  redis
  postgres
  open-webui
)

docker compose config >/dev/null
docker compose up -d "${default_services[@]}"
docker compose ps

echo
echo "Open WebUI: http://localhost:3000"
echo "LangGraph API: start separately with ./scripts/start-langgraph-studio.sh"
echo "Legacy API/UI: docker compose --profile legacy-api up -d agent-api"
echo "Ollama    : http://localhost:11434"
echo "Qdrant    : http://localhost:6333"
echo
echo "Default local model: ${OLLAMA_LOCAL_MODEL}"
if [[ -n "${OLLAMA_HEAVY_MODEL:-}" ]]; then
  echo "Optional heavy local model: ${OLLAMA_HEAVY_MODEL}"
fi
echo "Optional vLLM profile: docker compose --profile vllm up -d vllm"
