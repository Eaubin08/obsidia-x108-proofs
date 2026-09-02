from scripts.kernel.kernel_decision_gate_v1 import (
    KernelDecisionGate,
)

from scripts.kernel.kernel_decision_resolver_v1 import (
    KernelDecisionResolver,
)

from scripts.kernel.kernel_decision_resolver_receipt_v1 import (
    KernelDecisionResolverReceipt,
)

from scripts.kernel.kernel_decision_resolver_audit_v1 import (
    KernelDecisionResolverAudit,
)


def test_full_cg10_final_chain():

    gate = KernelDecisionGate()

    gate_result = gate.evaluate(
        {
            "audit_status": "PASSED"
        }
    )

    assert (
        gate_result["gate_status"]
        == "OPEN_FOR_DECISION"
    )


    resolver = KernelDecisionResolver()

    resolver_result = resolver.resolve(
        gate_result
    )

    assert (
        resolver_result["decision_status"]
        == "CANDIDATE_ONLY"
    )


    receipt = KernelDecisionResolverReceipt().create(
        resolver_result
    )

    assert (
        receipt.receipt_id
        == "resolver-receipt-v1"
    )


    audit = KernelDecisionResolverAudit().audit(
        resolver_result,
        receipt.to_dict(),
    )

    assert (
        audit["audit_status"]
        == "PASSED"
    )


def test_no_act():

    result = KernelDecisionResolver().resolve(
        {
            "gate_status": "OPEN_FOR_DECISION"
        }
    )

    assert result["act"] is False


def test_no_decision():

    result = KernelDecisionResolver().resolve(
        {
            "gate_status": "OPEN_FOR_DECISION"
        }
    )

    assert result["decision"] is None


def test_candidate_only():

    result = KernelDecisionResolver().resolve(
        {
            "gate_status": "OPEN_FOR_DECISION"
        }
    )

    assert (
        result["decision_status"]
        == "CANDIDATE_ONLY"
    )


def test_kernel_boundary():

    status = KernelDecisionResolverAudit().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
