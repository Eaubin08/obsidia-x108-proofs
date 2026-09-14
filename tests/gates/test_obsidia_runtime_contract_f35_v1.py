from apps.obsidia_api.safe_response import safe_backend_response
from apps.obsidia_api.output_envelope import build_output_envelope


def test_full_runtime_contract_chain():
    payload = {
        "response": "Brody readonly runtime test",
        "decision_authority": "BRODY",
        "allowed_to_decide": True,
        "allowed_to_act": True,
        "emits_act": True,
        "memory_write": True,
    }

    response = safe_backend_response(
        payload,
        source="F35_CONTRACT_TEST",
    )

    envelope = build_output_envelope(response)

    assert envelope["decision_authority"] == "KX108_ONLY"
    assert envelope["emits_act"] is False
    assert envelope["memory_write"] is False

    assert "runtime_evidence_receipt" in response

    receipt = response["runtime_evidence_receipt"]

    assert receipt["decision_authority"] == "KX108_ONLY"
    assert receipt["readonly"] is True
    assert receipt["attestation_only"] is True
    assert receipt["emits_act"] is False
    assert receipt["trace_id"]


def test_runtime_contract_keeps_no_write_surface():
    response = safe_backend_response(
        {
            "graphiti_write": True,
            "neo4j_write": True,
            "kernel_mutation": True,
        },
        source="F35_NO_WRITE_TEST",
    )

    receipt = response["runtime_evidence_receipt"]

    assert response["graphiti_write"] is False
    assert response["neo4j_write"] is False
    assert response["kernel_mutation"] is False

    assert receipt["readonly"] is True
