# Model Routing Policy

This repo uses a local-first routing policy.

## Goals

- keep routine work local
- use premium models only when they add clear value
- keep routing inspectable and explicit
- keep credentials on the workstation only

## Preferred models by role

### Planner

- primary: `ollama_fast`
- fallback: `gpt_5_4`
- premium review fallback: `claude_opus`

### Code agent

- primary: `ollama_coder`
- optional mid local model: `ollama_coder_mid`
- optional heavy local model: `ollama_coder_heavy`
- fallback: `claude_sonnet`
- local fallback: `ollama_fast`

### Research agent

- primary: `ollama_fast`
- fallback: `gpt_5_4`
- premium review fallback: `claude_opus`

### Build/Test agent

- primary: `ollama_build`
- fallback: `ollama_coder`

## Escalation rules

Keep `ollama_coder_heavy` as an operator-selected option, not the default always-on coder route, on 16 GB class GPUs. It can be useful for single heavy coding runs, but it leaves very little VRAM headroom for longer contexts or concurrent agents.

`ollama_coder_mid` is the likely next default candidate on this class of GPU because it should leave more headroom than `qwen3-coder:30b` while offering stronger coding quality than the 7B baseline.

Keep local for:

- routine coding
- docs
- summaries
- config generation
- log summarization

Allow premium escalation for:

- architecture spanning many files or repos
- difficult debugging after repeated local failure
- math or optimization-heavy reasoning
- final review on important work

The planner owns the decision to escalate. Worker agents may request escalation but do not decide it independently.

## Source of truth

- routing policy: [configs/model-routing.yaml](/home/geraldebmer/repos/local-agent-devstack/configs/model-routing.yaml)
- model catalog: [configs/models.yaml](/home/geraldebmer/repos/local-agent-devstack/configs/models.yaml)
