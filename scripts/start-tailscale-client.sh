#!/usr/bin/env bash
set -euo pipefail

if ! command -v tailscale >/dev/null 2>&1; then
  echo "tailscale is not installed"
  exit 1
fi

sudo tailscale up
tailscale status
