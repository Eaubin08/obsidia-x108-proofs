from scripts.kernel.kx108_decision_authority_v1 import (
    KX108DecisionAuthority,
)

from scripts.kernel.kx108_decision_envelope_v1 import (
    KX108DecisionEnvelopeBuilder,
)

from scripts.kernel.kx108_decision_receipt_v1 import (
    KX108DecisionReceiptBuilder,
)

from scripts.kernel.kx108_decision_audit_v1 import (
    KX108DecisionAudit,
)


def audit_result():

    return {
        "audit_status": "PASSED",
    }


def test_full_kx108_chain():

    authority = KX108DecisionAuthority()

    authority_result = authority.evaluate(
        audit_result()
    )

    assert (
        authority_result["authority_status"]
        == "AUTHORIZED_CANDIDATE"
    )


    envelope = KX108DecisionEnvelopeBuilder().build(
        authority_result
    )

    assert (
        envelope.decision_status
        == "KX108_DECISION_READY"
    )


    receipt = KX108DecisionReceiptBuilder().create(
        envelope.to_dict()
    )

    assert (
        receipt.receipt_id
        == "kx108-decision-receipt-v1"
    )


    audit = KX108DecisionAudit().audit(
        envelope.to_dict(),
        receipt.to_dict(),
    )

    assert (
        audit["audit_status"]
        == "PASSED"
    )


def test_authority_propagation():

    authority = KX108DecisionAuthority()

    result = authority.evaluate(
        audit_result()
    )

    assert (
        result["authority_status"]
        == "AUTHORIZED_CANDIDATE"
    )


def test_envelope_propagation():

    envelope = KX108DecisionEnvelopeBuilder().build(
        {
            "authority_status": "AUTHORIZED_CANDIDATE",
        }
    )

    assert (
        envelope.source_authority
        == "KX108"
    )


def test_receipt_propagation():

    receipt = KX108DecisionReceiptBuilder().create(
        {
            "authority_status": "AUTHORIZED_CANDIDATE",
            "decision_status": "KX108_DECISION_READY",
        }
    )

    assert (
        receipt.source_envelope
        == "KX108_DECISION_ENVELOPE"
    )


def test_no_execution_authority():

    status = KX108DecisionAudit().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
