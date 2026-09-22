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


def audit_result():

    return {
        "audit_status": "PASSED",
    }


def test_full_resolution_chain():

    gate = KernelDecisionGate()

    gate_result = gate.evaluate(
        audit_result()
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
        resolver_result["resolver_status"]
        == "RESOLUTION_READY"
    )


    receipt = KernelDecisionResolverReceipt().create(
        resolver_result
    )

    assert (
        receipt.decision_status
        == "CANDIDATE_ONLY"
    )


    audit = KernelDecisionResolverAudit().audit(
        resolver_result,
        receipt.to_dict(),
    )

    assert (
        audit["audit_status"]
        == "PASSED"
    )


def test_no_decision_emission():

    resolver = KernelDecisionResolver()

    result = resolver.resolve(
        {
            "gate_status": "OPEN_FOR_DECISION",
        }
    )

    assert result["decision"] is None
    assert result["act"] is False


def test_candidate_only_survives():

    resolver = KernelDecisionResolver()

    result = resolver.resolve(
        {
            "gate_status": "OPEN_FOR_DECISION",
        }
    )

    assert (
        result["decision_status"]
        == "CANDIDATE_ONLY"
    )


def test_audit_receipt_binding():

    receipt = KernelDecisionResolverReceipt().create(
        {
            "resolver_status": "RESOLUTION_READY",
            "decision_status": "CANDIDATE_ONLY",
        }
    )

    assert (
        receipt.resolver_status
        == "RESOLUTION_READY"
    )


def test_kernel_authority_boundary():

    status = KernelDecisionResolverAudit().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
