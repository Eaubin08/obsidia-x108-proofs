from scripts.kernel.kernel_decision_resolver_audit_v1 import (
    KernelDecisionResolverAudit,
)


def resolver_result():

    return {
        "resolver_status": "RESOLUTION_READY",
        "decision_status": "CANDIDATE_ONLY",
    }


def resolver_receipt():

    return {
        "receipt_id": "resolver-receipt-v1",
        "resolver_status": "RESOLUTION_READY",
    }


def test_resolver_audit_passes():

    audit = KernelDecisionResolverAudit()

    result = audit.audit(
        resolver_result(),
        resolver_receipt(),
    )

    assert result["audit_status"] == "PASSED"


def test_candidate_only_check():

    audit = KernelDecisionResolverAudit()

    result = audit.audit(
        resolver_result(),
        resolver_receipt(),
    )

    assert result["checks"]["candidate_only"] is True


def test_receipt_check():

    audit = KernelDecisionResolverAudit()

    result = audit.audit(
        resolver_result(),
        resolver_receipt(),
    )

    assert result["checks"]["receipt_present"] is True


def test_no_decision_output():

    audit = KernelDecisionResolverAudit()

    result = audit.audit(
        resolver_result(),
        resolver_receipt(),
    )

    assert result["decision"] is None


def test_kernel_boundary():

    status = KernelDecisionResolverAudit().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
