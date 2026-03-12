# Rollout plan

## Stage 1 - Workstation stack

- copy `.env.example` to `.env`
- set workstation-local credentials and passwords
- join Tailscale on the workstation
- start the Docker stack with `./scripts/start-workstation.sh`
- pull the default local model with `./scripts/pull-ollama-model.sh`

## Stage 2 - Client access

- join Tailscale on the laptop
- confirm the laptop can open Open WebUI and reach the Agent API
- use SSH tunneling only if direct Tailscale access is not desired

## Stage 3 - Starter agent workflows

- create tasks through the Agent API
- verify planner-driven initial decomposition
- verify phase progression through the task lifecycle endpoints
- verify durable task and run storage
- verify automated runs can edit a repo and execute verification commands

## Stage 4 - Project integration

- connect your editor, browser, and terminal workflow to workstation services
- use local models by default and premium escalation only when needed
- evaluate the stack on one real repo before expanding the workflow
- if `vLLM` image/runtime compatibility lags behind your driver, pin `VLLM_IMAGE` to a compatible official tag instead of using `latest`

## Stage 5 - Later expansion

- add richer retrieval and memory workflows
- add orchestration tracing
- add streaming progress and richer operator dashboards
- add stronger execution sandboxing and approval controls
