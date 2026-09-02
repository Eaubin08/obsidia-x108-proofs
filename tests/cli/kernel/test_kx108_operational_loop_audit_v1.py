from scripts.kernel.kx108_operational_loop_audit_v1 import (
    KX108OperationalLoopAudit,
)


def state():

    return {
        "state": "DECISION_PENDING",
    }


def receipt():

    return {
        "receipt_id":
            "kx108-operational-loop-receipt-v1",
        "transition":
            "DECISION_PENDING",
        "next_state":
            "DECISION_PENDING",
    }


def test_loop_audit_passes():

    result = KX108OperationalLoopAudit().audit(
        state(),
        receipt(),
    )

    assert (
        result["audit_status"]
        == "PASSED"
    )


def test_state_check():

    result = KX108OperationalLoopAudit().audit(
        state(),
        receipt(),
    )

    assert (
        result["checks"]["state_present"]
        is True
    )


def test_receipt_check():

    result = KX108OperationalLoopAudit().audit(
        state(),
        receipt(),
    )

    assert (
        result["checks"]["receipt_valid"]
        is True
    )


def test_state_binding():

    result = KX108OperationalLoopAudit().audit(
        state(),
        receipt(),
    )

    assert (
        result["checks"]["state_binding"]
        is True
    )


def test_kernel_protection():

    status = KX108OperationalLoopAudit().status()

    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
