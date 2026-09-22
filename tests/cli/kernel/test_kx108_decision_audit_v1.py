from scripts.kernel.kx108_decision_audit_v1 import (
    KX108DecisionAudit,
)


def envelope():

    return {
        "authority_status": "AUTHORIZED_CANDIDATE",
        "decision_status": "KX108_DECISION_READY",
    }


def receipt():

    return {
        "receipt_id": "kx108-decision-receipt-v1",
        "source_envelope": "KX108_DECISION_ENVELOPE",
    }


def test_kx108_audit_passes():

    result = KX108DecisionAudit().audit(
        envelope(),
        receipt(),
    )

    assert result["audit_status"] == "PASSED"


def test_authority_check():

    result = KX108DecisionAudit().audit(
        envelope(),
        receipt(),
    )

    assert result["checks"]["authority_valid"] is True


def test_decision_ready_check():

    result = KX108DecisionAudit().audit(
        envelope(),
        receipt(),
    )

    assert result["checks"]["decision_ready"] is True


def test_receipt_binding_check():

    result = KX108DecisionAudit().audit(
        envelope(),
        receipt(),
    )

    assert result["checks"]["receipt_valid"] is True


def test_kernel_boundary():

    status = KX108DecisionAudit().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
