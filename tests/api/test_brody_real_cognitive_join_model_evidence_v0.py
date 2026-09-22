from __future__ import annotations

import hashlib

from apps.obsidia_api.brody_real_cognitive_join import (
    run_real_cognitive_join,
)


def _sha(value: str) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8",
            errors="replace",
        )
    ).hexdigest()


def _evidence(
    query: str,
    *,
    content: str = "Local model evidence.",
) -> dict:
    return {
        "provider": "QWEN_LOCAL",
        "model": "qwen2.5-3b-instruct-q4_k_m",
        "result_kind": "EVIDENCE",

        "content": content,

        "input_hash": _sha(query),
        "evidence_hash": _sha(content),

        "readonly": True,
        "decision_authority": "KX108_ONLY",

        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,

        "allowed_to_decide": False,
        "allowed_to_act": False,

        "emits_act": False,
        "emits_verdict": False,

        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "real_action": False,
    }


def test_model_evidence_enters_context_before_w1_w2():
    query = (
        "analyse ce probleme complexe"
    )

    evidence = _evidence(
        query,
        content=(
            "The local model proposes a bounded "
            "readonly analytical hypothesis."
        ),
    )

    result = run_real_cognitive_join(
        message=query,
        language="fr",
        session_id="model-evidence-valid",
        precomputed_model_evidence=evidence,
    )

    assert (
        result["status"]
        == "READY_SHADOW_READONLY"
    )

    assert (
        result[
            "local_model_evidence_applied"
        ]
        is True
    )

    assert (
        result[
            "local_model_evidence_status"
        ]
        == "ACCEPTED_READONLY_EVIDENCE"
    )

    assert (
        result["components"][
            "W4B_LOCAL_MODEL_EVIDENCE"
        ]
        == "READY:EVIDENCE:QWEN_LOCAL"
    )

    context = result[
        "context_packet_v2"
    ]

    assert any(
        item.startswith(
            "MODEL_EVIDENCE:QWEN_LOCAL:"
        )
        for item in context[
            "context_items"
        ]
    )

    assert any(
        ref.startswith(
            "model-evidence:qwen_local:"
        )
        for ref in context[
            "source_refs"
        ]
    )

    assert (
        result["components"][
            "W1_RUNTIME_JOIN"
        ]
        == "READY"
    )

    assert (
        result["components"][
            "W2_X108_ADMISSION"
        ]
        == "READY:DRY_RUN"
    )

    assert (
        result["kx108_admission"]
        == "DRY_RUN"
    )

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        result["real_execution"]
        is False
    )


def test_model_evidence_input_hash_mismatch_is_rejected():
    query = "request A"

    evidence = _evidence(
        "request B",
    )

    result = run_real_cognitive_join(
        message=query,
        language="fr",
        session_id="model-evidence-mismatch",
        precomputed_model_evidence=evidence,
    )

    assert (
        result[
            "local_model_evidence_applied"
        ]
        is False
    )

    component = result[
        "components"
    ][
        "W4B_LOCAL_MODEL_EVIDENCE"
    ]

    assert (
        "INPUT_HASH_MISMATCH"
        in component
    )

    assert any(
        "W4B_LOCAL_MODEL_EVIDENCE"
        in error
        and "INPUT_HASH_MISMATCH"
        in error
        for error in result[
            "errors"
        ]
    )


def test_sovereign_model_evidence_is_rejected():
    query = "analyse ceci"

    evidence = _evidence(
        query,
    )

    evidence[
        "allowed_to_decide"
    ] = True

    result = run_real_cognitive_join(
        message=query,
        language="fr",
        session_id="model-evidence-sovereign",
        precomputed_model_evidence=evidence,
    )

    assert (
        result[
            "local_model_evidence_applied"
        ]
        is False
    )

    assert any(
        "ALLOWED_TO_DECIDE_MUST_BE_FALSE"
        in error
        for error in result[
            "errors"
        ]
    )


def test_model_evidence_cannot_change_kx_authority():
    query = "analyse ceci"

    evidence = _evidence(
        query,
    )

    result = run_real_cognitive_join(
        message=query,
        language="fr",
        session_id="model-evidence-kx",
        precomputed_model_evidence=evidence,
    )

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        result[
            "context_packet_v2"
        ][
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        result[
            "decision_ticket_dry_run"
        ]
        is not None
    )

    assert (
        result[
            "allowed_to_decide"
        ]
        is False
    )

    assert (
        result[
            "allowed_to_act"
        ]
        is False
    )
