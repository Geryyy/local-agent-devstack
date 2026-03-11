# Rollout plan

## Stage 1 - Base local inference
- install Ollama on workstation
- load workstation settings from `.env` when needed
- pull core 8B-first models
- verify local API and generation path on workstation

## Stage 2 - Client connectivity
- verify SSH from laptop to workstation
- establish local port forward
- verify laptop can reach workstation Ollama through localhost

## Stage 3 - Devcontainer integration
- add `host.docker.internal` mapping
- verify container access to `http://host.docker.internal:11434`

## Stage 4 - Agent tools
- configure Continue as default local-first client
- install Codex as the optional premium fallback

## Stage 5 - Project templates
- add `docs/ai/ARCHITECTURE.md`
- add `docs/ai/COMMON_TASKS.md`
- add `scripts/ai/verify.sh`
- add `AGENTS.md` to each serious repo

## Stage 6 - Validation
- run prompt benchmarks on one real robotics repo
- compare local-only vs premium fallback behavior

## Optional later stage - Add-ons
- consider `vLLM` once Ollama-only workflow is productive
- consider LiteLLM when one unified API would simplify client routing
- consider OpenWebUI for local prompt testing and model comparison
- consider automation and observability tools only after a real workflow need appears
- keep details in `docs/optional-addons-later.md`
