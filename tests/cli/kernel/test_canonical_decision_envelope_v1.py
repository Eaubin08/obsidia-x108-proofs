from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelopeBuilder,
)


def test_build_candidate_envelope():

    builder = CanonicalDecisionEnvelopeBuilder()

    envelope = builder.build(
        {
            "provider_id": "brody",
            "runtime_id": "runtime-001",
            "status": "GUARD_PASSED",
        }
    )

    assert envelope.decision_status == "CANDIDATE_ONLY"


def test_provider_binding():

    builder = CanonicalDecisionEnvelopeBuilder()

    envelope = builder.build(
        {
            "provider_id": "obsidure",
            "runtime_id": "runtime-002",
            "status": "GUARD_PASSED",
        }
    )

    assert envelope.source_provider == "obsidure"


def test_runtime_binding():

    builder = CanonicalDecisionEnvelopeBuilder()

    envelope = builder.build(
        {
            "provider_id": "brody",
            "runtime_id": "runtime-003",
            "status": "GUARD_PASSED",
        }
    )

    assert envelope.runtime_ref == "runtime-003"


def test_no_act_output():

    builder = CanonicalDecisionEnvelopeBuilder()

    envelope = builder.build(
        {
            "provider_id": "brody",
            "runtime_id": "runtime-004",
            "status": "GUARD_PASSED",
        }
    )

    assert envelope.decision_status != "ACT"


def test_kernel_boundary():

    status = CanonicalDecisionEnvelopeBuilder().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
