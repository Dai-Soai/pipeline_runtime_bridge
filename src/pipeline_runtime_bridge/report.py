from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from pipeline_runtime_bridge.contract import RuntimeContext
from pipeline_runtime_bridge.events import read_runtime_events
from pipeline_runtime_bridge.router import list_artifacts


RUNTIME_REPORT_FILENAME = "runtime_report.json"


def build_runtime_report(context: RuntimeContext) -> dict:
    artifacts = list_artifacts(context)
    events = read_runtime_events(context)

    event_types = [event.event_type for event in events]
    artifact_types = [artifact.artifact_type for artifact in artifacts]

    status = "empty"
    if "RuntimeFailed" in event_types:
        status = "failed"
    elif "ExecutionCompleted" in event_types:
        status = "completed"
    elif events:
        status = "running"

    return {
        "status": status,
        "context": asdict(context),
        "summary": {
            "artifact_count": len(artifacts),
            "event_count": len(events),
            "artifact_types": sorted(set(artifact_types)),
            "event_types": sorted(set(event_types)),
        },
        "artifacts": [asdict(artifact) for artifact in artifacts],
        "events": [asdict(event) for event in events],
    }


def get_runtime_report_path(context: RuntimeContext) -> Path:
    return Path(context.output_dir) / RUNTIME_REPORT_FILENAME


def write_runtime_report(context: RuntimeContext) -> Path:
    report_path = get_runtime_report_path(context)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = build_runtime_report(context)

    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return report_path
