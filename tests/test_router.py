import pytest

from pipeline_runtime_bridge.contract import ArtifactReference
from pipeline_runtime_bridge.context import create_runtime_context
from pipeline_runtime_bridge.router import (
    ARTIFACT_REGISTRY_FILENAME,
    get_artifact_registry_path,
    list_artifacts,
    register_artifact,
    resolve_artifact,
    route_artifact,
)


def test_get_artifact_registry_path(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    registry_path = get_artifact_registry_path(context)

    assert registry_path.name == ARTIFACT_REGISTRY_FILENAME
    assert registry_path.parent == tmp_path / "runtime_demo"


def test_register_artifact_saves_artifact(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    artifact = ArtifactReference(
        artifact_id="summary-001",
        artifact_type="summary_json",
        path="data/summary.json",
        producer="summary_engine",
    )

    register_artifact(context, artifact)
    artifacts = list_artifacts(context)

    assert len(artifacts) == 1
    assert artifacts[0].artifact_id == "summary-001"


def test_register_artifact_ignores_duplicate_id(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    artifact = ArtifactReference(
        artifact_id="summary-001",
        artifact_type="summary_json",
        path="data/summary.json",
        producer="summary_engine",
    )

    register_artifact(context, artifact)
    register_artifact(context, artifact)

    assert len(list_artifacts(context)) == 1


def test_resolve_artifact_returns_matching_artifact(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    artifact = ArtifactReference(
        artifact_id="audit-001",
        artifact_type="audit_jsonl",
        path="data/audit.jsonl",
        producer="audit_logger",
    )

    register_artifact(context, artifact)
    resolved = resolve_artifact(context, "audit-001")

    assert resolved.artifact_type == "audit_jsonl"
    assert resolved.producer == "audit_logger"


def test_resolve_artifact_raises_for_missing_artifact(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    with pytest.raises(KeyError):
        resolve_artifact(context, "missing-artifact")


def test_route_artifact_returns_route_payload(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    artifact = ArtifactReference(
        artifact_id="summary-001",
        artifact_type="summary_json",
        path="data/summary.json",
        producer="summary_engine",
    )

    register_artifact(context, artifact)
    route = route_artifact(context, artifact_id="summary-001", target="dashboard")

    assert route["artifact_id"] == "summary-001"
    assert route["target"] == "dashboard"
    assert route["routed"] is True
