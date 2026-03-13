from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class TaskPhase(str, Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    RESEARCHING = "researching"
    CODING = "coding"
    BUILDING = "building"
    TESTING = "testing"
    WAITING_FOR_HUMAN = "waiting_for_human"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskRequest(BaseModel):
    title: str
    description: str
    project_path: Optional[str] = None
    execution_target: Literal["local", "ssh"] = "local"
    ssh_host: Optional[str] = None
    ssh_user: Optional[str] = None
    ssh_port: int = 22
    scope: Optional[List[str]] = None
    task_type: str = "routine_coding"
    constraints: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    premium_allowed: bool = False


class TaskRecord(BaseModel):
    id: str
    title: str
    description: str
    phase: TaskPhase
    assigned_agents: List[str] = Field(default_factory=list)
    files_touched: List[str] = Field(default_factory=list)
    premium_calls_used: int = 0
    notes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RunRequest(BaseModel):
    commands_override: List[str] = Field(default_factory=list)
    mode: Literal["patch_only", "patch_and_run"] = "patch_and_run"


class RunRecord(BaseModel):
    id: str
    task_id: str
    status: str
    planner_output: Optional[Dict[str, Any]] = None
    code_result: Optional[Dict[str, Any]] = None
    touched_files: List[str] = Field(default_factory=list)
    command_results: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None


class SteerRequest(BaseModel):
    note: str = ""
    premium_selected: Optional[bool] = None
    commands_override: List[str] = Field(default_factory=list)
