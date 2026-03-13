from __future__ import annotations

import asyncio
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse

from build_agent import describe_build_agent
from code_agent import describe_code_agent
from db import get_run as db_get_run
from db import get_task as db_get_task
from db import init_db, list_runs as db_list_runs, list_tasks as db_list_tasks, save_task
from llm_client import generate_role_text
from memory import index_project_memory, search_project_memory
from models import RunRecord, RunRequest, SteerRequest, TaskRecord, TaskRequest, TaskPhase
from planner_agent import plan_to_record
from project_targets import resolve_target, summarize_target
from research_agent import describe_research_agent
from routing import load_models_config, load_routing_config, validate_model_references
from workflow import execute_task_run


@asynccontextmanager
async def lifespan(_: FastAPI):
    validate_model_references(load_routing_config(), load_models_config())
    init_db()
    yield

app = FastAPI(title="local-agent-devstack Agent API", lifespan=lifespan)


def _studio_url(request: Request) -> str:
    base_url = str(request.base_url).rstrip("/")
    return f"https://smith.langchain.com/studio/?baseUrl={quote(base_url, safe=':/')}"


@app.get("/")
def root(request: Request) -> RedirectResponse:
    return RedirectResponse(url=_studio_url(request))


@app.get("/studio")
def studio(request: Request) -> RedirectResponse:
    return RedirectResponse(url=_studio_url(request))


@app.get("/ui")
def ui(request: Request) -> RedirectResponse:
    return RedirectResponse(url=_studio_url(request))


@app.get("/ops")
def ops() -> FileResponse:
    return FileResponse(Path(__file__).resolve().parent / "static" / "dashboard.html")

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
            {"name": "memory_agent", "purpose": "Indexes and retrieves project snippets for planner and coder context."},
        ]
    }


@app.post("/tasks", response_model=TaskRecord)
def create_task(task: TaskRequest) -> TaskRecord:
    task_id = str(uuid.uuid4())
    record = plan_to_record(task_id, task)
    record.metadata["constraints"] = task.constraints
    record.metadata["acceptance_criteria"] = task.acceptance_criteria
    record.metadata["task_type"] = task.task_type
    record.metadata["execution_target"] = task.execution_target
    record.metadata["ssh_host"] = task.ssh_host
    record.metadata["ssh_user"] = task.ssh_user
    record.metadata["ssh_port"] = task.ssh_port
    save_task(task_id, record.model_dump(mode="json"))
    return record


@app.get("/tasks", response_model=List[TaskRecord])
def list_tasks() -> List[TaskRecord]:
    return [TaskRecord.model_validate(item) for item in db_list_tasks()]


@app.get("/tasks/{task_id}", response_model=TaskRecord)
def get_task(task_id: str) -> TaskRecord:
    payload = db_get_task(task_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRecord.model_validate(payload)


def _require_project(task: TaskRecord) -> dict:
    try:
        target = resolve_target(task.metadata)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return summarize_target(target)


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
    save_task(task_id, record.model_dump(mode="json"))
    return {
        "task_id": task_id,
        "project_summary": project_summary,
        "planner_output": generated,
    }


@app.get("/tasks/{task_id}/memory")
async def task_memory(task_id: str) -> dict:
    record = get_task(task_id)
    project_summary = _require_project(record)
    await index_project_memory(project_summary["project_key"], project_summary["snippets"])
    results = await search_project_memory(project_summary["project_key"], f"{record.title}\n{record.description}")
    return {"task_id": task_id, "memory_hits": results}


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
    record = get_task(task_id)
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

    save_task(task_id, record.model_dump(mode="json"))
    return record


@app.post("/tasks/{task_id}/steer", response_model=TaskRecord)
def steer_task(task_id: str, steer_request: SteerRequest) -> TaskRecord:
    record = get_task(task_id)
    if steer_request.note:
        record.notes.append(f"Operator: {steer_request.note}")
    if steer_request.premium_selected is not None:
        record.metadata["premium_selected"] = steer_request.premium_selected
        record.notes.append(
            f"Operator set premium_selected={steer_request.premium_selected}."
        )
    if steer_request.commands_override:
        record.metadata["commands_override"] = steer_request.commands_override
        record.notes.append("Operator updated verification commands.")
    save_task(task_id, record.model_dump(mode="json"))
    return record


@app.post("/tasks/{task_id}/runs", response_model=RunRecord)
async def create_run(task_id: str, run_request: RunRequest) -> RunRecord:
    record = get_task(task_id)
    if run_request.commands_override:
        record.metadata["commands_override"] = run_request.commands_override
    record.metadata["run_mode"] = run_request.mode
    save_task(task_id, record.model_dump(mode="json"))

    result = await execute_task_run(record)
    return RunRecord(
        id=result["run_id"],
        task_id=task_id,
        status=result["status"],
        planner_output=result.get("planner_output"),
        code_result=result.get("code_result"),
        touched_files=result.get("touched_files", []),
        command_results=result.get("command_results", []),
        error=result.get("error"),
    )


@app.get("/tasks/{task_id}/runs", response_model=List[RunRecord])
def list_task_runs(task_id: str) -> List[RunRecord]:
    _ = get_task(task_id)
    return [
        RunRecord(
            id=item["run_id"],
            task_id=task_id,
            status=item["status"],
            planner_output=item.get("planner_output"),
            code_result=item.get("code_result"),
            touched_files=item.get("touched_files", []),
            command_results=item.get("command_results", []),
            error=item.get("error"),
        )
        for item in db_list_runs(task_id)
    ]


@app.get("/runs/{run_id}", response_model=RunRecord)
def get_run(run_id: str) -> RunRecord:
    payload = db_get_run(run_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunRecord(
        id=payload["run_id"],
        task_id=payload["task"]["id"],
        status=payload["status"],
        planner_output=payload.get("planner_output"),
        code_result=payload.get("code_result"),
        touched_files=payload.get("touched_files", []),
        command_results=payload.get("command_results", []),
        error=payload.get("error"),
    )


@app.get("/runs/{run_id}/stream")
async def stream_run(run_id: str) -> StreamingResponse:
    async def event_source():
        last_payload = None
        while True:
            payload = db_get_run(run_id)
            if payload is None:
                yield "event: error\ndata: Run not found\n\n"
                break

            if payload != last_payload:
                record = RunRecord(
                    id=payload["run_id"],
                    task_id=payload["task"]["id"],
                    status=payload["status"],
                    planner_output=payload.get("planner_output"),
                    code_result=payload.get("code_result"),
                    touched_files=payload.get("touched_files", []),
                    command_results=payload.get("command_results", []),
                    error=payload.get("error"),
                )
                yield f"event: update\ndata: {record.model_dump_json()}\n\n"
                last_payload = payload

            if payload["status"] in {"completed", "failed"}:
                break

            await asyncio.sleep(1)

    return StreamingResponse(event_source(), media_type="text/event-stream")
