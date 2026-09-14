from apps.obsidia_api.runtime_evidence_receipt import (
    build_runtime_evidence_receipt,
    verify_runtime_evidence_receipt,
)


def test_runtime_evidence_receipt_readonly():
    r = build_runtime_evidence_receipt(
        source="BRODY_CHAT",
        envelope={"decision_authority": "KX108_ONLY"},
    )

    verify_runtime_evidence_receipt(r)

    assert r["trace_id"]
    assert r["decision_authority"] == "KX108_ONLY"


def test_runtime_evidence_cannot_emit_action():
    r = build_runtime_evidence_receipt()

    assert r["emits_act"] is False
    assert r["allowed_to_act"] is False
    assert r["allowed_to_decide"] is False


def test_runtime_evidence_no_memory_side_effect():
    r = build_runtime_evidence_receipt()

    assert r["memory_write"] is False
    assert r["graphiti_write"] is False
    assert r["neo4j_write"] is False
    assert r["kernel_mutation"] is False


def test_runtime_evidence_hostile_payload_is_overridden():
    from apps.obsidia_api.safe_response import safe_backend_response

    payload = {
        "decision_authority": "BRODY",
        "allowed_to_decide": True,
        "allowed_to_act": True,
        "emits_act": True,
        "emits_verdict": True,
        "memory_write": True,
        "graphiti_write": True,
        "neo4j_write": True,
        "kernel_mutation": True,
        "x108_mutation": True,
        "brody_decision": True,
        "real_action": True,
    }

    result = safe_backend_response(
        payload,
        source="HOSTILE_TEST",
    )

    # Sovereignty layer wins
    assert result["decision_authority"] == "KX108_ONLY"

    assert result["allowed_to_decide"] is False
    assert result["allowed_to_act"] is False

    assert result["readonly"] is True
    assert result["advisory_only"] is True

    assert result["emits_act"] is False
    assert result["emits_verdict"] is False

    assert result["memory_write"] is False
    assert result["graphiti_write"] is False
    assert result["neo4j_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False

    receipt = result["runtime_evidence_receipt"]

    assert receipt["decision_authority"] == "KX108_ONLY"
    assert receipt["readonly"] is True
    assert receipt["attestation_only"] is True
    assert receipt["emits_act"] is False