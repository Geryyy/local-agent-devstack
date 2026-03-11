# Architecture

## Machines

### Workstation
Responsibilities:

- runs Ollama
- stores local models
- provides GPU-backed local inference
- never becomes the primary coding environment

### Laptop
Responsibilities:

- runs VS Code
- hosts the ROS 2 devcontainer
- has access to required VPNs
- runs Codex / Continue client tooling
- forwards requests to workstation-hosted Ollama through an SSH tunnel

## Data path

Preferred path:

`devcontainer -> host.docker.internal -> laptop host localhost:11434 -> SSH tunnel -> workstation localhost:11434`

This keeps the model endpoint local from the perspective of the devcontainer, while the actual inference happens on the workstation.

## Why this design

- the workstation is stronger and should do inference
- the laptop is where your real workflows already happen
- SSH tunneling is simpler and safer than exposing ports over LAN/VPN
- host-level Ollama avoids duplicate model storage in containers
