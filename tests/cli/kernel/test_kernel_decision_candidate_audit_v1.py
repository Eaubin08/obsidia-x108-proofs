from scripts.kernel.kernel_decision_candidate_audit_v1 import (
    KernelDecisionCandidateAudit,
)


def candidate_flow():

    return {
        "candidate": {
            "decision_status": "CANDIDATE_ONLY"
        }
    }


def candidate_receipt():

    return {
        "receipt_id": "candidate-receipt-v1",
        "source_provider": "brody",
        "runtime_ref": "runtime-001",
    }


def test_audit_passes():

    audit = KernelDecisionCandidateAudit()

    result = audit.audit(
        candidate_flow(),
        candidate_receipt(),
    )

    assert result["audit_status"] == "PASSED"


def test_candidate_check():

    audit = KernelDecisionCandidateAudit()

    result = audit.audit(
        candidate_flow(),
        candidate_receipt(),
    )

    assert result["checks"]["candidate_present"] is True


def test_receipt_check():

    audit = KernelDecisionCandidateAudit()

    result = audit.audit(
        candidate_flow(),
        candidate_receipt(),
    )

    assert result["checks"]["receipt_present"] is True


def test_no_decision_output():

    audit = KernelDecisionCandidateAudit()

    result = audit.audit(
        candidate_flow(),
        candidate_receipt(),
    )

    assert result["decision"] is None


def test_kernel_boundary():

    status = KernelDecisionCandidateAudit().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
