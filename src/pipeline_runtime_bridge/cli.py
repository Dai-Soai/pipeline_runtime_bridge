from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from pipeline_runtime_bridge.context import (
    create_runtime_context,
    get_context_path,
    load_runtime_context,
    save_runtime_context,
)
from pipeline_runtime_bridge.contract import ArtifactReference, ExecutionRequest
from pipeline_runtime_bridge.dispatcher import dispatch_request, execute_route
from pipeline_runtime_bridge.events import emit_runtime_event, read_runtime_events
from pipeline_runtime_bridge.report import build_runtime_report, write_runtime_report
from pipeline_runtime_bridge.router import (
    list_artifacts,
    register_artifact,
    route_artifact,
)


def print_json(payload: dict | list) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_init(args: argparse.Namespace) -> int:
    context = create_runtime_context(
        workspace=args.workspace,
        pipeline_id=args.pipeline_id,
        session_id=args.session_id,
        metadata={"created_by": "runtime-bridge-cli"},
    )
    context_path = save_runtime_context(context)

    emit_runtime_event(
        context,
        "RuntimeStarted",
        {
            "session_id": context.session_id,
            "pipeline_id": context.pipeline_id,
            "context_path": str(context_path),
        },
    )

    print_json(
        {
            "status": "initialized",
            "context": asdict(context),
            "context_path": str(context_path),
        }
    )
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    context = load_runtime_context(args.workspace)

    print_json(
        {
            "context_path": str(get_context_path(args.workspace)),
            "context": asdict(context),
        }
    )
    return 0


def cmd_register(args: argparse.Namespace) -> int:
    context = load_runtime_context(args.workspace)

    artifact = ArtifactReference(
        artifact_id=args.artifact_id,
        artifact_type=args.artifact_type,
        path=args.path,
        producer=args.producer,
        metadata={"registered_by": "runtime-bridge-cli"},
    )

    registered = register_artifact(context, artifact)

    emit_runtime_event(
        context,
        "ArtifactRegistered",
        {
            "artifact_id": registered.artifact_id,
            "artifact_type": registered.artifact_type,
            "producer": registered.producer,
        },
    )

    print_json(
        {
            "status": "registered",
            "artifact": asdict(registered),
        }
    )
    return 0


def cmd_artifacts(args: argparse.Namespace) -> int:
    context = load_runtime_context(args.workspace)
    artifacts = list_artifacts(context)

    print_json([asdict(artifact) for artifact in artifacts])
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    context = load_runtime_context(args.workspace)

    route = route_artifact(
        context,
        artifact_id=args.artifact_id,
        target=args.target,
    )

    emit_runtime_event(
        context,
        "ArtifactRouted",
        {
            "artifact_id": args.artifact_id,
            "target": args.target,
        },
    )

    print_json(route)
    return 0


def cmd_dispatch(args: argparse.Namespace) -> int:
    context = load_runtime_context(args.workspace)

    request = ExecutionRequest(
        target=args.target,
        action=args.action,
        parameters={"source": "runtime-bridge-cli"},
    )

    emit_runtime_event(
        context,
        "ExecutionRequested",
        {
            "request_id": request.request_id,
            "target": request.target,
            "action": request.action,
        },
    )

    result = dispatch_request(context, request)

    emit_runtime_event(
        context,
        "ExecutionCompleted" if result.success else "RuntimeFailed",
        {
            "request_id": request.request_id,
            "success": result.success,
            "message": result.message,
        },
    )

    print_json(asdict(result))
    return 0 if result.success else 1


def cmd_execute_route(args: argparse.Namespace) -> int:
    context = load_runtime_context(args.workspace)

    emit_runtime_event(
        context,
        "ArtifactRouted",
        {
            "artifact_id": args.artifact_id,
            "target": args.target,
        },
    )

    result = execute_route(
        context,
        artifact_id=args.artifact_id,
        target=args.target,
    )

    emit_runtime_event(
        context,
        "ExecutionCompleted" if result.success else "RuntimeFailed",
        {
            "success": result.success,
            "message": result.message,
        },
    )

    print_json(asdict(result))
    return 0 if result.success else 1


def cmd_events(args: argparse.Namespace) -> int:
    context = load_runtime_context(args.workspace)
    events = read_runtime_events(context)

    print_json([asdict(event) for event in events])
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="runtime-bridge",
        description="Pipeline Runtime Bridge CLI",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a runtime workspace")
    init_parser.add_argument("--workspace", required=True)
    init_parser.add_argument("--pipeline-id", default="pipeline-demo")
    init_parser.add_argument("--session-id", default=None)
    init_parser.set_defaults(func=cmd_init)

    context_parser = subparsers.add_parser("context", help="Show runtime context")
    context_parser.add_argument("--workspace", required=True)
    context_parser.set_defaults(func=cmd_context)

    register_parser = subparsers.add_parser("register", help="Register an artifact")
    register_parser.add_argument("--workspace", required=True)
    register_parser.add_argument("--artifact-id", required=True)
    register_parser.add_argument("--artifact-type", required=True)
    register_parser.add_argument("--path", required=True)
    register_parser.add_argument("--producer", required=True)
    register_parser.set_defaults(func=cmd_register)

    artifacts_parser = subparsers.add_parser(
        "artifacts", help="List registered artifacts"
    )
    artifacts_parser.add_argument("--workspace", required=True)
    artifacts_parser.set_defaults(func=cmd_artifacts)

    route_parser = subparsers.add_parser("route", help="Route an artifact to a target")
    route_parser.add_argument("--workspace", required=True)
    route_parser.add_argument("--artifact-id", required=True)
    route_parser.add_argument("--target", required=True)
    route_parser.set_defaults(func=cmd_route)

    dispatch_parser = subparsers.add_parser(
        "dispatch", help="Dispatch a runtime request"
    )
    dispatch_parser.add_argument("--workspace", required=True)
    dispatch_parser.add_argument("--target", required=True)
    dispatch_parser.add_argument("--action", default="run")
    dispatch_parser.set_defaults(func=cmd_dispatch)

    execute_route_parser = subparsers.add_parser(
        "execute-route",
        help="Route an artifact and dispatch the target",
    )
    execute_route_parser.add_argument("--workspace", required=True)
    execute_route_parser.add_argument("--artifact-id", required=True)
    execute_route_parser.add_argument("--target", required=True)
    execute_route_parser.set_defaults(func=cmd_execute_route)

    events_parser = subparsers.add_parser("events", help="Show runtime events")
    events_parser.add_argument("--workspace", required=True)
    events_parser.set_defaults(func=cmd_events)

    report_parser = subparsers.add_parser("report", help="Build runtime JSON report")
    report_parser.add_argument("--workspace", required=True)
    report_parser.add_argument("--write", action="store_true")
    report_parser.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def cmd_report(args: argparse.Namespace) -> int:
    context = load_runtime_context(args.workspace)

    if args.write:
        report_path = write_runtime_report(context)
        print_json(
            {
                "status": "written",
                "report_path": str(report_path),
                "report": build_runtime_report(context),
            }
        )
        return 0

    print_json(build_runtime_report(context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
