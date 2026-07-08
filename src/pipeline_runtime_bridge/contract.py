from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RuntimeContext:
    session_id: str
    pipeline_id: str
    workspace: str
    artifact_dir: str
    output_dir: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArtifactReference:
    artifact_id: str
    artifact_type: str
    path: str
    producer: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionRequest:
    target: str
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class ExecutionResult:
    success: bool
    message: str
    artifacts: list[ArtifactReference] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeEvent:
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=utc_now_iso)
