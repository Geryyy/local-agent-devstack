#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scripts/stop-workstation.sh
  ./scripts/stop-workstation.sh --down

Defaults to `docker compose stop` so containers stop without removing them.
Use `--down` for a fuller teardown while keeping named volumes intact.
EOF
}

mode="stop"

case "${1:-}" in
  "")
    ;;
  --down)
    mode="down"
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    echo "Unknown option: ${1}"
    echo
    usage
    exit 1
    ;;
esac

if [[ "${mode}" == "stop" ]]; then
  docker compose stop
else
  docker compose down
fi

docker compose ps
