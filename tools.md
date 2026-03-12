# Local Agent Devstack Tools

This repo now assumes a workstation-hosted multi-service stack, with the laptop acting as the development client.

## Default stack

Install and use first:

- Docker Compose
  Primary deployment interface for the workstation stack.
- Tailscale
  Default secure access layer between laptop and workstation.
- Open WebUI
  Main operator interface for local and premium model comparison.
- vLLM
  Primary local OpenAI-compatible runtime.
- Ollama
  Secondary local runtime and convenient fallback.
- FastAPI-based Agent API
  Starter task API and future orchestration surface.

## Supporting services

- Qdrant
  Retrieval backend for later memory workflows.
- Redis
  Lightweight state and queue support for later expansion. It is currently intended for internal container-to-container use.
- Postgres
  Durable storage for later run tracking and richer metadata.

## Optional later tools

- OpenHands
- LangGraph
- Langfuse
- LiteLLM
- n8n

Add them only when the baseline stack is already useful and the need is concrete.
