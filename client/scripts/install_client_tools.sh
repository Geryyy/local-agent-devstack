#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] This script installs baseline client-side tools."
echo "[INFO] It does not install VS Code itself."
echo "[INFO] Phase 1 keeps premium escalation optional and OpenAI-focused."

if ! command -v curl >/dev/null 2>&1; then
  echo "[ERROR] curl is required."
  exit 1
fi

if ! command -v ssh >/dev/null 2>&1; then
  echo "[ERROR] OpenSSH client is required."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "[WARN] npm not found. Codex install will be skipped."
else
  echo "[INFO] Installing Codex CLI..."
  npm install -g @openai/codex
fi

echo "[INFO] Done."
echo "[INFO] Continue is typically installed as a VS Code extension."
