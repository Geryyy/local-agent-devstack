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
- starter planner-driven task decomposition

## Current boundary

This repo does not yet claim full autonomous orchestration. The shipped Agent API is intentionally a starter scaffold that makes the future architecture concrete without overstating what is already implemented.
