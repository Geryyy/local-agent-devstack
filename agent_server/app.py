from __future__ import annotations

import uuid
from typing import Dict, List

from fastapi import FastAPI, HTTPException

from build_agent import describe_build_agent
from code_agent import describe_code_agent
from models import TaskRecord, TaskRequest, TaskPhase
from planner_agent import plan_to_record
from research_agent import describe_research_agent
from routing import load_models_config, load_routing_config, validate_model_references

app = FastAPI(title="local-agent-devstack Agent API")

TASKS: Dict[str, TaskRecord] = {}


@app.on_event("startup")
def validate_configs() -> None:
    validate_model_references(load_routing_config(), load_models_config())


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/agents")
def agents() -> dict:
    return {
        "agents": [
            {"name": "planner", "purpose": "Decompose tasks and choose escalation."},
            describe_code_agent(),
            describe_research_agent(),
            describe_build_agent(),
            {"name": "memory_agent", "purpose": "Reserved for future retrieval and durable summaries."},
        ]
    }


@app.post("/tasks", response_model=TaskRecord)
def create_task(task: TaskRequest) -> TaskRecord:
    task_id = str(uuid.uuid4())
    record = plan_to_record(task_id, task)
    TASKS[task_id] = record
    return record


@app.get("/tasks", response_model=List[TaskRecord])
def list_tasks() -> List[TaskRecord]:
    return list(TASKS.values())


@app.get("/tasks/{task_id}", response_model=TaskRecord)
def get_task(task_id: str) -> TaskRecord:
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    return TASKS[task_id]


@app.post("/tasks/{task_id}/advance", response_model=TaskRecord)
def advance_task(task_id: str) -> TaskRecord:
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")

    record = TASKS[task_id]
    order = [
        TaskPhase.QUEUED,
        TaskPhase.PLANNING,
        TaskPhase.RESEARCHING,
        TaskPhase.CODING,
        TaskPhase.BUILDING,
        TaskPhase.TESTING,
        TaskPhase.COMPLETED,
    ]

    try:
        idx = order.index(record.phase)
    except ValueError:
        return record

    if idx < len(order) - 1:
        record.phase = order[idx + 1]
        record.notes.append(f"Task advanced to phase: {record.phase.value}")

    TASKS[task_id] = record
    return record
