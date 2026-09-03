from periphery.context.context_packet_builder_v2 import (
    build_context_packet_v2,
)

from scripts.kernel.kx108_proof_context_boundary_v1 import (
    KX108ProofContextBoundary,
)


def packet():

    return build_context_packet_v2(
        query="CG39 context validation",
        context_items=[
            "readonly context signal",
        ],
    ).to_dict()


def test_context_packet_validated():

    result = KX108ProofContextBoundary().validate(
        packet()
    )

    assert result["context_boundary_status"] == "VALIDATED"
    assert result["checks"]["packet_valid"] is True
    assert result["checks"]["x108_boundary_passed"] is True


def test_context_packet_is_signal_only():

    result = KX108ProofContextBoundary().validate(
        packet()
    )

    assert result["checks"]["context_signal_only"] is True
    assert result["checks"]["cannot_decide"] is True
    assert result["checks"]["cannot_act"] is True


def test_context_memory_write_tamper_rejected():

    candidate = packet()
    candidate["memory_write"] = True

    result = KX108ProofContextBoundary().validate(
        candidate
    )

    assert result["context_boundary_status"] == "REJECTED"
    assert result["checks"]["no_memory_write"] is False


def test_context_authority_tamper_rejected():

    candidate = packet()
    candidate["decision_authority"] = "PERIPHERY"

    result = KX108ProofContextBoundary().validate(
        candidate
    )

    assert result["context_boundary_status"] == "REJECTED"
    assert result["checks"]["kx108_only"] is False


def test_context_boundary_has_no_sovereignty():

    status = KX108ProofContextBoundary().status()

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["allowed_to_decide"] is False
    assert status["allowed_to_act"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
