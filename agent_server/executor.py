from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Dict, List

DEFAULT_ALLOWED_COMMAND_PREFIXES = (
    os.getenv("AGENT_ALLOWED_COMMAND_PREFIXES", "python,python3")
    .split(",")
)
BLOCKED_TOKENS = {
    "rm",
    "sudo",
    "su",
    "shutdown",
    "reboot",
    "mkfs",
    "dd",
    "mount",
    "umount",
}


def write_files(project_root: Path, file_writes: List[Dict[str, str]]) -> List[str]:
    touched: List[str] = []
    for item in file_writes:
        path = (project_root / item["path"]).resolve()
        if project_root.resolve() not in path.parents and path != project_root.resolve():
            raise ValueError(f"Refusing to write outside project root: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(item["content"], encoding="utf-8")
        touched.append(str(path.relative_to(project_root)))
    return touched


def _validate_command(command: str) -> List[str]:
    parts = shlex.split(command)
    if not parts:
        raise ValueError("Empty command is not allowed.")

    executable = parts[0]
    if executable not in DEFAULT_ALLOWED_COMMAND_PREFIXES:
        raise ValueError(f"Command prefix not allowed: {executable}")

    for token in parts:
        if token in BLOCKED_TOKENS:
            raise ValueError(f"Blocked token in command: {token}")

    return parts


def run_commands(project_root: Path, commands: List[str]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for command in commands:
        try:
            argv = _validate_command(command)
            completed = subprocess.run(
                argv,
                cwd=project_root,
                text=True,
                capture_output=True,
                timeout=120,
            )
        except Exception as exc:
            results.append(
                {
                    "command": command,
                    "returncode": 1,
                    "stdout": "",
                    "stderr": str(exc),
                    "success": False,
                }
            )
            continue
        results.append(
            {
                "command": command,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-12000:],
                "stderr": completed.stderr[-12000:],
                "success": completed.returncode == 0,
            }
        )
    return results
