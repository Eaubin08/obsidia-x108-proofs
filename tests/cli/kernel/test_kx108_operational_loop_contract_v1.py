from scripts.kernel.kx108_operational_loop_contract_v1 import (
    KX108OperationalLoopContract,
)


def test_observation_start():

    result = KX108OperationalLoopContract().create_loop(
        {
            "state": "INITIAL",
        }
    )

    assert (
        result["loop_status"]
        == "OBSERVATION_ACCEPTED"
    )


def test_next_state_decision():

    result = KX108OperationalLoopContract().create_loop(
        {
            "state": "INITIAL",
        }
    )

    assert (
        result["next_state"]
        == "DECISION"
    )


def test_feedback_return():

    result = KX108OperationalLoopContract().update_feedback(
        {
            "result": "OK",
        }
    )

    assert (
        result["loop_status"]
        == "FEEDBACK_RECEIVED"
    )


def test_no_kernel_mutation():

    status = KX108OperationalLoopContract().status()

    assert status["kernel_mutation"] is False


def test_no_memory_write():

    status = KX108OperationalLoopContract().status()

    assert status["memory_write"] is False
