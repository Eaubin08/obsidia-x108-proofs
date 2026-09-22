"""
Receipt lifecycle proof for CanonicalRuntimeReceiptFlow.

The flow is the caller that owns the ProviderRuntimeReceipt lifecycle.
A receipt carrying a result_ref must not stay STARTED, and a completion
must never be fabricated when no real sealed runtime result exists.

No authority. No decision. No mutation.
"""

from scripts.kernel.kx108_proof_receipt_validation_v1 import (
    KX108ProofReceiptValidator,
)
from scripts.providers.canonical_runtime_receipt_flow_v1 import (
    CanonicalRuntimeReceiptFlow,
)


def real_provider(**kwargs):
    return {
        "runtime_id": "runtime-lifecycle-001",
        "provider": "brody",
    }


def resultless_provider(**kwargs):
    return {
        "provider": "brody",
    }


def _flow(handler=real_provider, provider_id="brody"):
    flow = CanonicalRuntimeReceiptFlow()
    flow.register_provider(provider_id, handler)
    return flow


def _run(flow, mission_id="mission-lifecycle-001", provider_id="brody"):
    return flow.run(
        mission_id=mission_id,
        provider_id=provider_id,
        capability="analysis",
        payload={},
    )


def test_receipt_is_completed_on_a_real_sealed_runtime_result():
    receipt = _run(_flow())["receipt"]

    assert receipt["status"] == "COMPLETED"
    assert receipt["result_ref"] == "runtime-lifecycle-001"
    assert receipt["completed_at"] != ""
    assert receipt["started_at"] != ""


def test_completed_receipt_is_bound_to_the_sealed_envelope():
    output = _run(_flow(), mission_id="mission-lifecycle-002")

    envelope = output["execution"]["execution"]["envelope"]
    receipt = output["receipt"]

    assert envelope["status"] == "SEALED"
    assert output["execution"]["flow_status"] == "COMPLETED"
    assert receipt["result_ref"] == envelope["runtime_id"]
    assert receipt["invocation_id"] == "mission-lifecycle-002"
    assert receipt["provider_id"] == envelope["provider_id"]
    assert receipt["adapter_id"] == "brody_runtime"


def test_receipt_never_carries_a_result_ref_while_still_started():
    receipt = _run(_flow(), mission_id="mission-lifecycle-003")["receipt"]

    assert not (receipt["result_ref"] and receipt["status"] == "STARTED")


def test_no_result_means_failed_receipt_not_a_fabricated_completion():
    """A provider returning no runtime_id must not yield a COMPLETED receipt."""
    receipt = _run(
        _flow(handler=resultless_provider), mission_id="mission-lifecycle-004"
    )["receipt"]

    assert receipt["status"] == "FAILED"
    assert receipt["result_ref"] == ""
    assert receipt["completed_at"] != ""


def test_failed_receipt_is_rejected_by_the_kx108_receipt_validator():
    output = _run(
        _flow(handler=resultless_provider), mission_id="mission-lifecycle-005"
    )
    envelope = output["execution"]["execution"]["envelope"]

    validation = KX108ProofReceiptValidator().validate(
        output["receipt"],
        expected_result_ref=envelope["runtime_id"],
        expected_invocation_id="mission-lifecycle-005",
    )

    assert validation["receipt_validation_status"] == "REJECTED"
    assert validation["checks"]["result_reference"] is False
    assert validation["checks"]["status_acceptable"] is False


def test_completed_receipt_is_validated_by_the_kx108_receipt_validator():
    output = _run(_flow(), mission_id="mission-lifecycle-006")
    envelope = output["execution"]["execution"]["envelope"]

    validation = KX108ProofReceiptValidator().validate(
        output["receipt"],
        expected_result_ref=envelope["runtime_id"],
        expected_invocation_id="mission-lifecycle-006",
    )

    assert validation["receipt_validation_status"] == "VALIDATED"
    assert validation["checks"]["status_acceptable"] is True
    assert validation["checks"]["binding_valid"] is True
    assert validation["checks"]["result_ref_matches"] is True
    assert validation["checks"]["authority_boundary_preserved"] is True


def test_receipt_lifecycle_creates_no_authority():
    receipt = _run(_flow(), mission_id="mission-lifecycle-007")["receipt"]

    assert receipt["decision_authority"] is False
    assert receipt["execution_authority"] is False
    assert receipt["memory_write"] is False
    assert receipt["kernel_mutation"] is False
    assert receipt["emits_act"] is False


def test_each_run_produces_a_distinct_runtime_execution_id():
    flow = _flow()

    first = _run(flow, mission_id="mission-lifecycle-008")["receipt"]
    second = _run(flow, mission_id="mission-lifecycle-009")["receipt"]

    assert first["runtime_execution_id"] != second["runtime_execution_id"]
    assert first["invocation_id"] != second["invocation_id"]
    assert first["status"] == second["status"] == "COMPLETED"
