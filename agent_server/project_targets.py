from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from workspace_context import DEFAULT_WORKSPACE_ROOT, summarize_project


TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".sh",
    ".js",
    ".ts",
}
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}
DEFAULT_ALLOWED_COMMAND_PREFIXES = (
    os.getenv("AGENT_ALLOWED_COMMAND_PREFIXES", "python,python3").split(",")
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


def resolve_target(metadata: Dict[str, Any]) -> Dict[str, Any]:
    execution_target = metadata.get("execution_target", "local")
    project_path = metadata.get("project_path")
    if execution_target == "ssh":
        ssh_host = metadata.get("ssh_host")
        ssh_user = metadata.get("ssh_user")
        ssh_port = int(metadata.get("ssh_port", 22))
        if not ssh_host or not ssh_user or not project_path:
            raise ValueError("SSH projects require ssh_host, ssh_user, and project_path.")
        if not str(project_path).startswith("/"):
            raise ValueError("SSH project_path must be absolute on the client machine.")
        return {
            "kind": "ssh",
            "project_root": str(project_path),
            "project_key": f"ssh://{ssh_user}@{ssh_host}:{ssh_port}{project_path}",
            "ssh_host": ssh_host,
            "ssh_user": ssh_user,
            "ssh_port": ssh_port,
        }

    if not project_path:
        raise ValueError("Task has no project_path")

    candidate = Path(project_path)
    if not candidate.is_absolute():
        candidate = DEFAULT_WORKSPACE_ROOT / candidate

    resolved = candidate.resolve()
    workspace_root = DEFAULT_WORKSPACE_ROOT.resolve()
    if workspace_root not in resolved.parents and resolved != workspace_root:
        raise ValueError(f"Project path must stay under {workspace_root}")
    if not resolved.exists():
        raise ValueError(f"Project path does not exist: {resolved}")

    return {
        "kind": "local",
        "project_root": resolved,
        "project_key": str(resolved),
    }


def _ssh_base(target: Dict[str, Any]) -> List[str]:
    return [
        "ssh",
        "-p",
        str(target["ssh_port"]),
        "-o",
        "UserKnownHostsFile=/root/.ssh/known_hosts",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{target['ssh_user']}@{target['ssh_host']}",
    ]


def _run_remote_python(target: Dict[str, Any], code: str, payload: Dict[str, Any] | None = None, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*_ssh_base(target), "python3", "-c", code],
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def summarize_target(target: Dict[str, Any]) -> Dict[str, object]:
    if target["kind"] == "local":
        summary = summarize_project(target["project_root"])
        summary["project_key"] = target["project_key"]
        summary["execution_target"] = "local"
        return summary

    code = """
import json, os
from pathlib import Path

TEXT_EXTENSIONS = {'.md','.txt','.py','.toml','.yaml','.yml','.json','.sh','.js','.ts'}
IGNORED_DIRS = {'.git','.venv','venv','node_modules','__pycache__','.mypy_cache','.pytest_cache'}
project_root = Path(%r)
files = []
for root, dirs, filenames in os.walk(project_root):
    dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
    for filename in sorted(filenames):
        path = Path(root) / filename
        if path.suffix in TEXT_EXTENSIONS or path.name in {'README','Makefile','AGENTS.md'}:
            files.append(path)
        if len(files) >= 40:
            break
    if len(files) >= 40:
        break
relative_files = [str(path.relative_to(project_root)) for path in files]
snippets = []
for path in files[:8]:
    rel = path.relative_to(project_root)
    try:
        content = path.read_text(encoding='utf-8')[:1200].strip()
    except UnicodeDecodeError:
        continue
    if content:
        snippets.append(f"## {rel}\\n{content}")
print(json.dumps({
    'project_root': str(project_root),
    'file_count': len(relative_files),
    'files': relative_files,
    'snippets': snippets,
}))
""" % (target["project_root"],)
    completed = _run_remote_python(target, code, timeout=120)
    if completed.returncode != 0:
        raise ValueError(f"Failed to summarize remote project: {completed.stderr.strip()}")
    summary = json.loads(completed.stdout)
    summary["project_key"] = target["project_key"]
    summary["execution_target"] = "ssh"
    return summary


def write_files_to_target(target: Dict[str, Any], file_writes: List[Dict[str, str]]) -> List[str]:
    if target["kind"] == "local":
        project_root = Path(target["project_root"])
        touched: List[str] = []
        for item in file_writes:
            path = (project_root / item["path"]).resolve()
            if project_root.resolve() not in path.parents and path != project_root.resolve():
                raise ValueError(f"Refusing to write outside project root: {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(item["content"], encoding="utf-8")
            touched.append(str(path.relative_to(project_root)))
        return touched

    payload = {
        "project_root": target["project_root"],
        "file_writes": file_writes,
    }
    code = """
import json, sys
from pathlib import Path

payload = json.load(sys.stdin)
project_root = Path(payload['project_root']).resolve()
touched = []
for item in payload['file_writes']:
    path = (project_root / item['path']).resolve()
    if project_root not in path.parents and path != project_root:
        raise ValueError(f"Refusing to write outside project root: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(item['content'], encoding='utf-8')
    touched.append(str(path.relative_to(project_root)))
print(json.dumps(touched))
"""
    completed = _run_remote_python(target, code, payload=payload, timeout=180)
    if completed.returncode != 0:
        raise ValueError(f"Failed to write remote files: {completed.stderr.strip()}")
    return json.loads(completed.stdout)


def run_commands_on_target(target: Dict[str, Any], commands: List[str]) -> List[Dict[str, object]]:
    validated_commands = []
    results: List[Dict[str, object]] = []
    for command in commands:
        try:
            _validate_command(command)
            validated_commands.append(command)
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

    if not validated_commands:
        return results

    if target["kind"] == "local":
        project_root = Path(target["project_root"])
        for command in validated_commands:
            argv = shlex.split(command)
            try:
                completed = subprocess.run(
                    argv,
                    cwd=project_root,
                    text=True,
                    capture_output=True,
                    timeout=120,
                )
                results.append(
                    {
                        "command": command,
                        "returncode": completed.returncode,
                        "stdout": completed.stdout[-12000:],
                        "stderr": completed.stderr[-12000:],
                        "success": completed.returncode == 0,
                    }
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
        return results

    payload = {
        "project_root": target["project_root"],
        "commands": validated_commands,
    }
    code = """
import json, shlex, subprocess, sys

payload = json.load(sys.stdin)
results = []
for command in payload['commands']:
    try:
        completed = subprocess.run(
            shlex.split(command),
            cwd=payload['project_root'],
            text=True,
            capture_output=True,
            timeout=120,
        )
        results.append({
            'command': command,
            'returncode': completed.returncode,
            'stdout': completed.stdout[-12000:],
            'stderr': completed.stderr[-12000:],
            'success': completed.returncode == 0,
        })
    except Exception as exc:
        results.append({
            'command': command,
            'returncode': 1,
            'stdout': '',
            'stderr': str(exc),
            'success': False,
        })
print(json.dumps(results))
"""
    completed = _run_remote_python(target, code, payload=payload, timeout=240)
    if completed.returncode != 0:
        results.append(
            {
                "command": "remote_batch",
                "returncode": 1,
                "stdout": "",
                "stderr": completed.stderr.strip(),
                "success": False,
            }
        )
        return results
    return results + json.loads(completed.stdout)
