# Rollout plan

## Stage 1 - Workstation stack

- copy `.env.example` to `.env`
- set workstation-local credentials and passwords
- join Tailscale on the workstation
- if native Ollama is already installed on the workstation, keep using it as the default local model endpoint
- start the Docker stack with `./scripts/start-workstation.sh`

## Stage 2 - Client access

- join Tailscale on the laptop
- confirm the laptop can open Open WebUI and reach the Agent API
- use SSH tunneling only if direct Tailscale access is not desired

## Stage 3 - Starter agent workflows

- create tasks through the Agent API
- verify planner-driven initial decomposition
- verify phase progression through the task lifecycle endpoints

## Stage 4 - Project integration

- connect your editor, browser, and terminal workflow to workstation services
- use local models by default and premium escalation only when needed
- evaluate the stack on one real repo before expanding the workflow
- if `vLLM` image/runtime compatibility lags behind your driver, pin `VLLM_IMAGE` to a compatible official tag instead of using `latest`

## Stage 5 - Later expansion

- add durable run storage
- add richer retrieval and memory workflows
- add orchestration tracing
- add LangGraph or equivalent only when the starter flow is already useful
