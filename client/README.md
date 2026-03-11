# Client setup

This machine is the laptop where you actually code.
It is part of Phase 2. Phase 1 ends once the workstation-hosted Ollama service is validated locally.

## Responsibilities

- VS Code
- devcontainers
- ROS 2 workspace
- Continue configuration
- Codex installation for optional premium escalation
- SSH tunnel to the workstation

## Flow

The laptop should treat the workstation's Ollama as if it were local by forwarding:

`localhost:11434 -> workstation:localhost:11434`

Then the devcontainer reaches the laptop host via `host.docker.internal`.
