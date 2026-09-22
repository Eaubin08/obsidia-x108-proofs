from scripts.kernel.kx108_act_boundary_v1 import (
    KX108ACTBoundary,
)

from scripts.kernel.kx108_act_receipt_v1 import (
    KX108ACTReceiptBuilder,
)

from scripts.kernel.kx108_act_audit_v1 import (
    KX108ACTAudit,
)


def test_full_kx108_act_chain():

    act_boundary = KX108ACTBoundary().evaluate(
        {
            "audit_status": "PASSED",
        }
    )

    assert (
        act_boundary["act_status"]
        == "ACT_BLOCKED"
    )


    act_receipt = KX108ACTReceiptBuilder().create(
        act_boundary
    )

    assert (
        act_receipt.receipt_id
        == "kx108-act-receipt-v1"
    )


    act_audit = KX108ACTAudit().audit(
        act_boundary,
        act_receipt.to_dict(),
    )

    assert (
        act_audit["audit_status"]
        == "PASSED"
    )


def test_act_boundary_before_action():

    result = KX108ACTBoundary().evaluate(
        {
            "audit_status": "PASSED",
        }
    )

    assert (
        result["act"]
        is False
    )


def test_act_receipt_binding():

    receipt = KX108ACTReceiptBuilder().create(
        {
            "act_status": "ACT_BLOCKED",
            "act": False,
        }
    )

    assert (
        receipt.source_boundary
        == "KX108_ACT_BOUNDARY"
    )


def test_act_audit_binding():

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

    assert (
        result["audit_status"]
        == "PASSED"
    )


def test_final_act_integrity():

    status = KX108ACTAudit().status()

    assert status["act_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
