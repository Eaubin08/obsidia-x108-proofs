from scripts.kernel.kx108_act_boundary_v1 import (
    KX108ACTBoundary,
)

from scripts.kernel.kx108_act_receipt_v1 import (
    KX108ACTReceiptBuilder,
)

from scripts.kernel.kx108_act_audit_v1 import (
    KX108ACTAudit,
)


def test_final_act_chain():

    boundary = KX108ACTBoundary().evaluate(
        {
            "audit_status": "PASSED",
        }
    )

    receipt = KX108ACTReceiptBuilder().create(
        boundary
    )

    audit = KX108ACTAudit().audit(
        boundary,
        receipt.to_dict(),
    )

    assert (
        audit["audit_status"]
        == "PASSED"
    )


def test_act_blocked_default():

    result = KX108ACTBoundary().evaluate(
        {
            "audit_status": "PASSED",
        }
    )

    assert result["act"] is False


def test_receipt_integrity():

    receipt = KX108ACTReceiptBuilder().create(
        {
            "act_status": "ACT_BLOCKED",
            "act": False,
        }
    )

    assert (
        receipt.receipt_id
        == "kx108-act-receipt-v1"
    )


def test_audit_integrity():

    result = KX108ACTAudit().audit(
        {
            "act_status": "ACT_BLOCKED",
            "act": False,
        },
        {
            "receipt_id":
                "kx108-act-receipt-v1",
            "source_boundary":
                "KX108_ACT_BOUNDARY",
            "act":
                False,
        },
    )

    assert result["audit_status"] == "PASSED"


def test_final_kernel_integrity():

    status = KX108ACTAudit().status()

    assert status["act_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
