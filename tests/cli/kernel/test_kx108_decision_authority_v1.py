from scripts.kernel.kx108_decision_authority_v1 import (
    KX108DecisionAuthority,
)


def valid_audit():

    return {
        "audit_status": "PASSED",
    }


def test_kx108_authorizes_candidate():

    authority = KX108DecisionAuthority()

    result = authority.evaluate(
        valid_audit()
    )

    assert (
        result["authority_status"]
        == "AUTHORIZED_CANDIDATE"
    )


def test_decision_ready():

    authority = KX108DecisionAuthority()

    result = authority.evaluate(
        valid_audit()
    )

    assert (
        result["decision_status"]
        == "KX108_DECISION_READY"
    )


def test_no_act():

    authority = KX108DecisionAuthority()

    result = authority.evaluate(
        valid_audit()
    )

    assert result["act"] is False


def test_failed_audit_rejected():

    authority = KX108DecisionAuthority()

    result = authority.evaluate(
        {
            "audit_status": "FAILED",
        }
    )

    assert (
        result["authority_status"]
        == "REJECTED"
    )


def test_authority_boundary():

    status = KX108DecisionAuthority().status()

    assert status["authority_enabled"] is True
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
