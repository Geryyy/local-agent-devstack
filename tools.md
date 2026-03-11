# Local Agent Devstack Tools

This file tracks the tools that are most likely to improve productivity in this stack.

The default posture stays the same:

- local-first by default
- workstation-hosted inference
- SSH-tunneled access from the laptop
- premium APIs only as an explicit escalation path

## Backend layer

These are the model-serving tools worth considering on the workstation.

### Install now

- Ollama
  The default backend for this repo. It is the easiest way to get local models running, works well for coding agents, and is already integrated into the current setup.

### Install next

- vLLM
  Promising next backend once you want better throughput, larger contexts, or a cleaner OpenAI-compatible serving path for bigger reasoning models.
- LiteLLM gateway
  A strong next step if you want agents to call one stable API while routing requests across Ollama, vLLM, and optional premium providers.

### Install only when you have a clear need

- TGI
  Worth considering only if you end up needing a Hugging Face-first production serving path or more advanced large-model deployment behavior.

## Backend roles

- Ollama
  Best for easy local model management, coding agents, experimentation, and interactive use.
- vLLM
  Best for higher-throughput inference, larger reasoning models, long context windows, and heavier multi-agent workloads.
- LiteLLM
  Best as the gateway layer once you want unified routing, fallback, and provider abstraction.
- TGI
  Best reserved for heavier production-style inference needs.

## Suggested backend architecture

Short term:

- laptop tools -> SSH tunnel -> workstation Ollama

Next step:

- laptop tools -> SSH tunnel -> workstation LiteLLM
- LiteLLM routes coding traffic to Ollama
- LiteLLM routes heavier reasoning traffic to vLLM
- OpenAI remains an explicit fallback, not the default

Recommended local ports on the workstation:

- `11434` for Ollama
- `8000` for vLLM
- `4000` for LiteLLM
- `3000` for OpenWebUI
- `5678` for n8n

All of these should stay bound locally on the workstation and be reached through SSH tunnels when needed.

## Developer tools

These are the user-facing tools that improve daily coding flow.

### Install now

- Continue
  Best local-first editor companion for day-to-day coding with workstation-hosted models.
- Codex
  Keep as the premium escalation path when local reasoning is not enough.
- Aider
  Useful when you want a tight git-oriented terminal editing loop.
- A small set of MCP servers
  Add only the ones you use often, such as docs, filesystem-safe helpers, and repo context tools.
- OpenWebUI
  Good local chat surface for testing prompts, comparing models, and debugging outputs across Ollama or future LiteLLM and vLLM backends.

### Install next

- OpenHands
  Worth trying once the local and Codex workflows are stable and you want a more autonomous software agent.
- `lazygit`
  Optional, but nice if you want faster staging and review without living in raw git commands.
- `uv`
  Great for Python-heavy repos because it makes environment and tool installs much smoother.

### Install only when you have real automation pain

- n8n
  Useful when you need repeatable multi-step automations across services, not as a default coding tool.

### Install only when you are building your own agent systems

- LangGraph
  Good when you start building stateful multi-step agents instead of only using coding assistants.
- Flowise
  Useful for visual prototyping, but less important than LangGraph for serious agent logic.
- Langfuse
  Best when you need traces, evals, and prompt observability for your own agents.

## Terminal utilities that compound productivity

- `rg`
  Fast code and text search.
- `fd`
  Faster, cleaner file discovery than `find` for most daily use.
- `bat`
  Better file preview in the terminal with syntax highlighting.
- `jq`
  Essential for inspecting JSON from APIs like Ollama, LiteLLM, and OpenAI.
- `tmux`
  Very helpful for long-running agent, server, and benchmark sessions.
- `direnv`
  Good for repo-local environment management.
- `gh`
  Smooth GitHub workflow from the terminal.

## Recommended order

1. Keep Ollama as the working baseline.
2. Add Continue, Codex, Aider, and a few MCP servers.
3. Add OpenWebUI as the easiest local comparison and debugging surface.
4. Add vLLM when you want stronger performance or larger-model serving.
5. Add LiteLLM when you want one stable API in front of multiple backends.
6. Reach for n8n, LangGraph, Flowise, or Langfuse only once there is real workflow or agent-build pressure.
