#!/usr/bin/env bash
set -euo pipefail

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
  if ! rg -q "^${var_name}=.+$" ".env"; then
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

docker compose config >/dev/null
docker compose up -d
docker compose ps

echo
echo "Open WebUI: http://localhost:3000"
echo "Agent API : http://localhost:2024"
echo "Ollama    : http://localhost:11434"
echo "Qdrant    : http://localhost:6333"
echo
echo "Default local model: ${OLLAMA_LOCAL_MODEL}"
echo "Optional vLLM profile: docker compose --profile vllm up -d vllm"
