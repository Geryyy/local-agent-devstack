# local-agent-devstack

Local-first, multi-agent development stack for a workstation + client laptop setup.

This repo now targets a workstation-hosted Docker stack that serves local models, operator UI, retrieval, and a starter agent API. The laptop stays the coding surface and reaches the workstation primarily over Tailscale.

## Core idea

- Workstation runs:
  - Open WebUI
  - vLLM
  - Qdrant
  - Redis
  - Postgres
  - Agent API
- Workstation local model runtime:
  - host-native Ollama by default
  - optional containerized Ollama when you explicitly enable it
- Laptop uses:
  - VS Code or devcontainer
  - browser
  - terminal
  - Tailscale to reach workstation services securely

Default access pattern:

`laptop -> Tailscale -> workstation services`

SSH tunneling remains available as a fallback, but it is no longer the primary architecture.

## Main URLs

After startup, the typical workstation endpoints are:

- Open WebUI: `http://workstation:3000`
- Agent API: `http://workstation:2024`
- vLLM: `http://workstation:8001/v1`
- Ollama: `http://workstation:11434`
- Qdrant: `http://workstation:6333`

Replace `workstation` with your Tailscale hostname or Tailscale IP if MagicDNS is not enabled.

## Quick start

1. Copy the environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and set:
   - `POSTGRES_PASSWORD`
   - `OPENAI_API_KEY` if you want OpenAI escalation
   - `ANTHROPIC_API_KEY` if you want Anthropic escalation
   - `HUGGING_FACE_HUB_TOKEN` if your vLLM model pull needs it
   - `WORKSTATION_HOSTNAME` to your real Tailscale host name

3. On the workstation, join Tailscale:

```bash
./scripts/start-tailscale-workstation.sh
```

4. Start the workstation stack:

```bash
./scripts/start-workstation.sh
```

The repo pins `VLLM_IMAGE` to `vllm/vllm-openai:v0.10.2` by default instead of `latest` so the stack does not unexpectedly jump to a newer CUDA requirement.

If your workstation already has native Ollama listening on `127.0.0.1:11434`, that is the default Ollama path for this repo. The Compose Ollama service is optional and is not started unless you explicitly enable its profile.

5. On the laptop, join the same tailnet:

```bash
./scripts/start-tailscale-client.sh
```

6. Open the operator UI from the laptop:

```text
http://workstation:3000
```

## Agent API starter scope

This repo ships a runnable FastAPI starter scaffold, not a full orchestration platform yet.

Implemented now:

- `GET /health`
- `GET /agents`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/advance`
- `POST /tasks/{task_id}/draft-plan`
- `GET /tasks/{task_id}/briefs`
- initial planner-based task decomposition
- YAML-backed routing policy loading
- project-aware local planning against repos mounted into the agent API container
- internal Redis dependency without host port exposure

Documented for later, not implemented yet:

- LangGraph orchestration
- durable run storage
- tool sandboxing
- live progress streaming

## Dummy project workflow

Create a task against a repo mounted under `/workspace` in the agent API container, then ask the planner for a local draft and fetch role briefs you can paste into WebUI or editor agents.

```bash
curl -X POST http://localhost:2024/tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Add done command and tests",
    "description": "Extend the dummy todo CLI with a done command, file-backed tests, and slightly better help text.",
    "project_path": "playground/dummy-agent-app",
    "constraints": ["stdlib only", "keep changes small"],
    "acceptance_criteria": [
      "done command marks an item complete",
      "tests cover add list done",
      "README mentions how to run the CLI"
    ],
    "premium_allowed": false
  }'
```

Then:

```bash
curl -X POST http://localhost:2024/tasks/<task_id>/draft-plan
curl http://localhost:2024/tasks/<task_id>/briefs
```

## vLLM compatibility note

`vllm/vllm-openai:latest` can move to a newer CUDA runtime than your workstation driver supports. This repo now pins `VLLM_IMAGE` to `vllm/vllm-openai:v0.10.2` by default to avoid that drift.

If your workstation still needs something older or newer:

- set `VLLM_IMAGE` in `.env` to a compatible official image tag
- or update the NVIDIA driver and intentionally move forward

## Ollama note

This repo now assumes a workstation-native Ollama when one is already present.

To use the optional containerized Ollama instead:

```bash
docker compose --profile ollama-container up -d ollama
```

and set:

```bash
OLLAMA_BASE_URL=http://ollama:11434
```

## Security notes

- Keep premium API keys on the workstation only.
- Do not expose workstation ports to the public internet.
- Tailscale is the default private access layer.
- SSH tunneling is an acceptable fallback when direct Tailscale access is not desirable.

## Repo layout

- `agent_server/` FastAPI starter scaffold
- `configs/` model catalog and routing policy
- `docs/` architecture, networking, security, routing, and rollout notes
- `scripts/` workstation startup and Tailscale helpers
- `docker-compose.yml` primary workstation deployment interface
- `client/` legacy SSH-tunnel compatibility notes
- `workstation/` legacy native-Ollama compatibility notes

## Key docs

- [Architecture](/home/geraldebmer/repos/local-agent-devstack/docs/architecture.md)
- [Networking](/home/geraldebmer/repos/local-agent-devstack/docs/networking.md)
- [Model Routing](/home/geraldebmer/repos/local-agent-devstack/docs/model-routing.md)
- [Agent Roles](/home/geraldebmer/repos/local-agent-devstack/docs/agent-roles.md)
- [Security](/home/geraldebmer/repos/local-agent-devstack/docs/security.md)
