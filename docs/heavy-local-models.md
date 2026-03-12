# Heavy Local Models

This repo keeps the default local path conservative for multi-agent work:

- planner: `qwen2.5-coder:7b`
- coder: `qwen2.5-coder:7b`
- build: `qwen2.5-coder:7b`

For a stronger mid-tier coder, the model catalog also includes:

- `ollama_coder_mid` -> `deepcoder:14b`

For heavier manual coding runs, the model catalog also includes:

- `ollama_coder_heavy` -> `qwen3-coder:30b`

## Why this stays opt-in

On the tested workstation GPU:

- GPU: RTX 5070 Ti
- VRAM: about 16 GiB usable
- observed local smoke test: `qwen3-coder:30b` succeeded in Ollama
- observed VRAM usage for a tiny prompt: about 15.6 GiB

That means the model is usable, but leaves very little room for:

- larger contexts
- concurrent agent requests
- other GPU workloads

## How to install it

Set the model name in `.env`:

```bash
OLLAMA_MID_MODEL=deepcoder:14b
OLLAMA_HEAVY_MODEL=qwen3-coder:30b
```

Pull either optional model:

```bash
./scripts/pull-ollama-model.sh OLLAMA_MID_MODEL
./scripts/pull-ollama-model.sh OLLAMA_HEAVY_MODEL
```

## How to use it

Use it manually through Ollama:

```bash
ollama run deepcoder:14b "Explain the refactor plan for this file."
ollama run qwen3-coder:30b "Explain the refactor plan for this file."
```

Or repoint the code agent temporarily by editing [configs/model-routing.yaml](/home/geraldebmer/repos/local-agent-devstack/configs/model-routing.yaml) and setting one of:

```yaml
code_agent:
  primary_model: ollama_coder_mid
```

```yaml
code_agent:
  primary_model: ollama_coder_heavy
```

Revert that change after the heavy task if you want to keep the safer multi-agent baseline.
