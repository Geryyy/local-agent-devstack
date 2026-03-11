# Workstation setup

This machine hosts the local models and is the Phase 1 implementation target.

## Assumptions

- Ubuntu-based workstation
- NVIDIA GPU available
- this machine is reachable from the laptop over direct Ethernet or VPN in Phase 2
- SSH server is installed and reachable

## Steps

1. install Ollama
2. optionally create `.env` from `.env.example`
3. pull local models
4. optionally warm the default coding model
5. verify with `./workstation/scripts/verify_workstation.sh`

## Scripts

- `scripts/install_ollama.sh`
- `scripts/pull_models.sh`
- `scripts/keep_models_warm.sh`
- `scripts/verify_workstation.sh`

## Default model policy

Phase 1 uses an 8B-first local model set so the workstation stays responsive on a 16 GB GPU:

- code: `qwen2.5-coder:7b`
- reasoning: `qwen2.5:7b`
- fallback: `granite-code:8b`

If you want to experiment with a larger open model later, enable the opt-in experimental pull in `.env`.

## Notes

Keep Ollama local to the workstation host. Do not put it into each devcontainer.
