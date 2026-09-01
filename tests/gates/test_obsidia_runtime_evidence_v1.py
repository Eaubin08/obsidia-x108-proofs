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