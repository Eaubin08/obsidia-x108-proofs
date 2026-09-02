from scripts.kernel.kx108_operational_loop_state_v1 import (
    KX108OperationalLoopState,
)


def test_initial_state():

    state = KX108OperationalLoopState()

    assert (
        state.status()["state"]
        == "OBSERVATION"
    )


def test_valid_transition():

    state = KX108OperationalLoopState()

    result = state.transition(
        "DECISION_PENDING"
    )

    assert (
        result["transition_status"]
        == "ACCEPTED"
    )


def test_invalid_transition_blocked():

    state = KX108OperationalLoopState()

    result = state.transition(
        "EXECUTION_AUTHORIZED"
    )

    assert (
        result["transition_status"]
        == "BLOCKED"
    )


def test_full_cycle_step():

    state = KX108OperationalLoopState()

    sequence = [
        "DECISION_PENDING",
        "DECISION_VALIDATED",
        "EXECUTION_AUTHORIZED",
        "ACT_EVALUATED",
        "FEEDBACK_RECEIVED",
        "CONTEXT_UPDATED",
        "OBSERVATION",
    ]

    for step in sequence:
        result = state.transition(step)
        assert (
            result["transition_status"]
            == "ACCEPTED"
        )


def test_kernel_protection():

    status = KX108OperationalLoopState().status()

    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
