# Agentic Development Stack

This document defines the repository's target operating model for local-first multi-agent development.

## Workstation

The workstation hosts the services that need GPU, storage, or long-running process uptime:

- Open WebUI
- Ollama
- vLLM
- Qdrant
- Redis
- Postgres
- Agent API

## Laptop

The laptop remains the main development surface:

- VS Code
- devcontainers
- browser
- terminal

It reaches workstation services primarily over Tailscale.

## Where to plan work

Use Open WebUI as the default operator console for:

- starting discussions
- comparing local and premium models
- reviewing outputs

Use the Agent API for:

- task creation
- task status inspection
- planner-driven task decomposition
- project-aware planning briefs
- durable automated runs that can edit and execute in a mounted repo

## Current boundary

This repo now supports a practical local-first execution loop, but it is still an early backend rather than a fully polished orchestration platform. It can persist tasks and runs, generate project-aware plans, index and retrieve project memory, edit files in mounted repos, and run verification commands. A basic stream endpoint exists, but richer dashboards, stronger approval controls, and deeper tracing are still future work.
