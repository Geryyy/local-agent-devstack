#!/usr/bin/env bash
set -euo pipefail

if ! command -v tailscale >/dev/null 2>&1; then
  echo "tailscale is not installed"
  exit 1
fi

sudo tailscale up --ssh

echo "Tailscale status:"
tailscale status
echo
echo "Recommended: enable MagicDNS and give this machine a stable name such as 'workstation'."
