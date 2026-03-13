# Architecture

This repo defines a local-first multi-agent development stack built around a GPU workstation and a client laptop.

## Machine roles

### Workstation

Runs the full AI stack:

- Ollama
- Open WebUI
- Qdrant
- Redis
- Postgres
- Agent API
- optional `vllm` profile

Responsibilities:

- host local inference and supporting services
- keep premium credentials local to the workstation
- provide the operator UI and API endpoints
- remain the main runtime for future orchestration

### Laptop

Used for:

- VS Code and devcontainers
- browser access to Open WebUI
- terminal access to the Agent API
- day-to-day coding against workstation-hosted services

Responsibilities:

- stay the primary coding machine
- reach workstation services over Tailscale by default
- use SSH tunnels only as a compatibility fallback

## Service layout

Typical workstation ports:

- Open WebUI on `3000`
- Agent API on `2024`
- Agent Ops UI on `2024/ui`
- vLLM on `8001`
- Ollama on `11434`
- Qdrant on `6333`
- Postgres on `5432`

Redis is part of the internal stack and does not need a host-published port for the current starter stage.

## Operator flow

The intended flow is:

`laptop browser or editor -> Tailscale -> workstation services`

Open WebUI is the primary human-facing interface. The Agent API is the starter execution surface for structured task handling and future orchestration work.

The Agent API now also serves a lightweight operator dashboard for task creation, run control, and live monitoring.

## Current implementation level

Implemented now:

- Docker Compose workstation stack
- Tailscale-first networking guidance
- YAML-backed model routing config
- FastAPI agent service with durable task and run state in Postgres
- LangGraph-backed local execution loop for planner, coder, and build steps
- writable workspace mounts so the backend can edit and execute in target repos
- SSH-backed client project execution so the workstation can orchestrate while the project remains on the client
- built-in operator dashboard at `/ui`
- Open WebUI can start without a live vLLM container, which helps on workstations where vLLM image/runtime compatibility is still being tuned
- containerized Ollama is the default local inference path
- vLLM is intentionally pinned to a specific image tag in `.env`, but stays opt-in behind a Compose profile

Planned later:

- orchestration tracing and richer operator dashboards
- stronger execution sandboxing and approval controls
- more polished premium approval and escalation policy controls
