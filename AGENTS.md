# AGENTS.md

## Project intent

This repository defines a **local-first AI agent development stack** for a split-machine setup:

- workstation: local inference host
- laptop: editor/devcontainer client with VPN-bound development workflows

The repo must stay practical, scriptable, and security-conscious.

## Design principles

1. Default to **local inference**.
2. Use **closed models only as optional escalation**.
3. Keep private code on local machines unless explicitly requested otherwise.
4. Prefer **SSH tunnels** over exposing local model services on the network.
5. Avoid magical automation for risky networking changes. Document them clearly instead.
6. Every script should be:
   - idempotent where practical
   - readable
   - safe by default
   - explicit about assumptions
7. Use environment variables and examples instead of hardcoded usernames, IPs, or tokens.
8. Keep workstation and client responsibilities clearly separated.
9. Prefer small, composable Bash scripts over giant monolithic setup scripts.
10. Provide useful comments and error messages.

## Technical scope

This repo should cover:

- workstation setup for Ollama and local models
- laptop/client setup for Continue, Codex, Claude Code, and SSH tunneling
- devcontainer integration
- example configs
- project-level templates for AI-friendly repo instructions
- rollout and validation docs

## Out of scope

- fully automatic network reconfiguration of host machines
- exposing Ollama publicly without authentication/tunneling
- deep infra like Kubernetes
- replacing the user's real project build system

## Coding standards

- Shell: `bash`, `set -euo pipefail`
- Markdown: concise, actionable, practical
- Configs: include comments where they help
- Do not silently install risky packages without saying why
- Do not assume the user wants cloud defaults

## Validation

When modifying this repo:

- keep paths consistent
- keep docs aligned with scripts
- prefer placeholders over fake secrets
- ensure commands shown in docs match actual files in the repo
