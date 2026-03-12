from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from auto_repair import apply_auto_repairs
from db import save_run, save_task
from executor import run_commands, write_files
from llm_client import generate_role_text
from models import TaskPhase, TaskRecord
from workspace_context import resolve_project_path, summarize_project


class RunState(TypedDict, total=False):
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
    status: str
    error: str


def _extract_json(text: str) -> Dict[str, Any]:
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
    if candidate is None:
        raise ValueError("Model did not return JSON output.")
    return json.loads(candidate)


async def _planner_node(state: RunState) -> RunState:
    task = TaskRecord.model_validate(state["task"])
    project_summary = state["project_summary"]
    prompt = "\n\n".join(
        [
            "You are the planner agent for a local coding stack.",
            f"Task title: {task.title}",
            f"Task description: {task.description}",
            f"Constraints: {', '.join(task.metadata.get('constraints', [])) or 'none'}",
            f"Acceptance criteria: {', '.join(task.metadata.get('acceptance_criteria', [])) or 'none'}",
            f"Project root: {project_summary['project_root']}",
            "Files:\n- " + "\n- ".join(project_summary["files"][:20]),
            "\n\n".join(project_summary["snippets"][:4]),
            "Return a concise implementation plan with sections: summary, file changes, tests, risks.",
        ]
    )
    planner_output = await generate_role_text("planner", prompt)
    return {"planner_output": planner_output}


async def _coder_node(state: RunState) -> RunState:
    task = TaskRecord.model_validate(state["task"])
    project_summary = state["project_summary"]
    planner_text = state["planner_output"]["response"]
    failure_context = ""
    if state.get("command_results"):
        failure_context = "\n\nPrevious command failures:\n" + "\n\n".join(
            [
                f"Command: {item['command']}\nReturn code: {item['returncode']}\nSTDOUT:\n{item['stdout']}\nSTDERR:\n{item['stderr']}"
                for item in state["command_results"]
                if not item["success"]
            ]
        )
    prompt = "\n\n".join(
        [
            "You are the code agent for a local coding stack.",
            "Return strict JSON with keys: summary, file_writes, commands, notes.",
            "Return JSON only. Do not wrap it in markdown fences.",
            "file_writes must be a list of objects with path and content.",
            "Use project-relative paths only, for example todo.py or test_todo.py.",
            "commands must be a list of shell commands to verify the change.",
            "Only write files under the project root.",
            "All code must be syntactically valid.",
            "When writing Python f-strings with dict access, use single quotes inside the expression, for example item['title'].",
            "Because the task requires tests and docs, include updates for both test_todo.py and README.md.",
            "Use only Python standard library tools.",
            "Tests must use unittest, not pytest.",
            "Do not use pytest, capsys, venv creation, or any third-party packages.",
            "Use python3 -m unittest -v for tests.",
            f"Task title: {task.title}",
            f"Task description: {task.description}",
            f"Constraints: {', '.join(task.metadata.get('constraints', [])) or 'none'}",
            f"Acceptance criteria: {', '.join(task.metadata.get('acceptance_criteria', [])) or 'none'}",
            f"Project root: {project_summary['project_root']}",
            "Visible files:\n- " + "\n- ".join(project_summary["files"][:20]),
            "\n\n".join(project_summary["snippets"][:8]),
            f"Planner plan:\n{planner_text}",
            failure_context,
        ]
    )
    code_result = await generate_role_text("code_agent", prompt)
    parsed = _extract_json(code_result["response"])
    commands = task.metadata.get("commands_override") or parsed.get("commands") or ["python3 -m unittest -v"]
    return {
        "code_result": code_result,
        "file_writes": parsed.get("file_writes", []),
        "commands": commands,
    }


def _build_node(state: RunState) -> RunState:
    task = TaskRecord.model_validate(state["task"])
    project_root = resolve_project_path(task.metadata.get("project_path"))
    if project_root is None:
        raise ValueError("Task has no project path.")

    touched_files = write_files(project_root, state.get("file_writes", []))
    command_results = run_commands(project_root, state.get("commands", []))
    repaired_files = apply_auto_repairs(project_root, command_results)
    if repaired_files:
        touched_files = sorted(set(touched_files + repaired_files))
        command_results = run_commands(project_root, state.get("commands", []))
    task.files_touched = touched_files
    success = all(result["success"] for result in command_results)
    task.phase = TaskPhase.COMPLETED if success else TaskPhase.FAILED
    task.notes.append(
        "Automated run completed successfully." if success else "Automated run failed."
    )
    save_task(task.id, task.model_dump(mode="json"))

    return {
        "project_summary": summarize_project(project_root),
        "touched_files": touched_files,
        "command_results": command_results,
        "retry_count": state.get("retry_count", 0) + (0 if success else 1),
        "status": "completed" if success else "failed",
    }


def _route_after_build(state: RunState) -> str:
    if state.get("status") == "completed":
        return "end"
    if state.get("retry_count", 0) < 4:
        return "retry"
    return "end"


def _build_workflow():
    workflow = StateGraph(RunState)
    workflow.add_node("planner", _planner_node)
    workflow.add_node("coder", _coder_node)
    workflow.add_node("builder", _build_node)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "coder")
    workflow.add_edge("coder", "builder")
    workflow.add_conditional_edges(
        "builder",
        _route_after_build,
        {
            "retry": "coder",
            "end": END,
        },
    )
    return workflow.compile()


GRAPH = _build_workflow()


async def execute_task_run(task: TaskRecord) -> Dict[str, Any]:
    project_root = resolve_project_path(task.metadata.get("project_path"))
    if project_root is None:
        raise ValueError("Task has no project_path.")

    run_id = str(uuid.uuid4())
    initial_state: RunState = {
        "run_id": run_id,
        "task": task.model_dump(mode="json"),
        "project_summary": summarize_project(project_root),
        "retry_count": 0,
        "status": "running",
    }
    save_run(run_id, task.id, "running", dict(initial_state))

    try:
        result = await GRAPH.ainvoke(initial_state)
        payload = dict(result)
        payload["status"] = payload.get("status", "completed")
        save_run(run_id, task.id, payload["status"], payload)
        return payload
    except Exception as exc:
        failed = dict(initial_state)
        failed["status"] = "failed"
        failed["error"] = str(exc)
        save_run(run_id, task.id, "failed", failed)
        raise
