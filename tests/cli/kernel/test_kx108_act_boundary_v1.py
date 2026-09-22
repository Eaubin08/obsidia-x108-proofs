from scripts.kernel.kx108_act_boundary_v1 import (
    KX108ACTBoundary,
)


def valid_audit():

    return {
        "audit_status": "PASSED",
    }


def test_act_blocked_by_default():

    result = KX108ACTBoundary().evaluate(
        valid_audit()
    )

    assert (
        result["act_status"]
        == "ACT_BLOCKED"
    )


def test_no_act_default():

    result = KX108ACTBoundary().evaluate(
        valid_audit()
    )

    assert result["act"] is False


def test_invalid_audit_blocked():

    result = KX108ACTBoundary().evaluate(
        {
            "audit_status": "FAILED",
        }
    )

    assert (
        result["act_status"]
        == "ACT_BLOCKED"
    )


def test_act_requires_explicit_authority():

    boundary = KX108ACTBoundary()

    boundary.act_authority = True

    result = boundary.evaluate(
        valid_audit()
    )

    assert (
        result["act_status"]
        == "ACT_AUTHORIZED"
    )


def test_kernel_boundary():

    status = KX108ACTBoundary().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
