from scripts.kernel.kx108_operational_loop_contract_v1 import (
    KX108OperationalLoopContract,
)

from scripts.kernel.kx108_operational_loop_state_v1 import (
    KX108OperationalLoopState,
)

from scripts.kernel.kx108_operational_loop_receipt_v1 import (
    KX108OperationalLoopReceiptBuilder,
)

from scripts.kernel.kx108_operational_loop_audit_v1 import (
    KX108OperationalLoopAudit,
)


def test_full_operational_loop_chain():

    contract = KX108OperationalLoopContract()

    start = contract.create_loop(
        {
            "context": "INITIAL",
        }
    )

    assert (
        start["loop_status"]
        == "OBSERVATION_ACCEPTED"
    )


    state_machine = KX108OperationalLoopState()

    transition = state_machine.transition(
        "DECISION_PENDING"
    )

    assert (
        transition["transition_status"]
        == "ACCEPTED"
    )


    receipt = (
        KX108OperationalLoopReceiptBuilder()
        .create(
            transition,
            "OBSERVATION",
            "DECISION_PENDING",
        )
    )


    audit = KX108OperationalLoopAudit().audit(
        state_machine.status(),
        receipt.to_dict(),
    )


    assert (
        audit["audit_status"]
        == "PASSED"
    )


def test_state_machine_binding():

    state = KX108OperationalLoopState()

    result = state.transition(
        "DECISION_PENDING"
    )

    assert (
        result["state"]
        == "DECISION_PENDING"
    )


def test_receipt_binding():

    receipt = (
        KX108OperationalLoopReceiptBuilder()
        .create(
            {
                "transition_status":
                    "ACCEPTED",
                "state":
                    "DECISION_PENDING",
            },
            "OBSERVATION",
            "DECISION_PENDING",
        )
    )

    assert (
        receipt.next_state
        == "DECISION_PENDING"
    )


def test_audit_binding():

    result = KX108OperationalLoopAudit().audit(
        {
            "state":
                "DECISION_PENDING",
        },
        {
            "receipt_id":
                "kx108-operational-loop-receipt-v1",
            "transition":
                "DECISION_PENDING",
            "next_state":
                "DECISION_PENDING",
        },
    )

    assert (
        result["audit_status"]
        == "PASSED"
    )


def test_final_kernel_integrity():

    contract_status = (
        KX108OperationalLoopContract()
        .status()
    )

    state_status = (
        KX108OperationalLoopState()
        .status()
    )

    audit_status = (
        KX108OperationalLoopAudit()
        .status()
    )

    assert (
        contract_status["memory_write"]
        is False
    )

    assert (
        state_status["kernel_mutation"]
        is False
    )

    assert (
        audit_status["kernel_mutation"]
        is False
    )
