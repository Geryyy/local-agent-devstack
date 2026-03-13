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

This gives you a practical hybrid path:

- cloud for high-level coordination
- local for fast cheap implementation loops
- backend for actual task execution and persistence
