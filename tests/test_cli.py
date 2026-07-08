from pathlib import Path

from pipeline_runtime_bridge.cli import main
from pipeline_runtime_bridge.context import load_runtime_context
from pipeline_runtime_bridge.events import read_runtime_events


def test_cli_init_creates_context(tmp_path):
    workspace = tmp_path / "runtime_demo"

    exit_code = main(
        [
            "init",
            "--workspace",
            str(workspace),
            "--pipeline-id",
            "pipeline-cli-test",
            "--session-id",
            "session-cli-test",
        ]
    )

    assert exit_code == 0
    assert (workspace / "runtime_context.json").exists()


def test_cli_context_reads_context(tmp_path):
    workspace = tmp_path / "runtime_demo"

    main(
        [
            "init",
            "--workspace",
            str(workspace),
        ]
    )

    exit_code = main(
        [
            "context",
            "--workspace",
            str(workspace),
        ]
    )

    assert exit_code == 0


def test_cli_register_adds_artifact(tmp_path):
    workspace = tmp_path / "runtime_demo"

    main(["init", "--workspace", str(workspace)])

    exit_code = main(
        [
            "register",
            "--workspace",
            str(workspace),
            "--artifact-id",
            "summary-001",
            "--artifact-type",
            "summary_json",
            "--path",
            "data/summary.json",
            "--producer",
            "summary_engine",
        ]
    )

    assert exit_code == 0
    assert (workspace / "artifact_registry.json").exists()


def test_cli_artifacts_lists_artifacts(tmp_path):
    workspace = tmp_path / "runtime_demo"

    main(["init", "--workspace", str(workspace)])
    main(
        [
            "register",
            "--workspace",
            str(workspace),
            "--artifact-id",
            "summary-001",
            "--artifact-type",
            "summary_json",
            "--path",
            "data/summary.json",
            "--producer",
            "summary_engine",
        ]
    )

    exit_code = main(
        [
            "artifacts",
            "--workspace",
            str(workspace),
        ]
    )

    assert exit_code == 0


def test_cli_route_routes_artifact(tmp_path):
    workspace = tmp_path / "runtime_demo"

    main(["init", "--workspace", str(workspace)])
    main(
        [
            "register",
            "--workspace",
            str(workspace),
            "--artifact-id",
            "summary-001",
            "--artifact-type",
            "summary_json",
            "--path",
            "data/summary.json",
            "--producer",
            "summary_engine",
        ]
    )

    exit_code = main(
        [
            "route",
            "--workspace",
            str(workspace),
            "--artifact-id",
            "summary-001",
            "--target",
            "dashboard",
        ]
    )

    assert exit_code == 0


def test_cli_dispatch_returns_success_for_supported_target(tmp_path):
    workspace = tmp_path / "runtime_demo"

    main(["init", "--workspace", str(workspace)])

    exit_code = main(
        [
            "dispatch",
            "--workspace",
            str(workspace),
            "--target",
            "dashboard",
            "--action",
            "generate",
        ]
    )

    assert exit_code == 0


def test_cli_dispatch_returns_failure_for_unknown_target(tmp_path):
    workspace = tmp_path / "runtime_demo"

    main(["init", "--workspace", str(workspace)])

    exit_code = main(
        [
            "dispatch",
            "--workspace",
            str(workspace),
            "--target",
            "unknown",
        ]
    )

    assert exit_code == 1


def test_cli_execute_route_dispatches_target(tmp_path):
    workspace = tmp_path / "runtime_demo"

    main(["init", "--workspace", str(workspace)])
    main(
        [
            "register",
            "--workspace",
            str(workspace),
            "--artifact-id",
            "summary-001",
            "--artifact-type",
            "summary_json",
            "--path",
            "data/summary.json",
            "--producer",
            "summary_engine",
        ]
    )

    exit_code = main(
        [
            "execute-route",
            "--workspace",
            str(workspace),
            "--artifact-id",
            "summary-001",
            "--target",
            "dashboard",
        ]
    )

    assert exit_code == 0


def test_cli_events_lists_runtime_events(tmp_path):
    workspace = tmp_path / "runtime_demo"

    main(["init", "--workspace", str(workspace)])

    exit_code = main(
        [
            "events",
            "--workspace",
            str(workspace),
        ]
    )

    assert exit_code == 0
    assert (workspace / "runtime_events.jsonl").exists()


def test_cli_register_emits_artifact_registered_event(tmp_path):
    workspace = tmp_path / "runtime_demo"

    main(["init", "--workspace", str(workspace)])
    main(
        [
            "register",
            "--workspace",
            str(workspace),
            "--artifact-id",
            "summary-001",
            "--artifact-type",
            "summary_json",
            "--path",
            "data/summary.json",
            "--producer",
            "summary_engine",
        ]
    )

    context = load_runtime_context(str(workspace))
    events = read_runtime_events(context)

    event_types = [event.event_type for event in events]

    assert "ArtifactRegistered" in event_types
