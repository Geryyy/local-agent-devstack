#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def ollama_generate(base_url: str, model: str, prompt: str) -> dict[str, Any]:
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": 0,
            "options": {"temperature": 0},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/generate",
        data=payload,
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


def benchmark_model(base_url: str, model: str, prompt: str) -> dict[str, Any]:
    started = time.perf_counter()
    before_gpu = gpu_memory_snapshot()
    payload = ollama_generate(base_url, model, prompt)
    elapsed = time.perf_counter() - started
    after_gpu = gpu_memory_snapshot()
    response_text = payload.get("response", "").strip()
    eval_count = payload.get("eval_count")
    eval_duration = payload.get("eval_duration")
    prompt_eval_count = payload.get("prompt_eval_count")

    tokens_per_second = None
    if eval_count and eval_duration:
        tokens_per_second = round(eval_count / (eval_duration / 1_000_000_000), 2)

    return {
        "model": model,
        "elapsed_seconds": round(elapsed, 2),
        "response_preview": response_text[:120],
        "response_ok": response_text == "benchmark smoke ok",
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
        "--json",
        action="store_true",
        help="Print machine-readable JSON only.",
    )
    args = parser.parse_args()

    models = args.models or DEFAULT_MODELS
    results: list[dict[str, Any]] = []

    for model in models:
        try:
            result = benchmark_model(args.base_url, model, args.prompt)
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
