from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List


KNOWN_STDLIB_IMPORTS = {
    "argparse",
    "contextlib",
    "io",
    "json",
    "tempfile",
    "unittest",
}


def _ensure_import(path: Path, module_name: str) -> bool:
    content = path.read_text(encoding="utf-8")
    if re.search(rf"^import {re.escape(module_name)}$", content, re.MULTILINE):
        return False
    lines = content.splitlines()
    insert_at = 0
    if lines and lines[0].startswith("from __future__ import"):
        insert_at = 1
        while insert_at < len(lines) and lines[insert_at] == "":
            insert_at += 1
    lines.insert(insert_at, f"import {module_name}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def apply_auto_repairs(project_root: Path, command_results: List[Dict[str, object]]) -> List[str]:
    changed: List[str] = []

    for result in command_results:
        stderr = str(result.get("stderr", ""))
        project_trace_files = [
            Path(match).resolve()
            for match in re.findall(r'File "([^"]+)", line \d+, in', stderr)
            if project_root.resolve() in Path(match).resolve().parents
        ]

        for missing_name in re.findall(r"NameError: name '([A-Za-z_][A-Za-z0-9_]*)' is not defined", stderr):
            if missing_name in KNOWN_STDLIB_IMPORTS:
                if not project_trace_files:
                    continue
                file_path = project_trace_files[-1]
                if _ensure_import(file_path, missing_name):
                    changed.append(str(file_path.relative_to(project_root)))

        if "unittest.mock.StringIO" in stderr:
            test_file = project_root / "test_todo.py"
            if test_file.exists():
                content = test_file.read_text(encoding="utf-8")
                updated = content.replace("unittest.mock.StringIO", "io.StringIO")
                if updated != content:
                    test_file.write_text(updated, encoding="utf-8")
                    changed.append("test_todo.py")
                if _ensure_import(test_file, "io") and "test_todo.py" not in changed:
                    changed.append("test_todo.py")

    return sorted(set(changed))
