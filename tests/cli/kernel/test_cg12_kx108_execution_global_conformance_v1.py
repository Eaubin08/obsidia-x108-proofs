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

from scripts.kernel.kx108_execution_boundary_v1 import (
    KX108ExecutionBoundary,
)

from scripts.kernel.kx108_execution_receipt_v1 import (
    KX108ExecutionReceiptBuilder,
)

from scripts.kernel.kx108_execution_audit_v1 import (
    KX108ExecutionAudit,
)


def test_full_kx108_execution_chain():

    authority = KX108DecisionAuthority()

    authority_result = authority.evaluate(
        {
            "audit_status": "PASSED",
        }
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


    decision_receipt = KX108DecisionReceiptBuilder().create(
        envelope.to_dict()
    )

    assert (
        decision_receipt.receipt_id
        == "kx108-decision-receipt-v1"
    )


    decision_audit = KX108DecisionAudit().audit(
        envelope.to_dict(),
        decision_receipt.to_dict(),
    )

    assert (
        decision_audit["audit_status"]
        == "PASSED"
    )


    execution = KX108ExecutionBoundary().authorize(
        decision_audit
    )

    assert (
        execution["execution_status"]
        == "EXECUTION_AUTHORIZED"
    )


    execution_receipt = (
        KX108ExecutionReceiptBuilder().create(
            execution
        )
    )

    assert (
        execution_receipt.receipt_id
        == "kx108-execution-receipt-v1"
    )


    execution_audit = KX108ExecutionAudit().audit(
        execution,
        execution_receipt.to_dict(),
    )

    assert (
        execution_audit["audit_status"]
        == "PASSED"
    )


def test_decision_to_execution_binding():

    result = KX108ExecutionBoundary().authorize(
        {
            "audit_status": "PASSED",
        }
    )

    assert (
        result["execution_status"]
        == "EXECUTION_AUTHORIZED"
    )


def test_execution_receipt_binding():

    receipt = KX108ExecutionReceiptBuilder().create(
        {
            "execution_status":
                "EXECUTION_AUTHORIZED",
        }
    )

    assert (
        receipt.source_boundary
        == "KX108_EXECUTION_BOUNDARY"
    )


def test_execution_audit_binding():

    result = KX108ExecutionAudit().audit(
        {
            "execution_status":
                "EXECUTION_AUTHORIZED",
        },
        {
            "receipt_id":
                "kx108-execution-receipt-v1",
            "source_boundary":
                "KX108_EXECUTION_BOUNDARY",
            "act":
                False,
        },
    )

    assert result["audit_status"] == "PASSED"


def test_final_act_boundary():

    status = KX108ExecutionAudit().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
