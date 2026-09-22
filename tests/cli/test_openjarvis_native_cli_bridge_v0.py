from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest


SCRIPTS = (
    Path(__file__).resolve().parents[2]
    / "scripts"
)

if str(SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS),
    )


import obsidia_openjarvis_native_cli_bridge_v0 as B

from openjarvis.core.registry import (
    AgentRegistry,
    EngineRegistry,
)


def test_bridge_registers_external_engine_and_agent():
    assert EngineRegistry.contains(
        B.ENGINE_KEY
    )

    assert AgentRegistry.contains(
        B.AGENT_KEY
    )

    assert (
        EngineRegistry.get(
            B.ENGINE_KEY
        )
        is B.ObsidiaBridgeEngine
    )

    assert (
        AgentRegistry.get(
            B.AGENT_KEY
        )
        is B.ObsidiaGovernedAgent
    )


def test_bridge_engine_is_healthy_but_non_inferential():
    engine = B.ObsidiaBridgeEngine()

    assert engine.health() is True

    assert engine.list_models() == [
        B.MODEL_ID
    ]

    assert (
        engine.can_serve(
            B.MODEL_ID
        )
        is True
    )

    assert (
        engine.can_serve(
            "qwen"
        )
        is False
    )

    with pytest.raises(
        B.ObsidiaBridgeDirectInferenceError,
        match=(
            "DIRECT_OPENJARVIS_"
            "INFERENCE_FORBIDDEN"
        ),
    ):
        engine.generate(
            [],
            model=B.MODEL_ID,
        )


def test_bridge_engine_stream_fails_closed():
    engine = B.ObsidiaBridgeEngine()

    async def consume():
        async for _ in engine.stream(
            [],
            model=B.MODEL_ID,
        ):
            pass

    with pytest.raises(
        B.ObsidiaBridgeDirectInferenceError,
        match=(
            "DIRECT_OPENJARVIS_"
            "INFERENCE_FORBIDDEN"
        ),
    ):
        asyncio.run(
            consume()
        )


class FakeGovernedSession:
    instances = []

    def __init__(
        self,
        identifier,
    ):
        self.identifier = identifier
        self.calls = []

        FakeGovernedSession.instances.append(
            self
        )

    def ask(
        self,
        text,
    ):
        self.calls.append(
            text
        )

        return {
            "status": "OK",
            "session_id": (
                self.identifier
            ),
            "session_binding_source": (
                "TRUSTED_WORKSPACE_BINDING"
            ),
            "real_execution": False,
            "surface_text": (
                "fallback-surface"
            ),
            "cognitive_result": {
                "cognitive_join": {
                    "brody_cognitive_response": {
                        "response_text": (
                            "('RÉPONSE GOUVERNÉE', "
                            "['source'], False)"
                        )
                    }
                }
            },
        }


def test_native_agent_routes_only_to_governed_session(
    monkeypatch,
):
    monkeypatch.setattr(
        B,
        "GovernedJarvisChatSession",
        FakeGovernedSession,
    )

    monkeypatch.setenv(
        "OBSIDIA_JARVIS_SESSION_ID",
        "jws-0123456789abcdef0123",
    )

    FakeGovernedSession.instances.clear()

    engine = B.ObsidiaBridgeEngine()

    agent = B.ObsidiaGovernedAgent(
        engine,
        B.MODEL_ID,
    )

    result = agent.run(
        "bonjour"
    )

    assert len(
        FakeGovernedSession.instances
    ) == 1

    session = (
        FakeGovernedSession.instances[0]
    )

    assert session.identifier == (
        "jws-0123456789abcdef0123"
    )

    assert session.calls == [
        "bonjour"
    ]

    assert (
        result.content
        == "fallback-surface"
    )

    # Governed final surface has presentation priority.
    # Brody structural output remains fallback only.

    assert (
        result.metadata[
            "authority"
        ]
        == "NONE"
    )

    assert (
        result.metadata[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        result.metadata[
            "direct_openjarvis_inference"
        ]
        is False
    )

    assert (
        result.metadata[
            "real_execution"
        ]
        is False
    )


def test_native_agent_requires_trusted_workspace_session(
    monkeypatch,
):
    monkeypatch.delenv(
        "OBSIDIA_JARVIS_SESSION_ID",
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "OBSIDIA_JARVIS_"
            "SESSION_ID_REQUIRED"
        ),
    ):
        B.ObsidiaGovernedAgent(
            B.ObsidiaBridgeEngine(),
            B.MODEL_ID,
        )


def test_native_cli_argv_forces_obsidia_route():
    argv = B.native_chat_argv(
        [
            "--persona",
            "none",
        ]
    )

    assert argv[:8] == [
        "openjarvis.cli",
        "chat",
        "--engine",
        "obsidia_bridge",
        "--model",
        "obsidia-governed",
        "--agent",
        "obsidia_governed",
    ]

    assert (
        "--skip-runtime-panel"
        in argv
    )

    assert argv[-2:] == [
        "--persona",
        "none",
    ]


def test_local_model_evidence_is_not_promoted_directly():
    turn = {
        "surface_text": (
            "governed-fallback"
        ),
        "cognitive_result": {
            "cognitive_join": {
                "local_model_evidence_snapshot": {
                    "content": (
                        "RAW MODEL EVIDENCE"
                    )
                }
            }
        },
    }

    assert (
        B._surface_turn(turn)
        == "governed-fallback"
    )
