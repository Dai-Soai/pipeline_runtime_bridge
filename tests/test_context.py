from pathlib import Path

import pytest

from pipeline_runtime_bridge.context import (
    CONTEXT_FILENAME,
    create_runtime_context,
    get_context_path,
    load_runtime_context,
    save_runtime_context,
)


def test_create_runtime_context_creates_directories(tmp_path):
    workspace = tmp_path / "runtime_demo"

    context = create_runtime_context(
        workspace=str(workspace),
        pipeline_id="pipeline-test",
        session_id="session-test",
        metadata={"mode": "test"},
    )

    assert context.session_id == "session-test"
    assert context.pipeline_id == "pipeline-test"
    assert Path(context.workspace).exists()
    assert Path(context.artifact_dir).exists()
    assert Path(context.output_dir).exists()
    assert context.metadata["mode"] == "test"


def test_save_runtime_context_writes_json_file(tmp_path):
    workspace = tmp_path / "runtime_demo"
    context = create_runtime_context(workspace=str(workspace))

    context_path = save_runtime_context(context)

    assert context_path.exists()
    assert context_path.name == CONTEXT_FILENAME


def test_load_runtime_context_reads_saved_context(tmp_path):
    workspace = tmp_path / "runtime_demo"
    context = create_runtime_context(
        workspace=str(workspace),
        pipeline_id="pipeline-load-test",
        session_id="session-load-test",
    )
    save_runtime_context(context)

    loaded = load_runtime_context(str(workspace))

    assert loaded.session_id == "session-load-test"
    assert loaded.pipeline_id == "pipeline-load-test"
    assert loaded.workspace == str(workspace)


def test_get_context_path_returns_expected_path(tmp_path):
    workspace = tmp_path / "runtime_demo"

    context_path = get_context_path(str(workspace))

    assert context_path == workspace / CONTEXT_FILENAME


def test_load_runtime_context_raises_for_missing_file(tmp_path):
    workspace = tmp_path / "missing_runtime_demo"

    with pytest.raises(FileNotFoundError):
        load_runtime_context(str(workspace))
