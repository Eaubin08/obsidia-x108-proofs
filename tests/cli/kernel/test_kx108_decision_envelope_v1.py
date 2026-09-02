from scripts.kernel.kx108_decision_envelope_v1 import (
    KX108DecisionEnvelopeBuilder,
)


def authority_result():

    return {
        "authority_status": "AUTHORIZED_CANDIDATE",
    }


def test_envelope_creation():

    envelope = KX108DecisionEnvelopeBuilder().build(
        authority_result()
    )

    assert (
        envelope.decision_status
        == "KX108_DECISION_READY"
    )


def test_authority_trace():

    envelope = KX108DecisionEnvelopeBuilder().build(
        authority_result()
    )

    assert (
        envelope.source_authority
        == "KX108"
    )


def test_no_act():

    envelope = KX108DecisionEnvelopeBuilder().build(
        authority_result()
    )

    assert envelope.act is False


def test_rejected_authority():

    envelope = KX108DecisionEnvelopeBuilder().build(
        {
            "authority_status": "REJECTED",
        }
    )

    assert (
        envelope.decision_status
        == "NONE"
    )


def test_kernel_boundary():

    status = KX108DecisionEnvelopeBuilder().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
