# Client notes

The preferred path is Tailscale, but SSH tunneling is fully usable when that is what you have.

## SSH-only laptop workflow

Keep the stack running on the workstation, then open tunnels from the laptop:

```bash
./scripts/start-client-tunnel.sh youruser workstation
```

That forwards these workstation services onto laptop-local ports:

- `3000` Open WebUI
- `2024` Agent API
- `8001` optional vLLM
- `11434` Ollama
- `6333` Qdrant

After that, use the framework from the laptop as if it were local:

- Open WebUI: `http://127.0.0.1:3000`
- Agent API: `http://127.0.0.1:2024`
- Agent Ops UI: `http://127.0.0.1:2024/ui`

Typical flow:

1. SSH to the workstation and start the stack with [scripts/start-workstation.sh](/home/geraldebmer/repos/local-agent-devstack/scripts/start-workstation.sh)
2. On the laptop, run [scripts/start-client-tunnel.sh](/home/geraldebmer/repos/local-agent-devstack/scripts/start-client-tunnel.sh)
3. Open WebUI or Agent Ops in the laptop browser
4. Create and monitor tasks through the Agent API on `127.0.0.1:2024`

## Client-hosted project mode

The workstation can now orchestrate a project that remains on the client machine.

Use the Agent Ops UI or `POST /tasks` with:

- `execution_target: "ssh"`
- `ssh_host`: the client Tailscale IP or hostname
- `ssh_user`: your client username
- `ssh_port`: usually `22`
- `project_path`: absolute path on the client

That makes the workstation the agent service provider while file edits and verification commands run against the client project over SSH.

Before using this mode, make sure the workstation can already log into the client non-interactively:

```bash
ssh youruser@client-tailscale-ip 'pwd'
```

If that fails with `Permission denied (publickey,password)`, add the workstation's public key to the client user's `~/.ssh/authorized_keys` first.

## Tailscale path

Use [scripts/start-tailscale-client.sh](/home/geraldebmer/repos/local-agent-devstack/scripts/start-tailscale-client.sh) if you want direct workstation access instead of SSH tunnels.
