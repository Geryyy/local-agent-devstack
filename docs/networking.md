# Networking

## Default path: Tailscale direct access

This repo assumes the workstation and laptop may be on different networks. The default recommendation is Tailscale so the laptop can reach workstation services without exposing them publicly.

Benefits:

- no router changes
- encrypted access between devices
- stable hostnames with MagicDNS when enabled
- works across home, office, and travel networks

## Workstation setup

Install Tailscale and join the tailnet:

```bash
./scripts/start-tailscale-workstation.sh
```

Recommended:

- enable MagicDNS
- give the workstation a stable name such as `workstation`
- keep host firewall rules appropriate for your environment

## Laptop setup

Join the same tailnet:

```bash
./scripts/start-tailscale-client.sh
```

Then access the workstation by Tailscale hostname or Tailscale IP.

Typical URLs:

- `http://workstation:3000`
- `http://workstation:2024`
- `http://workstation:8001/v1`

## Fallback path: SSH tunnel

If you prefer not to access the services directly over Tailscale, open local tunnels instead:

```bash
./scripts/start-client-tunnel.sh youruser workstation
```

That forwards the main service ports to localhost on the laptop.

## Security rule

Do not expose these service ports to the public internet. Tailscale and SSH are the supported remote-access mechanisms for this repo.
