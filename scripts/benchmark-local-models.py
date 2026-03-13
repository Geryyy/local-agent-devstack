#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any


DEFAULT_MODELS = [
    "qwen2.5-coder:7b",
    "deepcoder:14b",
    "qwen3-coder:30b",
]

DEFAULT_PROMPT = (
    "You are benchmarking local coding models. "
    "Do not think aloud. Do not emit reasoning tags. "
    "Reply with exactly one line: benchmark smoke ok"
)

CODE_JSON_PROMPT = """You are the code agent for a local coding stack.
Return strict JSON with keys: summary, file_writes, commands, notes.
Return JSON only. Do not wrap it in markdown fences.
Do not emit hidden reasoning, chain-of-thought, or <think> tags.
file_writes must be a list of objects with path and content.
Use project-relative paths only.
commands must be a list of shell commands.
Only write files under the project root.
Use only Python standard library tools.
Tests must use unittest.

Task title: Add invalid-index test coverage
Task description: Update the dummy todo CLI to print a clearer invalid-index message and add a unittest for that case.
Constraints: stdlib only, keep changes small
Acceptance criteria: invalid index path is covered, tests use unittest, return valid JSON only
Project root: playground/dummy-agent-app
Visible files:
- todo.py
- test_todo.py

todo.py snippet:
def cmd_done(args: argparse.Namespace) -> None:
    items = load_items()
    if 1 <= args.index <= len(items):
        items[args.index - 1]["done"] = True
        save_items(items)
        print(f"marked as done: {items[args.index - 1]['title']}")
    else:
        print("Invalid item index")

test_todo.py snippet:
class TestTodoCLI(unittest.TestCase):
    @patch('todo.load_items')
    @patch('todo.save_items')
    def test_done(self, mock_save, mock_load):
        mock_load.return_value = [{'title': 'Buy groceries', 'done': False}]
        cmd_done(argparse.Namespace(index=1))
        mock_save.assert_called_once_with([{'title': 'Buy groceries', 'done': True}])
"""


def build_system_prompt(model: str) -> str | None:
    if model.startswith("deepcoder:"):
        return (
            "You are a coding model used inside an automated tool loop. "
            "Return only the final answer requested. "
            "Never emit hidden reasoning, chain-of-thought, or <think> tags. "
            "If JSON is requested, return valid JSON only."
        )
    return None


def ollama_generate(base_url: str, model: str, prompt: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": 0,
        "options": {"temperature": 0},
    }
    system_prompt = build_system_prompt(model)
    if system_prompt:
        payload["system"] = system_prompt
    encoded = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/generate",
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def gpu_memory_snapshot() -> str:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used,memory.total,utilization.gpu",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def _extract_json_candidate(text: str) -> dict[str, Any] | None:
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
    if candidate is None:
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def evaluate_response(scenario: str, response_text: str) -> tuple[bool, str]:
    if scenario == "smoke":
        return response_text == "benchmark smoke ok", response_text[:120]

    parsed = _extract_json_candidate(response_text)
    if parsed is None:
        return False, response_text[:120]
    if "<think>" in response_text.lower():
        return False, response_text[:120]
    required = {"summary", "file_writes", "commands", "notes"}
    if not required.issubset(parsed):
        return False, response_text[:120]
    return True, json.dumps(parsed)[:120]


def benchmark_model(base_url: str, model: str, prompt: str, scenario: str) -> dict[str, Any]:
    started = time.perf_counter()
    before_gpu = gpu_memory_snapshot()
    payload = ollama_generate(base_url, model, prompt)
    elapsed = time.perf_counter() - started
    after_gpu = gpu_memory_snapshot()
    response_text = payload.get("response", "").strip()
    eval_count = payload.get("eval_count")
    eval_duration = payload.get("eval_duration")
    prompt_eval_count = payload.get("prompt_eval_count")
    response_ok, preview = evaluate_response(scenario, response_text)

    tokens_per_second = None
    if eval_count and eval_duration:
        tokens_per_second = round(eval_count / (eval_duration / 1_000_000_000), 2)

    return {
        "model": model,
        "scenario": scenario,
        "elapsed_seconds": round(elapsed, 2),
        "response_preview": preview,
        "response_ok": response_ok,
        "prompt_eval_count": prompt_eval_count,
        "eval_count": eval_count,
        "tokens_per_second": tokens_per_second,
        "gpu_before": before_gpu,
        "gpu_after": after_gpu,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark local Ollama coding models.")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:11434",
        help="Ollama base URL",
    )
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Model to benchmark. Can be provided multiple times.",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt to send to each model.",
    )
    parser.add_argument(
        "--scenario",
        choices=["smoke", "code_json"],
        default="smoke",
        help="Benchmark scenario.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON only.",
    )
    args = parser.parse_args()

    models = args.models or DEFAULT_MODELS
    prompt = CODE_JSON_PROMPT if args.scenario == "code_json" else args.prompt
    results: list[dict[str, Any]] = []

    for model in models:
        try:
            result = benchmark_model(args.base_url, model, prompt, args.scenario)
        except urllib.error.HTTPError as exc:
            result = {
                "model": model,
                "error": f"HTTP {exc.code}: {exc.reason}",
                "response_ok": False,
            }
        except Exception as exc:  # noqa: BLE001
            result = {
                "model": model,
                "error": str(exc),
                "response_ok": False,
            }
        results.append(result)

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    for item in results:
        print(f"model: {item['model']}")
        if "error" in item:
            print(f"  error: {item['error']}")
            continue
        print(f"  ok: {item['response_ok']}")
        print(f"  elapsed_seconds: {item['elapsed_seconds']}")
        print(f"  tokens_per_second: {item['tokens_per_second']}")
        print(f"  gpu_before: {item['gpu_before']}")
        print(f"  gpu_after: {item['gpu_after']}")
        print(f"  response_preview: {item['response_preview']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
