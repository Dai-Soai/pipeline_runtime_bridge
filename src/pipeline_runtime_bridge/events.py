from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from pipeline_runtime_bridge.contract import RuntimeContext, RuntimeEvent

EVENT_LOG_FILENAME = "runtime_events.jsonl"


EVENT_TYPES = {
    "RuntimeStarted",
    "ExecutionRequested",
    "ArtifactRouted",
    "ExecutionCompleted",
    "RuntimeFinished",
    "RuntimeFailed",
    "ArtifactRegistered",
}


def is_supported_event_type(event_type: str) -> bool:
    return event_type in EVENT_TYPES


def get_event_log_path(context: RuntimeContext) -> Path:
    return Path(context.workspace) / EVENT_LOG_FILENAME


def create_runtime_event(
    event_type: str,
    payload: dict | None = None,
) -> RuntimeEvent:
    if not is_supported_event_type(event_type):
        raise ValueError(f"Unsupported event type: {event_type}")

    return RuntimeEvent(
        event_type=event_type,
        payload=payload or {},
    )


def append_runtime_event(
    context: RuntimeContext,
    event: RuntimeEvent,
) -> Path:
    log_path = get_event_log_path(context)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    return log_path


def read_runtime_events(context: RuntimeContext) -> list[RuntimeEvent]:
    log_path = get_event_log_path(context)

    if not log_path.exists():
        return []

    events: list[RuntimeEvent] = []

    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        data = json.loads(line)
        events.append(RuntimeEvent(**data))

    return events


def emit_runtime_event(
    context: RuntimeContext,
    event_type: str,
    payload: dict | None = None,
) -> RuntimeEvent:
    event = create_runtime_event(event_type=event_type, payload=payload)
    append_runtime_event(context, event)
    return event
