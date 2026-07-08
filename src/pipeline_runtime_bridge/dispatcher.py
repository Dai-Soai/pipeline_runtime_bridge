from __future__ import annotations

from pipeline_runtime_bridge.contract import (
    ArtifactReference,
    ExecutionRequest,
    ExecutionResult,
    RuntimeContext,
)
from pipeline_runtime_bridge.router import register_artifact, route_artifact


SUPPORTED_TARGETS = {
    "dashboard",
    "audit",
    "router",
    "summary",
}


def is_supported_target(target: str) -> bool:
    return target in SUPPORTED_TARGETS


def mock_execute(
    context: RuntimeContext,
    request: ExecutionRequest,
) -> ExecutionResult:
    if not is_supported_target(request.target):
        return ExecutionResult(
            success=False,
            message=f"Unsupported target: {request.target}",
            metadata={
                "request_id": request.request_id,
                "target": request.target,
                "action": request.action,
            },
        )

    artifact = ArtifactReference(
        artifact_id=f"{request.target}-{request.request_id}",
        artifact_type=f"{request.target}_result",
        path=f"{context.output_dir}/{request.target}_{request.request_id}.json",
        producer="pipeline_runtime_bridge",
        metadata={
            "request_id": request.request_id,
            "target": request.target,
            "action": request.action,
            "mock": True,
        },
    )

    register_artifact(context, artifact)

    return ExecutionResult(
        success=True,
        message=f"Mock execution completed for target: {request.target}",
        artifacts=[artifact],
        metadata={
            "request_id": request.request_id,
            "target": request.target,
            "action": request.action,
            "mock": True,
        },
    )


def dispatch_request(
    context: RuntimeContext,
    request: ExecutionRequest,
) -> ExecutionResult:
    return mock_execute(context, request)


def execute_route(
    context: RuntimeContext,
    artifact_id: str,
    target: str,
) -> ExecutionResult:
    route = route_artifact(context, artifact_id=artifact_id, target=target)

    request = ExecutionRequest(
        target=target,
        action="route",
        parameters={
            "artifact_id": artifact_id,
            "route": route,
        },
    )

    return dispatch_request(context, request)
