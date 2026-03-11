#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

load_repo_env
print_ollama_settings

if command -v ollama >/dev/null 2>&1; then
  echo "Ollama already installed: $(command -v ollama)"
  exit 0
fi

echo "[INFO] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "[INFO] Ollama installed."
echo "[INFO] Verify with: ollama --version"
echo "[INFO] On Linux, ensure the service is running:"
echo "       systemctl status ollama || sudo systemctl status ollama"
