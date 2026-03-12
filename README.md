# local-agent-devstack

Local-first, multi-agent development stack for a workstation + client laptop setup.

This repo now targets a workstation-hosted Docker stack that serves local models, operator UI, retrieval, and a usable agent execution API. The laptop stays the coding surface and reaches the workstation primarily over Tailscale.

## Core idea

- Workstation runs:
  - Ollama
  - Open WebUI
  - Qdrant
  - Redis
  - Postgres
  - Agent API
  - optional `vllm` profile
- Workstation local model runtime:
  - containerized Ollama by default
  - optional `vllm` profile when the GPU/runtime combination is ready
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

The repo pins `VLLM_IMAGE` to `vllm/vllm-openai:v0.10.2`, but `vllm` is now opt-in behind the `vllm` Compose profile instead of part of the default workstation path.

5. On the laptop, join the same tailnet:

```bash
./scripts/start-tailscale-client.sh
```

6. Open the operator UI from the laptop:

```text
http://workstation:3000
```

## Agent API scope

This repo ships a runnable FastAPI backend for local-first planning and execution. It is useful today, but still intentionally lighter than a full production orchestration platform.

Implemented now:

- `GET /health`
- `GET /agents`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/advance`
- `POST /tasks/{task_id}/draft-plan`
- `GET /tasks/{task_id}/briefs`
- `POST /tasks/{task_id}/runs`
- `GET /tasks/{task_id}/runs`
- `GET /runs/{run_id}`
- `GET /runs/{run_id}/stream`
- `GET /tasks/{task_id}/memory`
- initial planner-based task decomposition
- YAML-backed routing policy loading
- project-aware local planning against repos mounted into the agent API container
- durable task and run storage in Postgres
- LangGraph-backed local execution loop for planner -> coder -> build
- Qdrant-backed project memory indexing and retrieval for planner/coder prompts
- writable workspace mounts so runs can edit repos and execute commands
- run modes for `patch_only` and `patch_and_run`
- basic server-sent event streaming for run state
- premium-capable model routing with OpenAI or Anthropic fallbacks when a task is marked premium-eligible and retries cross the local threshold
- internal Redis dependency without host port exposure

Documented for later, not implemented yet:

- stronger sandboxing and approval controls for repo execution
- richer run artifacts, dashboards, and tracing
- more polished premium approval UX and policy controls

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
curl http://localhost:2024/tasks/<task_id>/memory
curl http://localhost:2024/tasks/<task_id>/briefs
```

To run the automated local workflow:

```bash
curl -X POST http://localhost:2024/tasks/<task_id>/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "mode": "patch_and_run"
  }'
```

Supported run modes:

- `patch_only` writes files but skips verification commands
- `patch_and_run` writes files and executes the generated or overridden verification commands

To watch a run:

```bash
curl http://localhost:2024/runs/<run_id>/stream
```

## vLLM compatibility note

`vllm/vllm-openai:latest` can move to a newer CUDA runtime than your workstation driver supports. This repo now pins `VLLM_IMAGE` to `vllm/vllm-openai:v0.10.2` by default to avoid that drift.

If your workstation still needs something older or newer:

- set `VLLM_IMAGE` in `.env` to a compatible official image tag
- or update the NVIDIA driver and intentionally move forward

## Ollama note

This repo now uses containerized Ollama as the default local inference path.

To start the optional `vllm` profile as an additional backend:

```bash
docker compose --profile vllm up -d vllm
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
