from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROUTING_CONFIG = str(REPO_ROOT / "configs" / "model-routing.yaml")
DEFAULT_MODELS_CONFIG = str(REPO_ROOT / "configs" / "models.yaml")


def _load_yaml(path_str: str) -> Dict[str, Any]:
    path = Path(path_str)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_routing_config() -> Dict[str, Any]:
    return _load_yaml(os.getenv("AGENT_ROUTING_CONFIG", DEFAULT_ROUTING_CONFIG))


def load_models_config() -> Dict[str, Any]:
    return _load_yaml(os.getenv("AGENT_MODELS_CONFIG", DEFAULT_MODELS_CONFIG))


def planner_decides_premium(task_title: str, task_description: str, premium_allowed: bool) -> bool:
    text = f"{task_title} {task_description}".lower()

    hard_keywords = [
        "architecture",
        "cross-repo",
        "multi-repo",
        "review",
        "derivation",
        "proof",
        "optimization",
        "debugging",
        "control",
        "math",
    ]
    return premium_allowed and any(keyword in text for keyword in hard_keywords)


def validate_model_references(routing_config: Dict[str, Any], models_config: Dict[str, Any]) -> None:
    defined_models = set(models_config.get("local_models", {})) | set(models_config.get("premium_models", {}))
    referenced_models = set()

    for section, data in routing_config.items():
        if not isinstance(data, dict):
            continue
        primary_model = data.get("primary_model")
        if primary_model:
            referenced_models.add(primary_model)
        for fallback in data.get("fallback_models", []) or []:
            referenced_models.add(fallback)

    missing = sorted(referenced_models - defined_models)
    if missing:
        raise ValueError(f"Unknown model identifiers in routing config: {', '.join(missing)}")
