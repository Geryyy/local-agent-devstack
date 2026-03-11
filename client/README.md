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
On Linux bridge-network devcontainers, that only works if the SSH tunnel is not bound to host loopback only.

## Phase 2 steps

1. copy `.env.example` to `.env` in this repo and set `WORKSTATION_USER` and `WORKSTATION_HOST`
2. install baseline client tools:
   `./client/scripts/install_client_tools.sh`
3. open the SSH tunnel:
   `./client/scripts/setup_ssh_tunnel.sh`
4. verify the laptop-local path:
   `./client/scripts/verify_client_path.sh`
5. add the `host.docker.internal` mapping from `configs/devcontainer/devcontainer.example.json`

If you run the verification script from inside the devcontainer, pass the laptop-host endpoint explicitly:

- `./client/scripts/verify_client_path.sh http://host.docker.internal:11434`

Using `LOCAL_OLLAMA_BIND_HOST=host.docker.internal` also works for that check, but it repurposes the tunnel bind variable and is not the intended setup knob.

## Devcontainer note for Linux

The default tunnel bind address is `127.0.0.1`, which is the safer host-only setting.
That is enough for laptop-local tools, but a bridge-network devcontainer usually cannot reach it through `host.docker.internal`.

If the devcontainer must call the tunnel directly, set `LOCAL_OLLAMA_BIND_HOST` before opening the tunnel:

- preferred when you know the Docker bridge IP:
  `LOCAL_OLLAMA_BIND_HOST=172.17.0.1`
- broader exposure, simpler setup:
  `LOCAL_OLLAMA_BIND_HOST=0.0.0.0`

Then restart the tunnel and rerun `./client/scripts/verify_client_path.sh`.

## Optional systemd tunnel

If you want the tunnel to persist across logins:

1. create `~/.config/local-agent-devstack/client.env`
2. add:
   `WORKSTATION_USER=youruser`
   `WORKSTATION_HOST=workstation.local`
   `LOCAL_OLLAMA_PORT=11434`
   `LOCAL_OLLAMA_BIND_HOST=127.0.0.1`
   `OLLAMA_PORT=11434`
3. install the unit from `client/systemd/ollama-tunnel.service`
4. enable it with:
   `systemctl --user enable --now ollama-tunnel.service`
