from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from pipeline_runtime_bridge.contract import RuntimeContext


CONTEXT_FILENAME = "runtime_context.json"


def create_runtime_context(
    workspace: str,
    pipeline_id: str = "pipeline-demo",
    session_id: str | None = None,
    metadata: dict | None = None,
) -> RuntimeContext:
    workspace_path = Path(workspace)
    artifact_dir = workspace_path / "artifacts"
    output_dir = workspace_path / "output"

    artifact_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    return RuntimeContext(
        session_id=session_id or str(uuid4()),
        pipeline_id=pipeline_id,
        workspace=str(workspace_path),
        artifact_dir=str(artifact_dir),
        output_dir=str(output_dir),
        metadata=metadata or {},
    )


def save_runtime_context(context: RuntimeContext) -> Path:
    workspace_path = Path(context.workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    context_path = workspace_path / CONTEXT_FILENAME
    context_path.write_text(
        json.dumps(asdict(context), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return context_path


def load_runtime_context(workspace: str) -> RuntimeContext:
    context_path = Path(workspace) / CONTEXT_FILENAME

    if not context_path.exists():
        raise FileNotFoundError(f"Runtime context not found: {context_path}")

    data = json.loads(context_path.read_text(encoding="utf-8"))

    return RuntimeContext(**data)


def get_context_path(workspace: str) -> Path:
    return Path(workspace) / CONTEXT_FILENAME
