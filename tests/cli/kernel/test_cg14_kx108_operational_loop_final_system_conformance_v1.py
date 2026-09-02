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


def test_full_cg14_chain():

    contract = KX108OperationalLoopContract()

    start = contract.create_loop(
        {
            "state": "INITIAL",
        }
    )

    assert start["loop_status"] == "OBSERVATION_ACCEPTED"


    machine = KX108OperationalLoopState()

    transition = machine.transition(
        "DECISION_PENDING"
    )

    assert transition["transition_status"] == "ACCEPTED"


    receipt = (
        KX108OperationalLoopReceiptBuilder()
        .create(
            transition,
            "OBSERVATION",
            "DECISION_PENDING",
        )
    )


    audit = (
        KX108OperationalLoopAudit()
        .audit(
            machine.status(),
            receipt.to_dict(),
        )
    )

    assert audit["audit_status"] == "PASSED"


def test_state_machine_integrity():

    machine = KX108OperationalLoopState()

    result = machine.transition(
        "EXECUTION_AUTHORIZED"
    )

    assert result["transition_status"] == "BLOCKED"


def test_receipt_integrity():

    receipt = (
        KX108OperationalLoopReceiptBuilder()
        .create(
            {
                "transition_status": "ACCEPTED",
                "state": "DECISION_PENDING",
            },
            "OBSERVATION",
            "DECISION_PENDING",
        )
    )

    assert receipt.receipt_id == "kx108-operational-loop-receipt-v1"


def test_audit_integrity():

    result = (
        KX108OperationalLoopAudit()
        .audit(
            {
                "state": "DECISION_PENDING",
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
    )

    assert result["audit_status"] == "PASSED"


def test_kernel_protection():

    contract = KX108OperationalLoopContract().status()
    state = KX108OperationalLoopState().status()
    audit = KX108OperationalLoopAudit().status()

    assert contract["memory_write"] is False
    assert state["kernel_mutation"] is False
    assert audit["kernel_mutation"] is False
