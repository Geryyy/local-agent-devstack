#!/usr/bin/env bash
set -euo pipefail

if [[ -d /ssh-src ]]; then
  mkdir -p /root/.ssh
  chmod 700 /root/.ssh
  find /ssh-src -maxdepth 1 -type f -exec cp {} /root/.ssh/ \;
  chmod 600 /root/.ssh/* 2>/dev/null || true
fi

exec "$@"
