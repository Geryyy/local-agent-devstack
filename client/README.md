# Client notes

The laptop is now expected to reach the workstation stack directly over Tailscale.

Use:

- [scripts/start-tailscale-client.sh](/home/geraldebmer/repos/local-agent-devstack/scripts/start-tailscale-client.sh) to join the tailnet
- [scripts/start-client-tunnel.sh](/home/geraldebmer/repos/local-agent-devstack/scripts/start-client-tunnel.sh) only if you want an SSH fallback

The old client-side tunnel bootstrap scripts were removed as part of the Tailscale-first migration.
