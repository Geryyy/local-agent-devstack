from __future__ import annotations

import uuid
from typing import Dict, List

from fastapi import FastAPI, HTTPException

from build_agent import describe_build_agent
from code_agent import describe_code_agent
from llm_client import generate_role_text
from models import TaskRecord, TaskRequest, TaskPhase
from planner_agent import plan_to_record
from research_agent import describe_research_agent
from routing import load_models_config, load_routing_config, validate_model_references
from workspace_context import resolve_project_path, summarize_project

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
    record.metadata["constraints"] = task.constraints
    record.metadata["acceptance_criteria"] = task.acceptance_criteria
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


def _require_project(task: TaskRecord) -> dict:
    project_path = task.metadata.get("project_path")
    if not project_path:
        raise HTTPException(status_code=400, detail="Task has no project_path")

    try:
        project_root = resolve_project_path(project_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if project_root is None:
        raise HTTPException(status_code=400, detail="Task has no project_path")

    return summarize_project(project_root)


@app.post("/tasks/{task_id}/draft-plan")
async def draft_plan(task_id: str) -> dict:
    record = get_task(task_id)
    project_summary = _require_project(record)

    prompt = "\n\n".join(
        [
            "You are the planner agent for a local coding stack.",
            f"Task title: {record.title}",
            f"Task description: {record.description}",
            f"Constraints: {', '.join(record.metadata.get('constraints', [])) or 'none'}",
            f"Acceptance criteria: {', '.join(record.metadata.get('acceptance_criteria', [])) or 'none'}",
            f"Project root: {project_summary['project_root']}",
            "Files:\n- " + "\n- ".join(project_summary["files"][:20]),
            "\n\n".join(project_summary["snippets"][:4]),
            "Return a concise implementation plan with sections: summary, file changes, tests, risks.",
        ]
    )

    generated = await generate_role_text("planner", prompt)
    record.notes.append("Planner drafted a project-aware implementation plan.")
    TASKS[task_id] = record
    return {
        "task_id": task_id,
        "project_summary": project_summary,
        "planner_output": generated,
    }


@app.get("/tasks/{task_id}/briefs")
def task_briefs(task_id: str) -> dict:
    record = get_task(task_id)
    project_summary = _require_project(record)
    file_list = "\n- ".join(project_summary["files"][:20])
    routing = load_routing_config()

    briefs = []
    for agent_name in record.assigned_agents:
        if agent_name == "planner":
            model_key = routing["planner"]["primary_model"]
            objective = "Refine scope and sequence the work."
        elif agent_name == "code_agent":
            model_key = routing["code_agent"]["primary_model"]
            objective = "Implement the requested code changes in small patches."
        elif agent_name == "build_agent":
            model_key = routing["build_agent"]["primary_model"]
            objective = "Run tests/build commands and summarize exact results."
        else:
            model_key = routing["research_agent"]["primary_model"]
            objective = "Support design and research questions with concise recommendations."

        prompt = "\n\n".join(
            [
                f"Role: {agent_name}",
                f"Objective: {objective}",
                f"Task: {record.title}",
                record.description,
                f"Project root: {project_summary['project_root']}",
                "Visible files:\n- " + file_list,
                "Constraints:\n- " + "\n- ".join(record.metadata.get("constraints", []) or ["None"]),
                "Acceptance criteria:\n- " + "\n- ".join(record.metadata.get("acceptance_criteria", []) or ["None"]),
            ]
        )
        briefs.append(
            {
                "agent": agent_name,
                "model": model_key,
                "objective": objective,
                "prompt": prompt,
            }
        )

    return {"task_id": task_id, "briefs": briefs}


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
