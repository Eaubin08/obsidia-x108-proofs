from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)

from scripts.kernel.kx108_proof_runtime_interface_boundary_v1 import (
    KX108ProofRuntimeInterfaceBoundary,
)


def packet():

    return cognitive_to_context_packet(
        {
            "signal":
                "cg77-runtime-interface",
        }
    )


def test_runtime_interface_boundary_validated():

    result = (
        KX108ProofRuntimeInterfaceBoundary()
        .validate(packet())
    )

    assert (
        result[
            "runtime_interface_boundary_status"
        ]
        == "VALIDATED"
    )


def test_kernel_interface_composed():

    result = (
        KX108ProofRuntimeInterfaceBoundary()
        .validate(packet())
    )

    assert (
        result["checks"]["kernel_interface_validated"]
        is True
    )


def test_runtime_authority_remains_disabled():

    result = (
        KX108ProofRuntimeInterfaceBoundary()
        .validate(packet())
    )

    assert (
        result["checks"]["runtime_authority_validated"]
        is True
    )

    assert (
        result[
            "runtime_authority_boundary"
        ][
            "authorizes_runtime"
        ]
        is False
    )

    assert result["runtime_activated"] is False


def test_runtime_activation_attempt_rejected():

    candidate = packet()
    candidate.runtime_allowed_now = True

    result = (
        KX108ProofRuntimeInterfaceBoundary()
        .validate(candidate)
    )

    assert (
        result[
            "runtime_interface_boundary_status"
        ]
        == "REJECTED"
    )


def test_runtime_interface_non_sovereign():

    result = (
        KX108ProofRuntimeInterfaceBoundary()
        .validate(packet())
    )

    assert result["interface_authority"] is False
    assert result["runtime_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
