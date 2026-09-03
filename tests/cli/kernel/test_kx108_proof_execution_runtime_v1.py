from scripts.kernel.kx108_proof_execution_runtime_v1 import (
    KX108ProofExecutionRuntime,
)


def flow_output():

    return {
        "flow_status":
            "COMPLETED",

        "execution": {
            "session": {
                "status":
                    "COMPLETED",
            },

            "envelope": {
                "provider_id":
                    "brody",

                "runtime_id":
                    "runtime-cg73",

                "status":
                    "SEALED",

                "decision_authority":
                    False,

                "execution_authority":
                    False,

                "memory_write":
                    False,

                "kernel_mutation":
                    False,

                "emits_act":
                    False,
            },
        },
    }


def test_execution_runtime_validated():

    result = (
        KX108ProofExecutionRuntime()
        .validate(flow_output())
    )

    assert (
        result["execution_runtime_status"]
        == "VALIDATED"
    )


def test_execution_runtime_has_runtime_ref():

    result = (
        KX108ProofExecutionRuntime()
        .validate(flow_output())
    )

    assert result["runtime_ref"] == "runtime-cg73"


def test_unsealed_execution_rejected():

    candidate = flow_output()

    candidate[
        "execution"
    ][
        "envelope"
    ][
        "status"
    ] = "CREATED"

    result = (
        KX108ProofExecutionRuntime()
        .validate(candidate)
    )

    assert result["execution_runtime_status"] == "REJECTED"


def test_execution_authority_escalation_rejected():

    candidate = flow_output()

    candidate[
        "execution"
    ][
        "envelope"
    ][
        "execution_authority"
    ] = True

    result = (
        KX108ProofExecutionRuntime()
        .validate(candidate)
    )

    assert result["execution_runtime_status"] == "REJECTED"


def test_execution_runtime_creates_no_authority():

    result = (
        KX108ProofExecutionRuntime()
        .validate(flow_output())
    )

    assert result["runtime_authority"] is False
    assert result["execution_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
