import json
from pathlib import Path

from pipeline_runtime_bridge.context import create_runtime_context
from pipeline_runtime_bridge.contract import ArtifactReference, ExecutionRequest
from pipeline_runtime_bridge.dispatcher import (
    SUPPORTED_TARGETS,
    dispatch_request,
    execute_route,
    is_supported_target,
    mock_execute,
)
from pipeline_runtime_bridge.router import list_artifacts, register_artifact


def test_supported_targets_contains_expected_targets():
    assert "dashboard" in SUPPORTED_TARGETS
    assert "audit" in SUPPORTED_TARGETS
    assert "router" in SUPPORTED_TARGETS
    assert "summary" in SUPPORTED_TARGETS


def test_is_supported_target_returns_true_for_known_target():
    assert is_supported_target("dashboard") is True


def test_is_supported_target_returns_false_for_unknown_target():
    assert is_supported_target("unknown") is False


def test_mock_execute_returns_success_for_supported_target(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    request = ExecutionRequest(target="dashboard", action="generate")

    result = mock_execute(context, request)

    assert result.success is True
    assert result.artifacts
    assert result.artifacts[0].producer == "pipeline_runtime_bridge"
    assert result.metadata["mock"] is True


def test_mock_execute_registers_result_artifact(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    request = ExecutionRequest(target="audit", action="write")

    result = mock_execute(context, request)
    artifacts = list_artifacts(context)

    assert result.success is True
    assert len(artifacts) == 1
    assert artifacts[0].artifact_type == "audit_result"


def test_mock_execute_returns_failure_for_unsupported_target(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    request = ExecutionRequest(target="unknown", action="run")

    result = mock_execute(context, request)

    assert result.success is False
    assert "Unsupported target" in result.message


def test_dispatch_request_uses_mock_execution(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    request = ExecutionRequest(target="summary", action="generate")

    result = dispatch_request(context, request)

    assert result.success is True
    assert result.metadata["target"] == "summary"


def test_execute_route_dispatches_routed_artifact(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    artifact = ArtifactReference(
        artifact_id="summary-001",
        artifact_type="summary_json",
        path="data/summary.json",
        producer="summary_engine",
    )
    register_artifact(context, artifact)

    result = execute_route(context, artifact_id="summary-001", target="dashboard")

    assert result.success is True
    assert result.metadata["target"] == "dashboard"
    assert result.metadata["action"] == "route"


def test_mock_execute_writes_physical_output_artifact(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    request = ExecutionRequest(target="dashboard", action="generate")

    result = mock_execute(context, request)

    artifact_path = Path(result.artifacts[0].path)

    assert artifact_path.exists()

    data = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert data["status"] == "success"
    assert data["mock"] is True
    assert data["target"] == "dashboard"
    assert data["action"] == "generate"
    assert data["producer"] == "pipeline_runtime_bridge"
    assert result.artifacts[0].metadata["physical_file"] is True
