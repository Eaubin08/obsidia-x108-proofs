from scripts.kernel.kx108_act_audit_v1 import (
    KX108ACTAudit,
)


def act_boundary():

    return {
        "act_status": "ACT_BLOCKED",
        "act": False,
    }


def act_receipt():

    return {
        "receipt_id": "kx108-act-receipt-v1",
        "source_boundary": "KX108_ACT_BOUNDARY",
        "act": False,
    }


def test_act_audit_passes():

    result = KX108ACTAudit().audit(
        act_boundary(),
        act_receipt(),
    )

    assert (
        result["audit_status"]
        == "PASSED"
    )


def test_boundary_validation():

    result = KX108ACTAudit().audit(
        act_boundary(),
        act_receipt(),
    )

    assert (
        result["checks"]["act_boundary_valid"]
        is True
    )


def test_receipt_validation():

    result = KX108ACTAudit().audit(
        act_boundary(),
        act_receipt(),
    )

    assert (
        result["checks"]["receipt_valid"]
        is True
    )


def test_act_consistency():

    result = KX108ACTAudit().audit(
        act_boundary(),
        act_receipt(),
    )

    assert (
        result["checks"]["act_consistency"]
        is True
    )


def test_kernel_boundary():

    status = KX108ACTAudit().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
