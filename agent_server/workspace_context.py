from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List


DEFAULT_WORKSPACE_ROOT = Path(os.getenv("AGENT_WORKSPACE_ROOT", "/workspace"))
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
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}


def resolve_project_path(project_path: str | None) -> Path | None:
    if not project_path:
        return None

    candidate = Path(project_path)
    if not candidate.is_absolute():
        candidate = DEFAULT_WORKSPACE_ROOT / candidate

    resolved = candidate.resolve()
    workspace_root = DEFAULT_WORKSPACE_ROOT.resolve()

    if workspace_root not in resolved.parents and resolved != workspace_root:
        raise ValueError(f"Project path must stay under {workspace_root}")

    if not resolved.exists():
        raise ValueError(f"Project path does not exist: {resolved}")

    return resolved


def _collect_files(project_root: Path, limit: int = 40) -> List[Path]:
    files: List[Path] = []
    for root, dirs, filenames in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for filename in sorted(filenames):
            path = Path(root) / filename
            if path.suffix in TEXT_EXTENSIONS or path.name in {"README", "Makefile", "AGENTS.md"}:
                files.append(path)
            if len(files) >= limit:
                return files
    return files


def summarize_project(project_root: Path) -> Dict[str, object]:
    files = _collect_files(project_root)
    relative_files = [str(path.relative_to(project_root)) for path in files]

    snippets: List[str] = []
    for path in files[:8]:
        rel = path.relative_to(project_root)
        try:
            content = path.read_text(encoding="utf-8")[:1200].strip()
        except UnicodeDecodeError:
            continue
        if content:
            snippets.append(f"## {rel}\n{content}")

    return {
        "project_root": str(project_root),
        "file_count": len(relative_files),
        "files": relative_files,
        "snippets": snippets,
    }
