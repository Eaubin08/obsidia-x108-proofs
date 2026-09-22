from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)

from scripts.kernel.kx108_proof_kernel_interface_v1 import (
    KX108ProofKernelInterface,
)


def packet():

    return cognitive_to_context_packet(
        {
            "signal":
                "cg68-kernel-interface",
        }
    )


def test_kernel_interface_validated():

    result = (
        KX108ProofKernelInterface()
        .validate(packet())
    )

    assert result["kernel_interface_status"] == "VALIDATED"

    assert (
        result["x108_decision"]
        == "ALLOW_CONTEXT_ONLY"
    )


def test_kernel_interface_preserves_kx108_only():

    result = (
        KX108ProofKernelInterface()
        .validate(packet())
    )

    assert (
        result["checks"]["runtime_wiring_kx108_only"]
        is True
    )

    assert (
        result["checks"]["packet_kx108_only"]
        is True
    )


def test_kernel_interface_rejects_decision_escalation():

    candidate = packet()
    candidate.decision_authority = "BRODY"

    result = (
        KX108ProofKernelInterface()
        .validate(candidate)
    )

    assert result["kernel_interface_status"] == "REJECTED"


def test_kernel_interface_rejects_act_escalation():

    candidate = packet()
    candidate.emits_act = True

    result = (
        KX108ProofKernelInterface()
        .validate(candidate)
    )

    assert result["kernel_interface_status"] == "REJECTED"


def test_kernel_interface_has_no_authority():

    status = (
        KX108ProofKernelInterface()
        .status()
    )

    assert status["interface_authority"] is False
    assert status["decision_authority"] == "KX108_ONLY"
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
