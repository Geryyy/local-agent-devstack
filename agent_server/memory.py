from __future__ import annotations

import hashlib
import math
import os
from typing import List

import httpx


QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333").rstrip("/")
COLLECTION_NAME = os.getenv("AGENT_MEMORY_COLLECTION", "agent_project_memory")
VECTOR_SIZE = 64


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in text.replace("\n", " ").split() if token.strip()]


def _embed_text(text: str) -> List[float]:
    vector = [0.0] * VECTOR_SIZE
    for token in _tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        bucket = digest[0] % VECTOR_SIZE
        sign = 1.0 if digest[1] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


async def ensure_collection() -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.put(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}",
            json={"vectors": {"size": VECTOR_SIZE, "distance": "Cosine"}},
        )
        if response.status_code not in {200, 201, 409}:
            response.raise_for_status()


async def index_project_memory(project_key: str, snippets: List[str]) -> None:
    await ensure_collection()
    points = []
    for index, snippet in enumerate(snippets):
        point_id = abs(hash(f"{project_key}:{index}")) % (2**31)
        points.append(
            {
                "id": point_id,
                "vector": _embed_text(snippet),
                "payload": {
                    "project_key": project_key,
                    "text": snippet,
                },
            }
        )

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.put(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points",
            json={"points": points},
        )
        response.raise_for_status()


async def search_project_memory(project_key: str, query: str, limit: int = 3) -> List[str]:
    await ensure_collection()
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/search",
            json={
                "vector": _embed_text(query),
                "limit": limit,
                "filter": {
                    "must": [
                        {"key": "project_key", "match": {"value": project_key}},
                    ]
                },
                "with_payload": True,
            },
        )
        response.raise_for_status()
        payload = response.json()

    return [item["payload"]["text"] for item in payload.get("result", [])]
