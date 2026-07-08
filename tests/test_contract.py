from pipeline_runtime_bridge.contract import (
    ArtifactReference,
    ExecutionRequest,
    ExecutionResult,
    RuntimeContext,
    RuntimeEvent,
)


def test_runtime_context_can_be_created():
    context = RuntimeContext(
        session_id="session-001",
        pipeline_id="pipeline-demo",
        workspace="data/runtime_demo",
        artifact_dir="data/runtime_demo/artifacts",
        output_dir="data/runtime_demo/output",
        metadata={"env": "test"},
    )

    assert context.session_id == "session-001"
    assert context.pipeline_id == "pipeline-demo"
    assert context.metadata["env"] == "test"


def test_artifact_reference_can_be_created():
    artifact = ArtifactReference(
        artifact_id="summary-001",
        artifact_type="summary_json",
        path="data/summary.json",
        producer="summary_engine",
        metadata={"size": 123},
    )

    assert artifact.artifact_id == "summary-001"
    assert artifact.artifact_type == "summary_json"
    assert artifact.producer == "summary_engine"


def test_execution_request_can_be_created():
    request = ExecutionRequest(
        target="dashboard",
        action="generate",
        parameters={"artifact": "summary-001"},
    )

    assert request.target == "dashboard"
    assert request.action == "generate"
    assert request.parameters["artifact"] == "summary-001"
    assert request.request_id


def test_execution_result_can_be_created():
    artifact = ArtifactReference(
        artifact_id="dashboard-001",
        artifact_type="dashboard_markdown",
        path="data/dashboard.md",
        producer="dashboard_report",
    )

    result = ExecutionResult(
        success=True,
        message="Dashboard generated",
        artifacts=[artifact],
        metadata={"duration_ms": 12},
    )

    assert result.success is True
    assert result.message == "Dashboard generated"
    assert result.artifacts[0].artifact_id == "dashboard-001"


def test_runtime_event_can_be_created():
    event = RuntimeEvent(
        event_type="ExecutionRequested",
        payload={"target": "dashboard"},
    )

    assert event.event_type == "ExecutionRequested"
    assert event.payload["target"] == "dashboard"
    assert event.event_id
    assert event.timestamp
