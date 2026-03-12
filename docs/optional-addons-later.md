# Optional Add-ons For Later

Keep the active baseline focused:

- Docker Compose workstation stack
- Tailscale access
- Open WebUI as operator UI
- vLLM and Ollama as local model backends
- Agent API starter scaffold

Add the items below only when the baseline is working well in daily use.

## Orchestration and observability

- LangGraph
  Add when you want stateful orchestration beyond the starter planner flow.
- Langfuse
  Add when you need tracing, evals, and prompt observability.
- Prometheus and Grafana
  Add when service-level monitoring becomes worth the overhead.

## Agent and workflow tools

- OpenHands
  Add when you want to experiment with a more execution-heavy coding agent.
- LiteLLM
  Add when one unified gateway in front of local and premium providers becomes useful.
- n8n
  Add only when you have repeatable multi-step automation worth formalizing.

## Local model expansion

- Add a role-specific local model split only after the Ollama-first baseline is stable in daily use.
- Candidate split to test later:
  - coder agent: `Qwen3-Coder-30B-A3B-Instruct` if it fits reliably in the chosen runtime
  - cheap helper/build agent: `DeepCoder-14B`
  - planner-lite/docs agent: `Qwen3`
  - premium escalation: `gpt-5.4` or Claude Sonnet/Opus when the planner decides
- Validate larger local models on the real workstation before promoting them to defaults.

## Packaging notes

- keep the supported baseline readable and scriptable
- add new services only when they solve a real workflow problem
- prefer explicit documentation over risky automatic network changes
