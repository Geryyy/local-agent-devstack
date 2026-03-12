#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f ".env" ]]; then
  echo "No .env found. Copy .env.example to .env first."
  exit 1
fi

model_name="$(rg '^OLLAMA_LOCAL_MODEL=' .env | cut -d= -f2-)"

if [[ -z "${model_name}" ]]; then
  echo "OLLAMA_LOCAL_MODEL is not set in .env."
  exit 1
fi

echo "Pulling Ollama model: ${model_name}"
docker compose up -d ollama >/dev/null
docker exec ollama ollama pull "${model_name}"
docker exec ollama ollama list
