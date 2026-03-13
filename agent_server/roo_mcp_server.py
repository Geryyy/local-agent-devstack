from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List

import httpx
from mcp.server.fastmcp import FastMCP


API_BASE_URL = os.getenv("AGENT_API_BASE_URL", "http://127.0.0.1:2024").rstrip("/")
TIMEOUT = float(os.getenv("AGENT_API_TIMEOUT_SECONDS", "120"))

mcp = FastMCP("local-agent-devstack")


def _client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE_URL, timeout=TIMEOUT)


def _parse_json_payload(payload: str) -> Dict[str, Any]:
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("Payload must be a JSON object.")
    return data


@mcp.tool()
def health_check() -> Dict[str, Any]:
    """Confirm that the local agent backend is reachable."""
    with _client() as client:
        response = client.get("/health")
        response.raise_for_status()
        return response.json()


@mcp.tool()
def list_agents() -> Dict[str, Any]:
    """Return the available backend agent roles."""
    with _client() as client:
        response = client.get("/agents")
        response.raise_for_status()
        return response.json()


@mcp.tool()
def create_task(task_json: str) -> Dict[str, Any]:
    """Create a task from a JSON object string using the backend TaskRequest schema."""
    payload = _parse_json_payload(task_json)
    with _client() as client:
        response = client.post("/tasks", json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def list_tasks() -> List[Dict[str, Any]]:
    """List recent tasks."""
    with _client() as client:
        response = client.get("/tasks")
        response.raise_for_status()
        return response.json()


@mcp.tool()
def get_task(task_id: str) -> Dict[str, Any]:
    """Fetch one task by id."""
    with _client() as client:
        response = client.get(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.json()


@mcp.tool()
def draft_plan(task_id: str) -> Dict[str, Any]:
    """Ask the planner to draft a project-aware plan for the task."""
    with _client() as client:
        response = client.post(f"/tasks/{task_id}/draft-plan")
        response.raise_for_status()
        return response.json()


@mcp.tool()
def get_memory(task_id: str) -> Dict[str, Any]:
    """Fetch retrieval-backed memory hits for a task."""
    with _client() as client:
        response = client.get(f"/tasks/{task_id}/memory")
        response.raise_for_status()
        return response.json()


@mcp.tool()
def get_briefs(task_id: str) -> Dict[str, Any]:
    """Fetch role briefs for planner, coder, and build agents."""
    with _client() as client:
        response = client.get(f"/tasks/{task_id}/briefs")
        response.raise_for_status()
        return response.json()


@mcp.tool()
def steer_task(task_id: str, steer_json: str) -> Dict[str, Any]:
    """Apply steering to a task. Expects a JSON object matching SteerRequest."""
    payload = _parse_json_payload(steer_json)
    with _client() as client:
        response = client.post(f"/tasks/{task_id}/steer", json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def start_run(task_id: str, mode: str = "patch_and_run", commands_override: List[str] | None = None) -> Dict[str, Any]:
    """Start a task run in patch_only or patch_and_run mode."""
    payload: Dict[str, Any] = {"mode": mode}
    if commands_override:
        payload["commands_override"] = commands_override
    with _client() as client:
        response = client.post(f"/tasks/{task_id}/runs", json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def list_task_runs(task_id: str) -> List[Dict[str, Any]]:
    """List runs for a task."""
    with _client() as client:
        response = client.get(f"/tasks/{task_id}/runs")
        response.raise_for_status()
        return response.json()


@mcp.tool()
def get_run(run_id: str) -> Dict[str, Any]:
    """Fetch one run by id."""
    with _client() as client:
        response = client.get(f"/runs/{run_id}")
        response.raise_for_status()
        return response.json()


@mcp.tool()
def wait_for_run(run_id: str, poll_seconds: float = 2.0, max_polls: int = 120) -> Dict[str, Any]:
    """Poll a run until it reaches completed or failed, then return the final payload."""
    with _client() as client:
        for _ in range(max_polls):
            response = client.get(f"/runs/{run_id}")
            response.raise_for_status()
            payload = response.json()
            if payload["status"] in {"completed", "failed"}:
                return payload
            time.sleep(poll_seconds)
    raise TimeoutError(f"Run {run_id} did not finish after {max_polls} polls.")


if __name__ == "__main__":
    mcp.run()
