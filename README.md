# local-agent-devstack

Local-first, multi-agent development stack for a workstation + client laptop setup.

This repo now targets a workstation-hosted local-first stack with LangGraph Studio as the primary orchestration UI. The workstation serves models and execution services, while the laptop stays the coding surface and reaches the workstation primarily over Tailscale.

## Core idea

- Workstation runs:
  - Ollama
  - Open WebUI
  - Qdrant
  - Redis
  - Postgres
  - LangGraph API server
  - optional legacy Agent API routes
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
- LangGraph API: `http://workstation:2024`
- legacy Agent Ops UI: `http://workstation:2024/ui`
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

This now starts the Dockerized workstation services and the Dockerized LangGraph API on port `2024`.

To stop the Docker services later without removing containers:

```bash
./scripts/stop-workstation.sh
```

For a fuller teardown:

```bash
./scripts/stop-workstation.sh --down
```

The repo pins `VLLM_IMAGE` to `vllm/vllm-openai:v0.10.2`, but `vllm` is now opt-in behind the `vllm` Compose profile instead of part of the default workstation path.

5. On the laptop, join the same tailnet:

```bash
./scripts/start-tailscale-client.sh
```

6. Open the operator surfaces from the laptop:

```text
Open WebUI: http://workstation:3000
LangGraph API: http://workstation:2024
```

Then connect LangGraph Studio to the workstation API URL.

If you are using SSH only instead of Tailscale, keep the stack on the workstation and open local tunnels from the laptop:

```bash
./scripts/start-client-tunnel.sh youruser workstation
```

Then use these laptop-local URLs:

- Open WebUI: `http://127.0.0.1:3000`
- LangGraph API: `http://127.0.0.1:2024`
- legacy Agent Ops UI: `http://127.0.0.1:2024/ui`
- Ollama: `http://127.0.0.1:11434`

If you want the old standalone host-run Studio dev path, [scripts/start-langgraph-studio.sh](/home/geraldebmer/repos/local-agent-devstack/scripts/start-langgraph-studio.sh) remains available as a fallback, but it is no longer the default startup path.

## LangGraph Studio workflow

The primary orchestration path is now the official LangGraph development server plus LangGraph Studio.

Studio graph entrypoint:

- [agent_server/studio_graph.py](/home/geraldebmer/repos/local-agent-devstack/agent_server/studio_graph.py)

Studio config:

- [langgraph.json](/home/geraldebmer/repos/local-agent-devstack/langgraph.json)

The Studio graph accepts task-style input directly:

```json
{
  "title": "Build tiny-notes-cli",
  "description": "Create a tiny Python CLI notes app with tests and README.",
  "project_path": "playground/dummy-agent-app",
  "execution_target": "local",
  "constraints": ["stdlib only"],
  "acceptance_criteria": ["python3 -m unittest -v passes"],
  "premium_allowed": false,
  "run_mode": "patch_and_run"
}
```

That input bootstraps a task record, runs the planner, code agent, and build agent, and persists task/run state into Postgres just like the existing backend flow.

## Legacy API scope

This repo still ships the runnable FastAPI backend for local-first planning and execution. It remains useful for custom routes, health checks, the fallback dashboard, and backward compatibility.

Implemented now:

- `GET /health`
- `GET /agents`
- `GET /ui`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/advance`
- `POST /tasks/{task_id}/steer`
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
- project-aware planning and execution against SSH-reachable client projects
- durable task and run storage in Postgres
- LangGraph-backed local execution loop for planner -> coder -> build
- Qdrant-backed project memory indexing and retrieval for planner/coder prompts
- writable workspace mounts so runs can edit repos and execute commands
- built-in fallback dashboard for task creation, monitoring, and steering at `/ui`
- run modes for `patch_only` and `patch_and_run`
- basic server-sent event streaming for run state
- premium-capable model routing with OpenAI or Anthropic fallbacks when a task is marked premium-eligible and retries cross the local threshold
- internal Redis dependency without host port exposure

Documented for later, not implemented yet:

- stronger sandboxing and approval controls for repo execution
- richer run artifacts, dashboards, and tracing
- more polished premium approval UX and policy controls

## Dummy project workflow

You can use either LangGraph Studio as the primary orchestration UI or the built-in fallback dashboard at `http://localhost:2024/ui`.

For legacy API usage, create a task against either:

- a repo mounted under `/workspace` in the agent API container
- or a repo that stays on the client and is reachable from the workstation over SSH

```bash
curl -X POST http://localhost:2024/tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Add done command and tests",
    "description": "Extend the dummy todo CLI with a done command, file-backed tests, and slightly better help text.",
    "project_path": "playground/dummy-agent-app",
    "execution_target": "local",
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
curl -X POST http://localhost:2024/tasks/<task_id>/steer \
  -H 'Content-Type: application/json' \
  -d '{"note":"Prefer the smallest patch possible","premium_selected":false}'
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

## Client-hosted projects

If the workstation should act only as the service provider, create tasks with `execution_target: "ssh"` and point `project_path` at the client-side absolute path.

The workstation must be able to reach the client over key-based SSH first. A quick host-level smoke test is:

```bash
ssh youruser@client-tailscale-ip 'pwd'
```

If that does not work yet, the agent backend will not be able to edit or run against the client project either.

Example:

```bash
curl -X POST http://localhost:2024/tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Client repo task",
    "description": "Update a project that stays on the client laptop.",
    "execution_target": "ssh",
    "ssh_host": "100.123.157.61",
    "ssh_user": "gerald",
    "ssh_port": 22,
    "project_path": "/home/gerald/projects/tiny-notes-cli",
    "constraints": ["stdlib only"],
    "acceptance_criteria": ["tests pass"],
    "premium_allowed": false
  }'
```

Requirements for SSH-backed client projects:

- the workstation must be able to SSH to the client over Tailscale
- the client project path must be absolute on the client machine
- the client must have `python3` available for file summary/write/run helpers
- the workstation user or container must have SSH credentials that can access the client

## Notes on LangGraph Studio

LangGraph Studio is the preferred UI for:

- creating and re-running graph executions
- inspecting node-by-node state
- comparing local-only and premium-enabled runs
- steering task inputs without maintaining a separate custom frontend

The lightweight Agent Ops UI remains available as a practical fallback for repo-local task ops, but Studio is now the first-class orchestration surface.

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

For an optional heavier Ollama coder model on this workstation:

```bash
./scripts/pull-ollama-model.sh OLLAMA_MID_MODEL
./scripts/pull-ollama-model.sh OLLAMA_HEAVY_MODEL
ollama run deepcoder:14b "Reply with exactly: benchmark smoke ok"
ollama run qwen3-coder:30b "Reply with exactly: heavy coder ready"
```

`qwen3-coder:30b` works locally on the tested 16 GB RTX 5070 Ti, but it used about 15.6 GiB VRAM for a tiny prompt. Treat it as a manual or single-run heavy coder, not the default multi-agent model.

To compare local coder options on your workstation:

```bash
python3 ./scripts/benchmark-local-models.py
```

Current workstation takeaway:

- `qwen2.5-coder:7b` remains the safest default for multi-agent orchestration
- `deepcoder:14b` fits better than the 30B model, but needs extra prompt or template control before it is a reliable strict-JSON worker
- `qwen3-coder:30b` works as a manual heavy coder, but leaves very little VRAM headroom

## Open WebUI account setup

This stack keeps Open WebUI signup enabled by default so you can create accounts without extra bootstrap steps.

If you can reach the UI, you can create a local Open WebUI account at:

- `http://localhost:3000`
- or your workstation Tailscale URL

If you want stricter access later, change `ENABLE_SIGNUP` for `open-webui` in [docker-compose.yml](/home/geraldebmer/repos/local-agent-devstack/docker-compose.yml).

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
- [Local Model Benchmarks](/home/geraldebmer/repos/local-agent-devstack/docs/local-model-benchmarks.md)
- [Agent Roles](/home/geraldebmer/repos/local-agent-devstack/docs/agent-roles.md)
- [Security](/home/geraldebmer/repos/local-agent-devstack/docs/security.md)
