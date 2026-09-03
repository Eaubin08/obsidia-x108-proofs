from periphery.memory.memory_source_registry import (
    MemorySourceEntry,
)

from periphery.memory.memory_source_types import (
    MemorySourceType,
)

from scripts.kernel.kx108_proof_memory_boundary_v1 import (
    KX108ProofMemoryBoundary,
)


def test_default_memory_source_validated():

    result = KX108ProofMemoryBoundary().validate_source(
        "brody_runtime"
    )

    assert result["memory_boundary_status"] == "VALIDATED"
    assert result["checks"]["readonly"] is True
    assert result["checks"]["write_forbidden"] is True


def test_unknown_memory_source_rejected():

    result = KX108ProofMemoryBoundary().validate_source(
        "does-not-exist"
    )

    assert result["memory_boundary_status"] == "REJECTED"
    assert result["checks"]["source_present"] is False


def test_write_enabled_source_rejected():

    source = MemorySourceEntry(
        source_id="unsafe",
        source_type=MemorySourceType.UNKNOWN,
        readonly=False,
        write_allowed=True,
    )

    result = KX108ProofMemoryBoundary().validate_source(
        source
    )

    assert result["memory_boundary_status"] == "REJECTED"
    assert result["checks"]["write_forbidden"] is False


def test_memory_registry_readonly():

    result = KX108ProofMemoryBoundary().validate_registry()

    assert result["memory_registry_status"] == "VALIDATED"
    assert result["checks"]["all_readonly"] is True
    assert result["checks"]["all_write_forbidden"] is True


def test_memory_boundary_has_no_sovereignty():

    status = KX108ProofMemoryBoundary().status()

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["allowed_to_decide"] is False
    assert status["allowed_to_act"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
