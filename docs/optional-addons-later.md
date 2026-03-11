# Optional Add-ons for Later

This file tracks useful extensions that are intentionally out of the default setup.

Keep the active baseline simple:

- native Ollama on the workstation
- SSH tunnel from laptop to workstation
- local-first editing with Continue
- Codex only as explicit premium escalation

Add the items below only after the baseline is productive in daily use.

## Backend add-ons

- vLLM
  Add when you want higher-throughput inference, larger reasoning models, or better long-context serving.
- LiteLLM gateway
  Add when you want one stable OpenAI-compatible endpoint in front of Ollama, vLLM, and optional premium providers.
- TGI
  Add only if you develop a real need for Hugging Face-first large-model serving.

## Product workflow add-ons

- OpenWebUI
  Add when you want a local chat surface for prompt testing and model comparison.
- OpenHands
  Add when you want to experiment with a more autonomous coding agent.
- n8n
  Add only once you have repetitive multi-step automations worth formalizing.
- LangGraph
  Add when you start building your own stateful multi-agent systems.
- Flowise
  Add when a visual pipeline builder would help with prototyping.
- Langfuse
  Add when you need tracing, evals, and prompt observability for custom agents.

## Packaging strategy

Do not containerize the default Ollama baseline yet.

If and when optional services are added later:

- keep native Ollama as the simplest supported baseline
- consider Docker Compose for vLLM, LiteLLM, OpenWebUI, and n8n
- keep all services local-only on the workstation
- access them from the laptop through SSH tunnels, not public exposure
