import json

from pipeline_runtime_bridge.contract import ArtifactReference
from pipeline_runtime_bridge.context import create_runtime_context
from pipeline_runtime_bridge.events import emit_runtime_event
from pipeline_runtime_bridge.report import (
    RUNTIME_REPORT_FILENAME,
    build_runtime_report,
    get_runtime_report_path,
    write_runtime_report,
)
from pipeline_runtime_bridge.router import register_artifact


def test_build_runtime_report_returns_empty_status(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    report = build_runtime_report(context)

    assert report["status"] == "empty"
    assert report["summary"]["artifact_count"] == 0
    assert report["summary"]["event_count"] == 0


def test_build_runtime_report_counts_artifacts_and_events(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    artifact = ArtifactReference(
        artifact_id="summary-001",
        artifact_type="summary_json",
        path="data/summary.json",
        producer="summary_engine",
    )
    register_artifact(context, artifact)
    emit_runtime_event(context, "RuntimeStarted", {"pipeline_id": "pipeline-test"})

    report = build_runtime_report(context)

    assert report["status"] == "running"
    assert report["summary"]["artifact_count"] == 1
    assert report["summary"]["event_count"] == 1
    assert "summary_json" in report["summary"]["artifact_types"]
    assert "RuntimeStarted" in report["summary"]["event_types"]


def test_build_runtime_report_status_completed(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    emit_runtime_event(context, "ExecutionCompleted", {"success": True})

    report = build_runtime_report(context)

    assert report["status"] == "completed"


def test_build_runtime_report_status_failed(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    emit_runtime_event(context, "ExecutionCompleted", {"success": True})
    emit_runtime_event(context, "RuntimeFailed", {"success": False})

    report = build_runtime_report(context)

    assert report["status"] == "failed"


def test_get_runtime_report_path(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    report_path = get_runtime_report_path(context)

    assert report_path.name == RUNTIME_REPORT_FILENAME
    assert report_path.parent == tmp_path / "runtime_demo" / "output"


def test_write_runtime_report_writes_json_file(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    emit_runtime_event(context, "RuntimeStarted", {"pipeline_id": "pipeline-test"})

    report_path = write_runtime_report(context)

    assert report_path.exists()

    data = json.loads(report_path.read_text(encoding="utf-8"))

    assert data["summary"]["event_count"] == 1
    assert data["events"][0]["event_type"] == "RuntimeStarted"
