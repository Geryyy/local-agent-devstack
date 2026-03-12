from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

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
    scope: Optional[List[str]] = None
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
