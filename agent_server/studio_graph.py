from __future__ import annotations

import uuid
from typing import Any, Dict, List, Literal, TypedDict

from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph

from db import init_db, save_run, save_task
from memory import index_project_memory, search_project_memory
from models import TaskRecord, TaskRequest
from planner_agent import plan_to_record
from project_targets import resolve_target, summarize_target
from routing import load_models_config, load_routing_config, validate_model_references
from workflow import (
    _build_node,
    _coder_node,
    _planner_node,
    _route_after_build,
)


class StudioTaskInput(BaseModel):
    title: str
    description: str
    project_path: str
    execution_target: Literal["local", "ssh"] = "local"
    ssh_host: str | None = None
    ssh_user: str | None = None
    ssh_port: int = 22
    task_type: str = "routine_coding"
    constraints: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    premium_allowed: bool = False
    run_mode: Literal["patch_only", "patch_and_run"] = "patch_and_run"
    commands_override: List[str] = Field(default_factory=list)
    operator_note: str = ""


class StudioRunState(TypedDict, total=False):
    title: str
    description: str
    project_path: str
    execution_target: Literal["local", "ssh"]
    ssh_host: str | None
    ssh_user: str | None
    ssh_port: int
    task_type: str
    constraints: List[str]
    acceptance_criteria: List[str]
    premium_allowed: bool
    run_mode: Literal["patch_only", "patch_and_run"]
    commands_override: List[str]
    operator_note: str
    run_id: str
    task: Dict[str, Any]
    project_summary: Dict[str, Any]
    planner_output: Dict[str, Any]
    code_result: Dict[str, Any]
    file_writes: List[Dict[str, str]]
    touched_files: List[str]
    commands: List[str]
    command_results: List[Dict[str, Any]]
    retry_count: int
    premium_calls_used: int
    memory_hits: List[str]
    status: str
    error: str


def _bootstrap_task(state: StudioRunState) -> StudioRunState:
    validate_model_references(load_routing_config(), load_models_config())
    init_db()

    payload = StudioTaskInput.model_validate(state)
    run_id = state.get("run_id", str(uuid.uuid4()))
    task_id = str(uuid.uuid4())
    task_request = TaskRequest(
        title=payload.title,
        description=payload.description,
        project_path=payload.project_path,
        execution_target=payload.execution_target,
        ssh_host=payload.ssh_host,
        ssh_user=payload.ssh_user,
        ssh_port=payload.ssh_port,
        task_type=payload.task_type,
        constraints=payload.constraints,
        acceptance_criteria=payload.acceptance_criteria,
        premium_allowed=payload.premium_allowed,
    )

    record = plan_to_record(task_id, task_request)
    record.metadata["constraints"] = payload.constraints
    record.metadata["acceptance_criteria"] = payload.acceptance_criteria
    record.metadata["task_type"] = payload.task_type
    record.metadata["run_mode"] = payload.run_mode
    if payload.commands_override:
        record.metadata["commands_override"] = payload.commands_override
    if payload.operator_note:
        record.notes.append(f"Operator: {payload.operator_note}")

    save_task(task_id, record.model_dump(mode="json"))

    target = resolve_target(record.metadata)
    project_summary = summarize_target(target)
    save_run(
        run_id,
        task_id,
        "running",
        {
            "run_id": run_id,
            "task": record.model_dump(mode="json"),
            "project_summary": project_summary,
            "retry_count": 0,
            "premium_calls_used": record.premium_calls_used,
            "memory_hits": [],
            "status": "running",
        },
    )

    return {
        "run_id": run_id,
        "task": record.model_dump(mode="json"),
        "project_summary": project_summary,
        "retry_count": 0,
        "premium_calls_used": record.premium_calls_used,
        "memory_hits": [],
        "status": "running",
    }


async def _refresh_memory(state: StudioRunState) -> StudioRunState:
    project_summary = state["project_summary"]
    task = TaskRecord.model_validate(state["task"])
    await index_project_memory(project_summary["project_key"], project_summary["snippets"])
    memory_hits = await search_project_memory(
        project_summary["project_key"],
        f"{task.title}\n{task.description}",
    )
    return {"memory_hits": memory_hits}

studio_workflow = StateGraph(StudioRunState, input=StudioTaskInput)
studio_workflow.add_node("bootstrap", _bootstrap_task)
studio_workflow.add_node("memory", _refresh_memory)
studio_workflow.add_node("planner", _planner_node)
studio_workflow.add_node("coder", _coder_node)
studio_workflow.add_node("builder", _build_node)
studio_workflow.set_entry_point("bootstrap")
studio_workflow.add_edge("bootstrap", "memory")
studio_workflow.add_edge("memory", "planner")
studio_workflow.add_edge("planner", "coder")
studio_workflow.add_edge("coder", "builder")
studio_workflow.add_conditional_edges(
    "builder",
    _route_after_build,
    {
        "retry": "coder",
        "end": END,
    },
)

studio_graph = studio_workflow.compile(name="local_agent_devstack")
