# Security

## Default posture

- local-first
- workstation-hosted services
- premium credentials stored on the workstation only
- Tailscale-first private access
- no public exposure of service ports

## Practical recommendations

- use Tailscale as the normal access layer between laptop and workstation
- keep SSH available as an administrative and fallback access path
- do not publish Open WebUI, Agent API, Ollama, or vLLM to the public internet
- use placeholders in docs and examples instead of real hostnames, users, or tokens
- keep `.env` out of git

## Data handling

Private code and documents should stay on local machines by default.

Closed-model access is optional escalation. When you use premium APIs:

- do it intentionally
- keep keys only on the workstation
- use routing policy to limit when escalation is allowed
- preserve task metadata that shows whether premium escalation was selected
