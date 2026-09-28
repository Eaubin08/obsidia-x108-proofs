"""Minimal governed OpenJarvis route shim preserved for Obsidia.

This is a delta-only bridge, not the upstream OpenJarvis server.  It keeps
only the model-surface lock and governed stream dispatch invariant needed by
Obsidia integration tests.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from openjarvis.server.models import ChatCompletionRequest


router = APIRouter()


def _server_agent_model_allowlist(agent: Any) -> tuple[str, ...]:
    if agent is None:
        return ()

    raw = getattr(agent, "server_model_allowlist", ())

    if isinstance(raw, str):
        raw = (raw,)

    try:
        values = tuple(raw or ())
    except TypeError:
        return ()

    result: list[str] = []

    for value in values:
        item = str(value or "").strip()
        if item and item not in result:
            result.append(item)

    return tuple(result)


async def _handle_agent_stream(*args: Any, **kwargs: Any) -> Any:
    raise NotImplementedError("OpenJarvis upstream agent stream is not bundled")


async def _handle_stream(*args: Any, **kwargs: Any) -> Any:
    raise NotImplementedError("OpenJarvis upstream direct stream is not bundled")


@router.post("/v1/chat/completions")
async def chat_completions(
    request_body: ChatCompletionRequest,
    request: Request,
) -> Any:
    agent = getattr(request.app.state, "agent", None)
    model = request_body.model

    agent_model_allowlist = _server_agent_model_allowlist(agent)

    if agent_model_allowlist and model not in agent_model_allowlist:
        raise HTTPException(
            status_code=400,
            detail="MODEL_NOT_AVAILABLE_FOR_ACTIVE_AGENT",
        )

    use_server_agent = (
        agent is not None
        and not request_body.tools
        and (
            not request_body.stream
            or bool(getattr(agent, "_tools", None))
            or bool(getattr(agent, "force_server_agent_stream", False))
        )
    )

    if request_body.stream and use_server_agent:
        return await _handle_agent_stream(
            agent,
            model,
            request_body,
            None,
            trace_store=getattr(request.app.state, "trace_store", None),
            bus=getattr(request.app.state, "bus", None),
            memory_service=getattr(request.app.state, "memory_service", None),
        )

    if request_body.stream:
        return await _handle_stream(
            getattr(request.app.state, "engine", None),
            model,
            request_body,
            None,
            trace_store=getattr(request.app.state, "trace_store", None),
            app_config=getattr(request.app.state, "config", None),
            bus=getattr(request.app.state, "bus", None),
            memory_service=getattr(request.app.state, "memory_service", None),
        )

    raise HTTPException(
        status_code=501,
        detail="OPENJARVIS_BRIDGE_DELTA_ONLY_STREAM_TEST_SURFACE",
    )
