# local-agent-devstack

Local-first, hybrid AI agent development environment for a split setup:

- **Workstation** = local inference server
- **Laptop** = coding machine with VS Code, devcontainers, ROS 2 workspaces, VPN access

This repo is designed around a workflow where the laptop does the coding and container work, while the workstation hosts the local models. The default path is:

`devcontainer -> laptop host -> SSH tunnel -> workstation Ollama`

Phase 1 focuses on the workstation only: get local inference reliable first, then wire the laptop and devcontainer path in Phase 2.
Closed models are optional fallbacks for the cases where local reasoning is not enough.

## Goals

- keep private code and documents local by default
- remove provider-side usage caps for most daily work
- keep latency low when laptop and workstation are near each other
- allow premium escalation to Codex / OpenAI only when needed
- make the setup reproducible across multiple repos

## Suggested topology

### Preferred path at the desk
Use a **direct Ethernet link** between laptop and workstation and keep the laptop's Wi-Fi/VPN unchanged for internet and remote access.

### Alternative path
Use a VPN between the laptop and workstation and run the exact same SSH tunnel flow.

## Recommended model policy

Primary local models on the workstation for a balanced 16 GB GPU setup:

- `qwen2.5-coder:7b` for code editing, refactors, repo understanding
- `qwen2.5:7b` for general reasoning, planning, architecture
- `granite-code:8b` as a secondary fallback

Optional larger-model experimentation:

- `gpt-oss:20b` only if you deliberately opt in and accept slower throughput or tighter memory pressure

Closed-model escalation on the laptop:

- **Codex / OpenAI** for hard implementation and premium reasoning when the local path is not enough

## Repo layout

- `workstation/` setup docs and scripts
- `client/` laptop setup docs and scripts
- `configs/` starter configs for Continue, Codex, devcontainer integration
- `templates/` drop-in files for your project repos
- `docs/` architecture, rollout, network, and security notes

## Quick start

### Phase 1: On the workstation
```bash
cp .env.example .env
cd workstation/scripts
./install_ollama.sh
./pull_models.sh
./verify_workstation.sh
```

If you do not need custom values yet, you can skip creating `.env`.

### Phase 2: On the laptop
```bash
cp .env.example .env
cd client/scripts
./install_client_tools.sh
./setup_ssh_tunnel.sh
./verify_client_path.sh
```

If the devcontainer needs to reach the laptop tunnel through `host.docker.internal` on Linux, set `LOCAL_OLLAMA_BIND_HOST` before opening the tunnel and then restart it.

### 3) In the devcontainer
Add the host mapping from `configs/devcontainer/devcontainer.example.json` and verify:

```bash
curl http://host.docker.internal:11434/api/tags
```

If you want to run the repo verification script from inside the devcontainer, use:

```bash
./client/scripts/verify_client_path.sh http://host.docker.internal:11434
```

## Important notes

- Do **not** expose Ollama directly on a public interface.
- Prefer SSH tunneling over direct port exposure.
- Run Ollama on the **workstation host**, not inside each devcontainer.
- Treat closed models as an explicit escalation path, not the default.
- Phase 1 is complete when the workstation can serve and verify local models without any laptop dependency.
