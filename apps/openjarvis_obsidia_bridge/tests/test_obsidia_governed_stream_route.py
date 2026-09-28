from __future__ import annotations

import asyncio
from types import SimpleNamespace

from openjarvis.server import routes
from openjarvis.server.models import (
    ChatCompletionRequest,
    ChatMessage,
)


class GovernedAgentWithoutTools:
    _tools = []
    force_server_agent_stream = True


def test_stream_true_capability_uses_server_agent(monkeypatch):
    calls = {
        "agent": 0,
        "direct": 0,
    }

    async def fake_agent_stream(*args, **kwargs):
        calls["agent"] += 1
        return "GOVERNED_AGENT_STREAM"

    async def forbidden_direct_stream(*args, **kwargs):
        calls["direct"] += 1
        raise AssertionError(
            "DIRECT_ENGINE_STREAM_MUST_NOT_BE_USED"
        )

    monkeypatch.setattr(
        routes,
        "_handle_agent_stream",
        fake_agent_stream,
    )

    monkeypatch.setattr(
        routes,
        "_handle_stream",
        forbidden_direct_stream,
    )

    state = SimpleNamespace(
        engine=object(),
        agent=GovernedAgentWithoutTools(),
        config=None,
        memory_backend=None,
        memory_service=None,
        trace_store=None,
        bus=None,
    )

    request = SimpleNamespace(
        app=SimpleNamespace(
            state=state,
        )
    )

    body = ChatCompletionRequest(
        model="obsidia-governed",
        messages=[
            ChatMessage(
                role="user",
                content="bonjour",
            )
        ],
        stream=True,
    )

    result = asyncio.run(
        routes.chat_completions(
            body,
            request,
        )
    )

    assert result == "GOVERNED_AGENT_STREAM"
    assert calls == {
        "agent": 1,
        "direct": 0,
    }
