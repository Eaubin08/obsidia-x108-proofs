import json

from periphery.agents.obsidure_math_memory_provider import (
    ObsidureMathMemoryProvider,
)

from scripts.kernel.kx108_proof_knowledge_boundary_v1 import (
    KX108ProofKnowledgeBoundary,
)


def provider(tmp_path):

    index = {
        "items": [
            {
                "id": "KNOWN_PROOF",
                "status": "CANONICAL_CANDIDATE",
                "can_be_used_for_proof": True,
                "related_metrics": ["S"],
                "missing_dependencies": [],
            },
            {
                "id": "KNOWN_HYPOTHESIS",
                "status": "HYPOTHESE_TEMPORAIRE",
                "can_be_used_for_proof": False,
                "related_metrics": [],
                "missing_dependencies": [],
            },
        ]
    }

    path = tmp_path / "memory_index.json"

    path.write_text(
        json.dumps(index),
        encoding="utf-8",
    )

    return ObsidureMathMemoryProvider(
        index_path=path
    )


def test_known_knowledge_available(tmp_path):

    boundary = KX108ProofKnowledgeBoundary(
        provider(tmp_path)
    )

    result = boundary.inspect(
        "KNOWN_PROOF"
    )

    assert result["knowledge_boundary_status"] == "AVAILABLE"
    assert result["checks"]["context_known"] is True


def test_known_proof_can_be_proof_eligible(tmp_path):

    boundary = KX108ProofKnowledgeBoundary(
        provider(tmp_path)
    )

    result = boundary.inspect(
        "KNOWN_PROOF"
    )

    assert result["proof_eligible"] is True


def test_hypothesis_not_promoted_to_proof(tmp_path):

    boundary = KX108ProofKnowledgeBoundary(
        provider(tmp_path)
    )

    result = boundary.inspect(
        "KNOWN_HYPOTHESIS"
    )

    assert result["knowledge_boundary_status"] == "AVAILABLE"
    assert result["proof_eligible"] is False


def test_missing_knowledge_stays_missing(tmp_path):

    boundary = KX108ProofKnowledgeBoundary(
        provider(tmp_path)
    )

    result = boundary.inspect(
        "NOT_PRESENT"
    )

    assert (
        result["knowledge_boundary_status"]
        == "MISSING_CONTEXT"
    )

    assert result["proof_eligible"] is False
    assert result["knowledge"] is None


def test_knowledge_boundary_has_no_sovereignty(tmp_path):

    boundary = KX108ProofKnowledgeBoundary(
        provider(tmp_path)
    )

    status = boundary.status()

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["allowed_to_decide"] is False
    assert status["allowed_to_act"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
