import pytest

from pipeline_runtime_bridge.context import create_runtime_context
from pipeline_runtime_bridge.events import (
    EVENT_LOG_FILENAME,
    EVENT_TYPES,
    append_runtime_event,
    create_runtime_event,
    emit_runtime_event,
    get_event_log_path,
    is_supported_event_type,
    read_runtime_events,
)


def test_event_types_contains_expected_events():
    assert "RuntimeStarted" in EVENT_TYPES
    assert "ExecutionRequested" in EVENT_TYPES
    assert "ArtifactRouted" in EVENT_TYPES
    assert "ExecutionCompleted" in EVENT_TYPES
    assert "RuntimeFinished" in EVENT_TYPES
    assert "RuntimeFailed" in EVENT_TYPES


def test_is_supported_event_type_returns_true_for_known_event():
    assert is_supported_event_type("RuntimeStarted") is True


def test_is_supported_event_type_returns_false_for_unknown_event():
    assert is_supported_event_type("UnknownEvent") is False


def test_get_event_log_path(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    event_log_path = get_event_log_path(context)

    assert event_log_path.name == EVENT_LOG_FILENAME
    assert event_log_path.parent == tmp_path / "runtime_demo"


def test_create_runtime_event_returns_event():
    event = create_runtime_event(
        event_type="ExecutionRequested",
        payload={"target": "dashboard"},
    )

    assert event.event_type == "ExecutionRequested"
    assert event.payload["target"] == "dashboard"
    assert event.event_id
    assert event.timestamp


def test_create_runtime_event_raises_for_unknown_event():
    with pytest.raises(ValueError):
        create_runtime_event("UnknownEvent")


def test_append_runtime_event_writes_jsonl(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))
    event = create_runtime_event(
        event_type="RuntimeStarted",
        payload={"pipeline_id": "pipeline-test"},
    )

    log_path = append_runtime_event(context, event)

    assert log_path.exists()
    assert log_path.read_text(encoding="utf-8").strip()


def test_read_runtime_events_returns_empty_list_when_missing(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    events = read_runtime_events(context)

    assert events == []


def test_read_runtime_events_reads_written_events(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    event = create_runtime_event(
        event_type="ExecutionCompleted",
        payload={"success": True},
    )
    append_runtime_event(context, event)

    events = read_runtime_events(context)

    assert len(events) == 1
    assert events[0].event_type == "ExecutionCompleted"
    assert events[0].payload["success"] is True


def test_emit_runtime_event_creates_and_appends_event(tmp_path):
    context = create_runtime_context(workspace=str(tmp_path / "runtime_demo"))

    emitted = emit_runtime_event(
        context=context,
        event_type="RuntimeFinished",
        payload={"status": "ok"},
    )

    events = read_runtime_events(context)

    assert emitted.event_type == "RuntimeFinished"
    assert len(events) == 1
    assert events[0].payload["status"] == "ok"
