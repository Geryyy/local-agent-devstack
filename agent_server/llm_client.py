from __future__ import annotations

from typing import Any, Dict

import httpx

from routing import load_models_config, load_routing_config


def _resolve_role_model(role_name: str) -> Dict[str, Any]:
    routing = load_routing_config()
    models = load_models_config()

    model_id = routing[role_name]["primary_model"]
    local_models = models.get("local_models", {})
    premium_models = models.get("premium_models", {})

    if model_id in local_models:
        config = dict(local_models[model_id])
        config["model_id"] = model_id
        return config

    if model_id in premium_models:
        raise ValueError(f"Role {role_name} is mapped to premium model {model_id}; local runtime only for now.")

    raise ValueError(f"Unknown model id for role {role_name}: {model_id}")


async def generate_role_text(role_name: str, prompt: str) -> Dict[str, Any]:
    config = _resolve_role_model(role_name)
    provider = config["provider"]

    if provider != "ollama":
        raise ValueError(f"Unsupported provider for local generation: {provider}")

    base_url = config["base_url"].rstrip("/")
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{base_url}/api/generate",
            json={
                "model": config["model"],
                "prompt": prompt,
                "stream": False,
            },
        )
        response.raise_for_status()
        payload = response.json()

    return {
        "model_id": config["model_id"],
        "provider": provider,
        "model": config["model"],
        "response": payload["response"],
    }
