from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from auto_repair import apply_auto_repairs
from db import save_run, save_task
from llm_client import generate_role_text, resolve_role_model_ids
from memory import index_project_memory, search_project_memory
from models import TaskPhase, TaskRecord
from project_targets import resolve_target, run_commands_on_target, summarize_target, write_files_to_target
from routing import load_routing_config


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
    premium_calls_used: int
    memory_hits: List[str]
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


def _persist_intermediate_state(state: RunState, *, status: str) -> None:
    run_id = state["run_id"]
    task_id = state["task"]["id"]
    payload = dict(state)
    payload["status"] = status
    save_run(run_id, task_id, status, payload)


async def _planner_node(state: RunState) -> RunState:
    task = TaskRecord.model_validate(state["task"])
    project_summary = state["project_summary"]
    target = resolve_target(task.metadata)
    memory_hits: List[str] = []
    await index_project_memory(project_summary["project_key"], project_summary["snippets"])
    memory_hits = await search_project_memory(project_summary["project_key"], f"{task.title}\n{task.description}")
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
            "Retrieved memory:\n" + ("\n\n".join(memory_hits) if memory_hits else "None"),
            "Return a concise implementation plan with sections: summary, file changes, tests, risks.",
        ]
    )
    planner_output = await generate_role_text("planner", prompt, preferred_model_id=_select_model_for_role(state, "planner"))
    result = {
        "planner_output": planner_output,
        "memory_hits": memory_hits,
    }
    merged = dict(state)
    merged.update(result)
    _persist_intermediate_state(merged, status="planning")
    return result


def _select_model_for_role(state: RunState, role_name: str) -> str:
    task = TaskRecord.model_validate(state["task"])
    model_ids = resolve_role_model_ids(role_name)
    primary = model_ids[0]
    routing_policy = load_routing_config().get("policy", {})

    if len(model_ids) == 1:
        return primary

    local_retry_limit = int(routing_policy.get("max_local_retries_before_escalation", 2))
    premium_limit = int(routing_policy.get("max_premium_calls_per_run", 3))

    if task.metadata.get("premium_selected") and state.get("premium_calls_used", task.premium_calls_used) < premium_limit and state.get("retry_count", 0) >= local_retry_limit:
        for candidate in model_ids[1:]:
            if candidate.startswith("gpt_") or candidate.startswith("claude_"):
                return candidate

    return primary


async def _coder_node(state: RunState) -> RunState:
    task = TaskRecord.model_validate(state["task"])
    project_summary = state["project_summary"]
    planner_text = state["planner_output"]["response"]
    memory_text = "\n\n".join(state.get("memory_hits", []))
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
            "Prefer the smallest necessary file set.",
            "Do not paste the contents of one file into another unrelated file.",
            "Never embed source code listings inside README or docs unless the task explicitly asks for that.",
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
            "Retrieved memory:\n" + (memory_text or "None"),
            f"Planner plan:\n{planner_text}",
            failure_context,
        ]
    )
    selected_model = _select_model_for_role(state, "code_agent")
    code_result = await generate_role_text("code_agent", prompt, preferred_model_id=selected_model)
    parsed = _extract_json(code_result["response"])
    commands = task.metadata.get("commands_override") or parsed.get("commands") or ["python3 -m unittest -v"]
    premium_calls_used = state.get("premium_calls_used", 0)
    if code_result["provider"] in {"openai", "anthropic"}:
        premium_calls_used += 1
        task.premium_calls_used = premium_calls_used
        save_task(task.id, task.model_dump(mode="json"))
    result = {
        "code_result": code_result,
        "file_writes": parsed.get("file_writes", []),
        "commands": commands,
        "premium_calls_used": premium_calls_used,
    }
    merged = dict(state)
    merged.update(result)
    _persist_intermediate_state(merged, status="coding")
    return result


def _build_node(state: RunState) -> RunState:
    task = TaskRecord.model_validate(state["task"])
    target = resolve_target(task.metadata)

    mode = task.metadata.get("run_mode", "patch_and_run")
    touched_files: List[str] = []
    command_results: List[Dict[str, Any]] = []

    if mode in {"patch_only", "patch_and_run"}:
        touched_files = write_files_to_target(target, state.get("file_writes", []))
    if mode == "patch_and_run":
        command_results = run_commands_on_target(target, state.get("commands", []))
    repaired_files = []
    if target["kind"] == "local":
        repaired_files = apply_auto_repairs(target["project_root"], command_results)
    if repaired_files:
        touched_files = sorted(set(touched_files + repaired_files))
        if mode == "patch_and_run":
            command_results = run_commands_on_target(target, state.get("commands", []))
    task.files_touched = touched_files
    success = True if mode != "patch_and_run" else all(result["success"] for result in command_results)
    task.phase = TaskPhase.COMPLETED if success else TaskPhase.FAILED
    task.notes.append(
        f"Automated run completed in mode {mode}." if success else "Automated run failed."
    )
    save_task(task.id, task.model_dump(mode="json"))

    result = {
        "project_summary": summarize_target(target),
        "touched_files": touched_files,
        "command_results": command_results,
        "retry_count": state.get("retry_count", 0) + (0 if success else 1),
        "premium_calls_used": state.get("premium_calls_used", 0),
        "status": "completed" if success else "failed",
    }
    merged = dict(state)
    merged.update(result)
    _persist_intermediate_state(merged, status=result["status"])
    return result


def _route_after_build(state: RunState) -> str:
    if state.get("status") == "completed":
        return "end"
    task = TaskRecord.model_validate(state["task"])
    if task.metadata.get("run_mode") != "patch_and_run":
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
    target = resolve_target(task.metadata)

    run_id = str(uuid.uuid4())
    initial_state: RunState = {
        "run_id": run_id,
        "task": task.model_dump(mode="json"),
        "project_summary": summarize_target(target),
        "retry_count": 0,
        "premium_calls_used": task.premium_calls_used,
        "memory_hits": [],
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
