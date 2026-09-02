from scripts.kernel.kx108_execution_audit_v1 import (
    KX108ExecutionAudit,
)


def boundary():

    return {
        "execution_status": "EXECUTION_AUTHORIZED",
    }


def receipt():

    return {
        "receipt_id": "kx108-execution-receipt-v1",
        "source_boundary": "KX108_EXECUTION_BOUNDARY",
        "act": False,
    }


def test_execution_audit_passes():

    result = KX108ExecutionAudit().audit(
        boundary(),
        receipt(),
    )

    assert (
        result["audit_status"]
        == "PASSED"
    )


def test_boundary_check():

    result = KX108ExecutionAudit().audit(
        boundary(),
        receipt(),
    )

    assert (
        result["checks"]["execution_authorized"]
        is True
    )


def test_receipt_check():

    result = KX108ExecutionAudit().audit(
        boundary(),
        receipt(),
    )

    assert (
        result["checks"]["receipt_valid"]
        is True
    )


def test_act_disabled():

    result = KX108ExecutionAudit().audit(
        boundary(),
        receipt(),
    )

    assert result["act"] is False


def test_kernel_boundary():

    status = KX108ExecutionAudit().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
