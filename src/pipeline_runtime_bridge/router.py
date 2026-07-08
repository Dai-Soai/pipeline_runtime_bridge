from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from pipeline_runtime_bridge.contract import ArtifactReference, RuntimeContext


ARTIFACT_REGISTRY_FILENAME = "artifact_registry.json"


def get_artifact_registry_path(context: RuntimeContext) -> Path:
    return Path(context.workspace) / ARTIFACT_REGISTRY_FILENAME


def load_artifact_registry(context: RuntimeContext) -> list[ArtifactReference]:
    registry_path = get_artifact_registry_path(context)

    if not registry_path.exists():
        return []

    data = json.loads(registry_path.read_text(encoding="utf-8"))

    return [ArtifactReference(**item) for item in data]


def save_artifact_registry(
    context: RuntimeContext,
    artifacts: list[ArtifactReference],
) -> Path:
    registry_path = get_artifact_registry_path(context)
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    registry_path.write_text(
        json.dumps([asdict(artifact) for artifact in artifacts], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return registry_path


def register_artifact(
    context: RuntimeContext,
    artifact: ArtifactReference,
) -> ArtifactReference:
    artifacts = load_artifact_registry(context)

    existing_ids = {item.artifact_id for item in artifacts}
    if artifact.artifact_id not in existing_ids:
        artifacts.append(artifact)

    save_artifact_registry(context, artifacts)

    return artifact


def list_artifacts(context: RuntimeContext) -> list[ArtifactReference]:
    return load_artifact_registry(context)


def resolve_artifact(
    context: RuntimeContext,
    artifact_id: str,
) -> ArtifactReference:
    artifacts = load_artifact_registry(context)

    for artifact in artifacts:
        if artifact.artifact_id == artifact_id:
            return artifact

    raise KeyError(f"Artifact not found: {artifact_id}")


def route_artifact(
    context: RuntimeContext,
    artifact_id: str,
    target: str,
) -> dict:
    artifact = resolve_artifact(context, artifact_id)

    return {
        "artifact_id": artifact.artifact_id,
        "artifact_type": artifact.artifact_type,
        "path": artifact.path,
        "producer": artifact.producer,
        "target": target,
        "routed": True,
    }
