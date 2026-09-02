from scripts.kernel.kx108_execution_boundary_v1 import (
    KX108ExecutionBoundary,
)

from scripts.kernel.kx108_execution_receipt_v1 import (
    KX108ExecutionReceiptBuilder,
)

from scripts.kernel.kx108_execution_audit_v1 import (
    KX108ExecutionAudit,
)


def test_final_execution_chain():

    boundary = KX108ExecutionBoundary().authorize(
        {
            "audit_status": "PASSED",
        }
    )

    assert (
        boundary["execution_status"]
        == "EXECUTION_AUTHORIZED"
    )


    receipt = KX108ExecutionReceiptBuilder().create(
        boundary
    )

    assert (
        receipt.receipt_id
        == "kx108-execution-receipt-v1"
    )


    audit = KX108ExecutionAudit().audit(
        boundary,
        receipt.to_dict(),
    )

    assert (
        audit["audit_status"]
        == "PASSED"
    )


def test_execution_never_emits_act():

    result = KX108ExecutionBoundary().authorize(
        {
            "audit_status": "PASSED",
        }
    )

    assert result["act"] is False


def test_receipt_boundary():

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


def test_audit_boundary():

    status = KX108ExecutionAudit().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False


def test_kernel_integrity():

    status = KX108ExecutionAudit().status()

    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
