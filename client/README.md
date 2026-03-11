# Client setup

This machine is the laptop where you actually code.
It is part of Phase 2. Phase 1 ends once the workstation-hosted Ollama service is validated locally.

## Responsibilities

- VS Code
- devcontainers
- ROS 2 workspace
- Continue configuration
- Codex installation for optional premium escalation
- SSH tunnel to the workstation

## Flow

The laptop should treat the workstation's Ollama as if it were local by forwarding:

`localhost:11434 -> workstation:localhost:11434`

Then the devcontainer reaches the laptop host via `host.docker.internal`.

## Phase 2 steps

1. copy `.env.example` to `.env` in this repo and set `WORKSTATION_USER` and `WORKSTATION_HOST`
2. install baseline client tools:
   `./client/scripts/install_client_tools.sh`
3. open the SSH tunnel:
   `./client/scripts/setup_ssh_tunnel.sh`
4. verify the laptop-local path:
   `./client/scripts/verify_client_path.sh`
5. add the `host.docker.internal` mapping from `configs/devcontainer/devcontainer.example.json`

## Optional systemd tunnel

If you want the tunnel to persist across logins:

1. create `~/.config/local-agent-devstack/client.env`
2. add:
   `WORKSTATION_USER=youruser`
   `WORKSTATION_HOST=workstation.local`
   `LOCAL_OLLAMA_PORT=11434`
   `OLLAMA_PORT=11434`
3. install the unit from `client/systemd/ollama-tunnel.service`
4. enable it with:
   `systemctl --user enable --now ollama-tunnel.service`
