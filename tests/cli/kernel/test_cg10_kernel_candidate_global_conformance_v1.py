from scripts.kernel.kernel_bridge_validator_v1 import (
    KernelBridgeValidator,
)

from scripts.kernel.x108_guard_adapter_v1 import (
    X108GuardAdapter,
)

from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelopeBuilder,
)

from scripts.kernel.kernel_decision_candidate_flow_v1 import (
    KernelDecisionCandidateFlow,
)

from scripts.kernel.kernel_decision_candidate_receipt_v1 import (
    KernelDecisionCandidateReceipt,
)

from scripts.kernel.kernel_decision_candidate_audit_v1 import (
    KernelDecisionCandidateAudit,
)


def runtime_receipt():

    return {
        "provider_id": "brody",
        "invocation_id": "mission-001",
        "result_ref": "runtime-001",
    }


def test_full_kernel_candidate_chain():

    receipt = runtime_receipt()

    validator = KernelBridgeValidator()

    validation = validator.validate(
        receipt
    )

    assert validation.status == "VALIDATED"


    guard = X108GuardAdapter()

    guard_result = guard.evaluate(
        {
            "status": validation.status,
            "provider_id": receipt["provider_id"],
            "runtime_id": receipt["result_ref"],
        }
    )

    assert guard_result.status == "GUARD_PASSED"


    builder = CanonicalDecisionEnvelopeBuilder()

    envelope = builder.build(
        {
            "provider_id": receipt["provider_id"],
            "runtime_id": receipt["result_ref"],
            "status": guard_result.status,
        }
    )

    assert envelope.decision_status == "CANDIDATE_ONLY"


    flow = KernelDecisionCandidateFlow()

    candidate = flow.process(
        {
            "status": "VALIDATED",
            "provider_id": receipt["provider_id"],
            "runtime_id": receipt["result_ref"],
        }
    )

    assert candidate["status"] == "CANDIDATE_CREATED"


    candidate_receipt = KernelDecisionCandidateReceipt().create(
        candidate["candidate"]
    )

    assert (
        candidate_receipt.candidate_status
        == "CANDIDATE_ONLY"
    )


    audit = KernelDecisionCandidateAudit().audit(
        candidate,
        candidate_receipt.to_dict(),
    )

    assert audit["audit_status"] == "PASSED"


def test_no_decision_authority():

    status = KernelDecisionCandidateAudit().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_candidate_is_not_act():

    envelope = CanonicalDecisionEnvelopeBuilder().build(
        {
            "provider_id": "brody",
            "runtime_id": "runtime-002",
            "status": "GUARD_PASSED",
        }
    )

    assert envelope.decision_status != "ACT"


def test_provider_trace_survives():

    receipt = KernelDecisionCandidateReceipt().create(
        {
            "source_provider": "brody",
            "runtime_ref": "runtime-003",
            "decision_status": "CANDIDATE_ONLY",
        }
    )

    assert receipt.source_provider == "brody"


def test_runtime_trace_survives():

    receipt = KernelDecisionCandidateReceipt().create(
        {
            "source_provider": "brody",
            "runtime_ref": "runtime-004",
            "decision_status": "CANDIDATE_ONLY",
        }
    )

    assert receipt.runtime_ref == "runtime-004"
