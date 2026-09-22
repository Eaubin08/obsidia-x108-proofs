from scripts.kernel.kx108_proof_state_validation_v1 import (
    KX108ProofStateValidator,
)


def valid_states():

    return [
        {
            "meta_domain": "SYSTEM",
            "state": "validated",
        },
        {
            "meta_domain": "ENVIRONMENT",
            "state": "validated",
        },
        {
            "meta_domain": "OPERATIONAL",
            "state": "validated",
        },
    ]


def test_valid_states_are_validated():

    result = KX108ProofStateValidator().validate(
        valid_states()
    )

    assert (
        result["state_validation_status"]
        == "VALIDATED"
    )

    assert result["state_count"] == 3


def test_valid_states_are_coordinated():

    result = KX108ProofStateValidator().validate(
        valid_states()
    )

    assert result["coordination"] is not None

    assert (
        result["coordination"]["recursive_state_count"]
        == 3
    )


def test_unvalidated_state_rejected():

    states = valid_states()
    states[1]["state"] = "pending"

    result = KX108ProofStateValidator().validate(
        states
    )

    assert (
        result["state_validation_status"]
        == "REJECTED"
    )

    assert result["checks"]["all_validated"] is False
    assert result["coordination"] is None


def test_empty_state_set_rejected():

    result = KX108ProofStateValidator().validate([])

    assert (
        result["state_validation_status"]
        == "REJECTED"
    )

    assert result["checks"]["non_empty"] is False


def test_state_validation_kernel_integrity():

    status = KX108ProofStateValidator().status()

    assert status["authority"] is False
    assert status["decision_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
