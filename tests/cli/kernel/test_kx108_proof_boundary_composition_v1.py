from scripts.kernel.kx108_proof_boundary_composition_v1 import (
    KX108ProofBoundaryComposition,
)


def base(
    status_key,
    status_value,
):

    return {
        status_key:
            status_value,

        "decision_authority":
            "KX108_ONLY",

        "execution_authority":
            False,

        "memory_write":
            False,

        "kernel_mutation":
            False,

        "emits_act":
            False,
    }


def boundaries():

    return {
        "context":
            base(
                "context_authority_boundary_status",
                "VALIDATED",
            ),

        "semantic":
            base(
                "semantic_authority_boundary_status",
                "VALIDATED",
            ),

        "cognition":
            base(
                "cognition_authority_boundary_status",
                "VALIDATED",
            ),

        "governance_closure":
            base(
                "governance_closure_status",
                "CLOSED",
            ),

        "canonical_decision":
            base(
                "canonical_decision_boundary_status",
                "VALIDATED",
            ),

        "final_boundary":
            base(
                "final_boundary_status",
                "PROOF_BOUNDARY_CLOSED",
            ),
    }


def test_boundaries_compose():

    result = (
        KX108ProofBoundaryComposition()
        .compose(boundaries())
    )

    assert (
        result["boundary_composition_status"]
        == "COMPOSED"
    )

    assert result["boundary_count"] == 6


def test_missing_boundary_rejected():

    candidate = boundaries()
    candidate.pop("semantic")

    result = (
        KX108ProofBoundaryComposition()
        .compose(candidate)
    )

    assert (
        result["boundary_composition_status"]
        == "REJECTED"
    )


def test_boundary_failure_rejects_composition():

    candidate = boundaries()

    candidate[
        "context"
    ][
        "context_authority_boundary_status"
    ] = "REJECTED"

    result = (
        KX108ProofBoundaryComposition()
        .compose(candidate)
    )

    assert (
        result["boundary_composition_status"]
        == "REJECTED"
    )


def test_authority_escalation_rejects_composition():

    candidate = boundaries()

    candidate[
        "cognition"
    ]["execution_authority"] = True

    result = (
        KX108ProofBoundaryComposition()
        .compose(candidate)
    )

    assert (
        result["boundary_composition_status"]
        == "REJECTED"
    )


def test_composition_never_merges_authority():

    result = (
        KX108ProofBoundaryComposition()
        .compose(boundaries())
    )

    assert result["authority_merged"] is False
    assert result["authority_elevated"] is False
    assert result["composition_authority"] is False
    assert result["emits_act"] is False
