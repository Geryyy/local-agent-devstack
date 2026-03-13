# Rollout plan

## Stage 1 - Workstation stack

- copy `.env.example` to `.env`
- set workstation-local credentials and passwords
- join Tailscale on the workstation
- start the Docker service stack with `./scripts/start-workstation.sh`
- pull the default local model with `./scripts/pull-ollama-model.sh`
- start the LangGraph API server with `./scripts/start-langgraph-studio.sh`

## Stage 2 - Client access

- join Tailscale on the laptop
- confirm the laptop can open Open WebUI and reach the LangGraph API
- connect LangGraph Studio to the workstation API URL
- confirm the fallback Agent Ops UI at `/ui` still works when needed
- use SSH tunneling only if direct Tailscale access is not desired

## Stage 3 - Starter agent workflows

- create tasks through the Agent API
- create and run tasks through LangGraph Studio
- verify planner-driven initial decomposition
- verify phase progression through the task lifecycle endpoints
- verify durable task and run storage
- verify project memory indexing and retrieval through Qdrant
- verify automated runs can edit a repo and execute verification commands
- verify run streaming with `/runs/{run_id}/stream`

## Stage 4 - Project integration

- connect your editor, browser, and terminal workflow to workstation services
- verify the workstation can orchestrate a client-hosted repo over SSH
- use local models by default and premium escalation only when needed
- evaluate the stack on one real repo before expanding the workflow
- if `vLLM` image/runtime compatibility lags behind your driver, pin `VLLM_IMAGE` to a compatible official tag instead of using `latest`

## Stage 5 - Later expansion

- add orchestration tracing
- add richer operator dashboards and run artifacts
- add stronger execution sandboxing and approval controls
- add more polished premium approval and escalation policy controls
