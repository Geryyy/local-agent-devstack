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

Primary local models on the workstation for a stronger agent-friendly default:

- `gpt-oss:20b` for agent-style coding, repo understanding, and general reasoning
- `qwen2.5-coder:7b` as a smaller fallback when you want lower latency
- use separate Continue roles if you later want to split code and reasoning back out

Optional larger-model experimentation:

- `qwen3-coder:30b` only if you deliberately opt in and accept higher VRAM use

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

### 3) Continue config choice
If Continue runs on the laptop host, use `configs/continue/config.yaml`, which assumes the SSH tunnel is reachable on localhost and points at:

```bash
http://127.0.0.1:11434
```

That file matches the default host-only tunnel bind:

```bash
LOCAL_OLLAMA_BIND_HOST=127.0.0.1
```

It also usually works if the tunnel is opened on all interfaces:

```bash
LOCAL_OLLAMA_BIND_HOST=0.0.0.0
```

If you bind the tunnel to a specific Linux bridge address such as `172.17.0.1`, update the live Continue config to use that address instead of `127.0.0.1`.

If Continue runs inside a devcontainer, use `configs/continue/devcontainer.config.yaml`.

### 4) In the devcontainer
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
