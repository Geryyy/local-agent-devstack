# Local Model Benchmarks

These notes capture practical workstation results for local coding models.

## Test machine

- GPU: RTX 5070 Ti
- VRAM: about 16 GiB
- Runtime: Ollama
- Date: 2026-03-12

## Benchmark method

Script:

- [scripts/benchmark-local-models.py](/home/geraldebmer/repos/local-agent-devstack/scripts/benchmark-local-models.py)

Prompt shape:

- deterministic smoke prompt
- `temperature: 0`
- `keep_alive: 0` to reduce cross-run contamination

## Observed results

### Smoke prompt

### `qwen2.5-coder:7b`

- response matched exactly
- about `1.8s` elapsed
- about `194.9 tokens/s`
- post-run GPU memory snapshot: about `5.1 GiB`

### `deepcoder:14b`

- did not follow the strict one-line response instruction
- emitted visible reasoning text
- about `8.7s` elapsed
- about `84.2 tokens/s`
- post-run GPU memory snapshot: about `9.7 GiB`

### `qwen3-coder:30b`

- response matched exactly
- about `6.3s` elapsed
- about `69.7 tokens/s`
- post-run GPU memory snapshot: about `15.6 GiB`

### Structured code-agent JSON prompt

This prompt was closer to a real worker task: return strict JSON for a small todo CLI change.

### `qwen2.5-coder:7b`

- returned valid JSON
- about `52.8s` elapsed
- about `10.1 tokens/s`

### `deepcoder:14b`

- did not finish within the `90s` benchmark timeout
- still needs more model-specific prompting or templating before it is a safe default worker

### `qwen3-coder:30b`

- returned valid JSON
- about `38.6s` elapsed
- about `19.1 tokens/s`

## Recommendation

For this workstation today:

- keep `qwen2.5-coder:7b` as the default planner/build/coder baseline
- keep `qwen3-coder:30b` as an opt-in heavy local coder for single important coding runs
- treat `deepcoder:14b` as promising, but not the default until it behaves better in strict agent prompts

Operationally:

- `qwen2.5-coder:7b` is still the safest always-on multi-agent default
- `qwen3-coder:30b` is currently the strongest local structured coder on this machine when you can afford the VRAM

## What to test next

- whether `deepcoder:14b` behaves better with a model-specific system prompt
- whether Open WebUI or another client-side template suppresses visible reasoning reliably
- whether a coding-task benchmark with file edits and tests changes the ranking versus this smoke prompt
