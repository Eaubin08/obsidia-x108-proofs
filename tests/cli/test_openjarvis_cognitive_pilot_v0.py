from __future__ import annotations

import os

import pytest


SOURCE = os.environ.get(
    "OBSIDIA_OPENJARVIS_SOURCE",
    "",
)

COMMIT = os.environ.get(
    "OBSIDIA_OPENJARVIS_COMMIT",
    "",
)


def _adapter():
    if not SOURCE or not COMMIT:
        pytest.skip(
            "OpenJarvis pin not configured"
        )

    from scripts import obsidia_openjarvis_adapter_v0 as O

    return (
        O.OpenJarvisObsidiaCognitivePilotAdapter(
            source_root=SOURCE,
            expected_commit=COMMIT,
        )
    )


def test_cognitive_pilot_rejects_policy_expansion():
    adapter = _adapter()

    for forbidden in (
        "allow_local_model",
        "model",
        "provider",
        "authority",
        "tool",
    ):
        out = adapter.execute(
            capability_id=(
                "OPENJARVIS_OBSIDIA_COGNITIVE_PILOT"
            ),
            payload={
                "input_text": "bonjour",
                forbidden: True,
            },
        )

        assert (
            out["status"]
            == "PAYLOAD_SCOPE_NOT_ALLOWED"
        )

        assert (
            forbidden
            in out["unknown_fields"]
        )

        assert (
            out["is_execution_authority"]
            is False
        )

        assert (
            out["is_kx_authority"]
            is False
        )


def test_cognitive_pilot_rejects_wrong_capability():
    adapter = _adapter()

    out = adapter.execute(
        capability_id=(
            "OPENJARVIS_OBSIDIA_SELF_BUILD_PILOT_SHADOW"
        ),
        payload={
            "input_text": "bonjour"
        },
    )

    assert (
        out["status"]
        == "CAPABILITY_NOT_ALLOWED"
    )


def test_real_openjarvis_cognitive_pilot_single_bound_tool(
    monkeypatch,
):
    adapter = _adapter()

    import scripts.obsidia_cognitive_ingress_v0 as C

    calls = []

    def fake_ingress(
        *,
        text,
        session_id,
        memory_index=None,
        allow_local_model=False,
    ):
        calls.append(
            {
                "text": text,
                "session_id": session_id,
                "allow_local_model": (
                    allow_local_model
                ),
            }
        )

        return {
            "next_stage": (
                "LOCAL_STACK_RESULT"
            ),

            "kx108_admission": "DRY_RUN",

            "local_model_stage": {
                "attempted": False,
                "model_call_used": False,
                "status": "SKIPPED",
                "finish_reason": None,
                "evidence_applied": False,
            },

            "route_receipt": {
                "result_status": (
                    "LOCAL_STACK_NO_LLM"
                ),
                "model_call_used": False,
            },

            "real_execution": False,
        }

    monkeypatch.setattr(
        C,
        "run_cognitive_ingress",
        fake_ingress,
    )

    out = adapter.execute(
        capability_id=(
            "OPENJARVIS_OBSIDIA_COGNITIVE_PILOT"
        ),
        payload={
            "input_text": (
                "explique la chaine cognitive"
            )
        },
    )

    assert (
        out["status"]
        == "OPENJARVIS_OBSIDIA_COGNITIVE_PILOT_OK"
    )

    assert len(calls) == 1

    call = calls[0]

    assert (
        call["text"]
        == "explique la chaine cognitive"
    )

    # This is bound by the integration,
    # not by OpenJarvis tool parameters.
    assert (
        call["allow_local_model"]
        is True
    )

    assert (
        call["session_id"]
        == out["bound_session_id"]
    )

    assert (
        call["session_id"]
        .startswith("ojc-")
    )

    assert (
        out["agent_class"]
        == "OrchestratorAgent"
    )

    assert (
        out["engine_calls"]
        == 2
    )

    assert (
        out["turns"]
        == 2
    )

    assert (
        out["tool_results"]
        == 1
    )

    assert (
        out["available_tool_count"]
        == 1
    )

    assert out["available_tools"] == [
        "obsidia_cognitive_query"
    ]

    assert (
        out["tool_name"]
        == "obsidia_cognitive_query"
    )

    assert (
        out["tool_success"]
        is True
    )

    assert (
        out["openjarvis_real_model_enabled"]
        is False
    )

    assert (
        out["obsidia_model_policy_enabled"]
        is True
    )

    assert (
        out["external_runtime_authority"]
        == "NONE"
    )

    assert (
        out["is_execution_authority"]
        is False
    )

    assert (
        out["is_kx_authority"]
        is False
    )

    assert (
        out["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        out["scope_expanded"]
        is False
    )

    assert (
        out["memory_written"]
        is False
    )

    assert (
        out["source_mutated"]
        is False
    )

    assert (
        out["shell_tool_enabled"]
        is False
    )

    assert (
        out["file_write_tool_enabled"]
        is False
    )

    assert (
        out["git_commit_tool_enabled"]
        is False
    )


def test_cognitive_pilot_does_not_expose_selfbuild_tool(
    monkeypatch,
):
    adapter = _adapter()

    import scripts.obsidia_cognitive_ingress_v0 as C

    monkeypatch.setattr(
        C,
        "run_cognitive_ingress",
        lambda **kwargs: {
            "next_stage": "LOCAL_STACK_RESULT",
            "kx108_admission": "DRY_RUN",
            "local_model_stage": {
                "attempted": False,
                "model_call_used": False,
                "status": "SKIPPED",
                "finish_reason": None,
                "evidence_applied": False,
            },
            "route_receipt": {
                "result_status": (
                    "LOCAL_STACK_NO_LLM"
                )
            },
            "real_execution": False,
        },
    )

    out = adapter.execute(
        capability_id=(
            "OPENJARVIS_OBSIDIA_COGNITIVE_PILOT"
        ),
        payload={
            "input_text": "bonjour"
        },
    )

    assert (
        "obsidia_self_build_phase1"
        not in out["available_tools"]
    )

    assert out["available_tools"] == [
        "obsidia_cognitive_query"
    ]
