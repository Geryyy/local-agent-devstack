from __future__ import annotations

import os
from typing import Any, Dict

import httpx

from routing import load_models_config, load_routing_config


def _resolve_model(model_id: str) -> Dict[str, Any]:
    models = load_models_config()

    local_models = models.get("local_models", {})
    premium_models = models.get("premium_models", {})

    if model_id in local_models:
        config = dict(local_models[model_id])
        config["model_id"] = model_id
        return config

    if model_id in premium_models:
        config = dict(premium_models[model_id])
        config["model_id"] = model_id
        return config

    raise ValueError(f"Unknown model id: {model_id}")


def resolve_role_model_ids(role_name: str) -> list[str]:
    routing = load_routing_config()
    role_config = routing[role_name]
    return [role_config["primary_model"], *(role_config.get("fallback_models") or [])]


async def generate_model_text(model_id: str, prompt: str) -> Dict[str, Any]:
    config = _resolve_model(model_id)
    provider = config["provider"]

    async with httpx.AsyncClient(timeout=120) as client:
        if provider == "ollama":
            base_url = config["base_url"].rstrip("/")
            response = await client.post(
                f"{base_url}/api/generate",
                json={
                    "model": config["model"],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0,
                    },
                },
            )
            response.raise_for_status()
            payload = response.json()
            text = payload["response"]
        elif provider == "openai":
            api_key = os.getenv(config["env_key"], "")
            if not api_key:
                raise ValueError(f"Missing required env key for model {model_id}: {config['env_key']}")
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": config["model"],
                    "input": prompt,
                },
            )
            response.raise_for_status()
            payload = response.json()
            text = payload["output"][0]["content"][0]["text"]
        elif provider == "anthropic":
            api_key = os.getenv(config["env_key"], "")
            if not api_key:
                raise ValueError(f"Missing required env key for model {model_id}: {config['env_key']}")
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": config["model"],
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            payload = response.json()
            text = "".join(block["text"] for block in payload["content"] if block["type"] == "text")
        else:
            raise ValueError(f"Unsupported provider for generation: {provider}")

    return {
        "model_id": model_id,
        "provider": provider,
        "model": config["model"],
        "response": text,
    }


async def generate_role_text(role_name: str, prompt: str, *, preferred_model_id: str | None = None) -> Dict[str, Any]:
    model_id = preferred_model_id or resolve_role_model_ids(role_name)[0]
    return await generate_model_text(model_id, prompt)
