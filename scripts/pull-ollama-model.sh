#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f ".env" ]]; then
  echo "No .env found. Copy .env.example to .env first."
  exit 1
fi

env_var_name="${1:-OLLAMA_LOCAL_MODEL}"
model_name="$(rg "^${env_var_name}=" .env | cut -d= -f2-)"

if [[ -z "${model_name}" ]]; then
  echo "${env_var_name} is not set in .env."
  exit 1
fi

echo "Pulling Ollama model from ${env_var_name}: ${model_name}"
docker compose up -d ollama >/dev/null
docker exec ollama ollama pull "${model_name}"
docker exec ollama ollama list
