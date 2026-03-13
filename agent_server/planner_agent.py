from __future__ import annotations

from typing import Dict, List

from models import TaskPhase, TaskRecord, TaskRequest
from routing import load_routing_config, planner_decides_premium


def build_initial_plan(task: TaskRequest) -> Dict[str, object]:
    routing_config = load_routing_config()
    assigned_agents: List[str] = ["planner", "code_agent", "build_agent"]

    if any(word in task.description.lower() for word in ["research", "paper", "compare", "derive", "theory"]):
        assigned_agents.append("research_agent")

    use_premium = planner_decides_premium(
        task_title=task.title,
        task_description=task.description,
        premium_allowed=task.premium_allowed,
    )

    notes = [
        "Planner created initial task decomposition.",
        f"Premium escalation {'enabled' if use_premium else 'not enabled'} for this run.",
    ]

    return {
        "phase": TaskPhase.PLANNING,
        "assigned_agents": assigned_agents,
        "notes": notes,
        "premium": use_premium,
        "routing_summary": {
            "planner_model": routing_config["planner"]["primary_model"],
            "code_model": routing_config["code_agent"]["primary_model"],
            "build_model": routing_config["build_agent"]["primary_model"],
        },
    }


def plan_to_record(task_id: str, task: TaskRequest) -> TaskRecord:
    plan = build_initial_plan(task)
    return TaskRecord(
        id=task_id,
        title=task.title,
        description=task.description,
        phase=plan["phase"],
        assigned_agents=plan["assigned_agents"],
        notes=plan["notes"],
        metadata={
            "premium_selected": plan["premium"],
            "project_path": task.project_path,
            "execution_target": task.execution_target,
            "ssh_host": task.ssh_host,
            "ssh_user": task.ssh_user,
            "ssh_port": task.ssh_port,
            "routing_summary": plan["routing_summary"],
        },
    )
