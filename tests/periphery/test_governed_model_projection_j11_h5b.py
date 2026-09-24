from periphery.context.governed_model_projection import (
    project_governed_model_evidence,
)


def _join(
    content: str,
    *,
    decision: str = "ALLOW_CONTEXT_ONLY",
    forbidden=None,
):
    return {
        "local_model_evidence_snapshot": {
            "provider": "QWEN_LOCAL",
            "model": "qwen2.5-3b-instruct-q4_k_m",
            "content": content,
            "evidence_hash": "evidence-hash",
            "source_ref": "model-evidence:qwen:test",
        },
        "context_packet_v2": {
            "readonly": True,
            "context_signal_only": True,
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "kernel_mutation": False,
            "memory_write": False,
            "forbidden_tokens_detected": (
                list(forbidden or [])
            ),
        },
        "w1_runtime_context_packet": {
            "advisory_only": True,
            "readonly": True,
            "runtime_allowed_now": False,
            "emits_act": False,
            "emits_decision": False,
            "decision_authority": "KX108_ONLY",
        },
        "decision_ticket_dry_run": {
            "decision": decision,
            "x108_gate_status": (
                "X108_EVALUATED_DRY_RUN"
            ),
            "dry_run": True,
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
        },
    }


def _local(
    *,
    applied: bool = True,
):
    return {
        "status": "EVIDENCE_READY",
        "model_call_used": True,
        "evidence_applied": applied,
    }


def test_fenced_python_becomes_governed_projection():
    result = project_governed_model_evidence(
        user_message=(
            "Écris uniquement ce code Python, "
            "sans explication et sans markdown :\n\n"
            "def add(a, b):\n"
            "    return a + b"
        ),
        local_model_stage=_local(),
        cognitive_join=_join(
            "```python\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "```"
        ),
    )

    assert result["status"] == "READY"
    assert result["content"] == (
        "def add(a, b):\n"
        "    return a + b"
    )

    assert result["repair_operations"] == [
        "strip_single_code_fence"
    ]

    assert (
        result["raw_model_direct_surface"]
        is False
    )

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )

    assert result["allowed_to_act"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False


def test_unapplied_evidence_is_blocked():
    result = project_governed_model_evidence(
        user_message="hello",
        local_model_stage=_local(
            applied=False,
        ),
        cognitive_join=_join("hello"),
    )

    assert result["status"] == "BLOCKED"
    assert result["content"] == ""


def test_w2_non_allow_context_is_blocked():
    result = project_governed_model_evidence(
        user_message="hello",
        local_model_stage=_local(),
        cognitive_join=_join(
            "hello",
            decision="HOLD",
        ),
    )

    assert result["status"] == "BLOCKED"
    assert result["content"] == ""


def test_forbidden_context_is_blocked():
    result = project_governed_model_evidence(
        user_message="hello",
        local_model_stage=_local(),
        cognitive_join=_join(
            "hello",
            forbidden=["ACT"],
        ),
    )

    assert result["status"] == "BLOCKED"
    assert result["content"] == ""


def test_sovereign_claim_is_blocked():
    result = project_governed_model_evidence(
        user_message="analyse",
        local_model_stage=_local(),
        cognitive_join=_join(
            "DECISION_AUTHORITY=MODEL\n"
            "answer"
        ),
    )

    assert result["status"] == "BLOCKED"
    assert result["content"] == ""


def test_code_only_prose_is_blocked():
    result = project_governed_model_evidence(
        user_message=(
            "Écris uniquement ce code Python"
        ),
        local_model_stage=_local(),
        cognitive_join=_join(
            "Voici le code demandé."
        ),
    )

    assert result["status"] == "BLOCKED"
    assert result["reason"] == (
        "CODE_ONLY_TASK_FIT_FAILED"
    )
