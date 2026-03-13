#!/usr/bin/env bash
set -euo pipefail

read_env_var() {
  local name="$1"
  local file="$2"
  if command -v rg >/dev/null 2>&1; then
    rg "^${name}=" "$file" | cut -d= -f2-
  else
    grep -E "^${name}=" "$file" | cut -d= -f2-
  fi
}

if [[ ! -f ".env" ]]; then
  echo "No .env found. Copy .env.example to .env first."
  exit 1
fi

env_var_name="${1:-OLLAMA_LOCAL_MODEL}"
model_name="$(read_env_var "${env_var_name}" ".env")"

if [[ -z "${model_name}" ]]; then
  echo "${env_var_name} is not set in .env."
  exit 1
fi

echo "Pulling Ollama model from ${env_var_name}: ${model_name}"
docker compose up -d ollama >/dev/null
docker exec ollama ollama pull "${model_name}"
docker exec ollama ollama list
