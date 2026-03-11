# Workflow tools

## Install now

### Core agent tools

- Continue
  Best local-first editor companion for day-to-day coding with Ollama-backed models.
- Codex
  Keep as the premium escalation path when local reasoning is not enough.
- Aider
  Useful when you want tight git-oriented edit loops from the terminal.
- A small set of MCP servers
  Add only the servers you actually use often, such as docs, filesystem-safe helpers, and repo context tools.

### Terminal utilities that compound productivity

- `rg`
  Fast code and text search. This is the default search tool worth building muscle memory around.
- `fd`
  Faster, cleaner file discovery than `find` for most daily use.
- `bat`
  Better file preview in the terminal with syntax highlighting.
- `jq`
  Essential for inspecting JSON from APIs like Ollama and OpenAI.
- `tmux`
  Very helpful for keeping long-running agent, server, and benchmark sessions alive.
- `direnv`
  Good for repo-local environment management without constantly sourcing files manually.
- `gh`
  Smooth GitHub workflow from the terminal for PRs, issues, and release notes.

## Install next

- OpenHands
  Worth trying once the local and Codex workflows are stable and you want a more autonomous software agent.
- `lazygit`
  Optional, but nice if you want faster staging and review without living in raw git commands.
- `uv`
  Great for Python-heavy repos because it makes virtualenv and tool installs much less annoying.

## Install only when you have real automation pain

- n8n
  Useful when you need repeatable multi-step automations across services, not as a default dev tool.

## Install only when you are building and debugging agent systems

- Langfuse
  Best when you need traces, evals, or prompt observability for your own agents rather than just better coding ergonomics.

## Recommended order

1. Stabilize local inference with Continue and Codex.
2. Add Aider if you want a stronger terminal editing loop.
3. Add only the MCP servers you use weekly.
4. Reach for OpenHands, n8n, or Langfuse once you hit a clear workflow bottleneck.
