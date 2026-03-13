# Roo Code Integration

Use Roo Code in VS Code as the orchestration surface while the workstation stack provides models, task execution, and persistence.

## Recommended split

- Cloud model for orchestration and architecture-heavy work in Roo
- Local Ollama models for lightweight coding, debugging, and build loops
- This repo's backend for task creation, run execution, and steering

## Connection model

1. Start the workstation stack:

```bash
./scripts/start-workstation.sh
```

2. On the client laptop, open the SSH tunnel to the workstation:

```bash
./scripts/start-client-tunnel.sh youruser cds-ebc.tailc07d54.ts.net
```

3. On the client laptop, start the MCP bridge:

```bash
./scripts/start-roo-mcp.sh
```

The MCP bridge talks to the backend through `http://127.0.0.1:2024`, which is the most reliable path for editor integrations.
The first run creates `.venv-roo-mcp` and installs the Python dependencies needed by the bridge.

## Intermediate goal

Treat Roo Code as the editor-native control plane:

- Roo orchestrates from VS Code
- cloud models do the hard planning and architecture work
- local Ollama models do the cheap coding and verification loops
- the workstation backend executes tasks, persists runs, and handles SSH-targeted projects

## Roo server command

Point Roo Code at this command:

```bash
python3 /home/geraldebmer/repos/local-agent-devstack/agent_server/roo_mcp_server.py
```

Or:

```bash
/home/geraldebmer/repos/local-agent-devstack/scripts/start-roo-mcp.sh
```

If needed, override the backend URL:

```bash
AGENT_API_BASE_URL=http://127.0.0.1:2024 /home/geraldebmer/repos/local-agent-devstack/scripts/start-roo-mcp.sh
```

## Available MCP tools

- `health_check`
- `list_agents`
- `create_task`
- `list_tasks`
- `get_task`
- `draft_plan`
- `get_memory`
- `get_briefs`
- `steer_task`
- `start_run`
- `list_task_runs`
- `get_run`
- `wait_for_run`

## Ready-to-use templates

- local task template: [playground/roo/local-feature-task.json](/home/geraldebmer/repos/local-agent-devstack/playground/roo/local-feature-task.json)
- client SSH task template: [playground/roo/client-ssh-task.json](/home/geraldebmer/repos/local-agent-devstack/playground/roo/client-ssh-task.json)
- orchestrator brief: [playground/roo/architect-brief.md](/home/geraldebmer/repos/local-agent-devstack/playground/roo/architect-brief.md)

## Recommended Roo workflow

1. Use a cloud model in Roo to turn a feature request into a compact task JSON payload.
2. Call `create_task`.
3. Optionally call `draft_plan`.
4. Call `start_run`.
5. Call `wait_for_run`.
6. Inspect `get_run` or `list_task_runs` for artifacts and touched files.

## Suggested mode split

- `Architect` or orchestration mode: cloud provider
- `Code` mode: local Ollama model
- `Debug` / `Build` mode: local Ollama model

Recommended practical split:

- `Architect`
  - cloud model
  - uses MCP tools to create tasks, inspect plans, and decide whether to allow premium escalation
- `Code`
  - local Ollama model
  - uses MCP mostly to fetch task context and inspect results
- `Debug` / `Build`
  - local Ollama model
  - uses MCP to start runs, inspect failures, and retry with steering

This gives you a practical hybrid path:

- cloud for high-level coordination
- local for fast cheap implementation loops
- backend for actual task execution and persistence

## Suggested first Roo workflow

1. In Roo `Architect`, paste [playground/roo/architect-brief.md](/home/geraldebmer/repos/local-agent-devstack/playground/roo/architect-brief.md) as the working instruction.
2. Ask it to prepare a task JSON payload for the current feature.
3. Call `create_task` with that JSON.
4. Call `draft_plan` if you want a project-aware plan before execution.
5. Call `start_run`.
6. Call `wait_for_run`.
7. If the run fails, call `get_run`, summarize the failure, then call `steer_task` and `start_run` again.

## Model recommendation

On your current GPU:

- Roo cloud orchestrator: OpenAI or Anthropic
- local code/debug/build models: `qwen2.5-coder:7b`
- optional heavier local coding runs: `qwen3-coder:30b`

That keeps orchestration strong while preserving local speed and stability for the cheap worker loops.
