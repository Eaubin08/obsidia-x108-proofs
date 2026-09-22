from scripts.kernel.kernel_bridge_contract_v1 import (
    KernelBridgeContract,
)


def test_valid_receipt():

    bridge = KernelBridgeContract()

    result = bridge.validate_receipt(
        {
            "provider_id": "brody",
            "invocation_id": "mission-001",
            "result_ref": "runtime-001",
        }
    )

    assert result.bridge_status == "VALIDATED"


def test_invalid_receipt():

    bridge = KernelBridgeContract()

    result = bridge.validate_receipt(
        {
            "provider_id": "brody",
        }
    )

    assert result.bridge_status == "REJECTED"


def test_no_kernel_access():

    bridge = KernelBridgeContract()

    result = bridge.validate_receipt(
        {
            "provider_id": "obsidure",
            "invocation_id": "mission-002",
            "result_ref": "runtime-002",
        }
    )

    assert result.kernel_access is False


def test_no_decision_output():

    bridge = KernelBridgeContract()

    result = bridge.validate_receipt(
        {
            "provider_id": "brody",
            "invocation_id": "mission-003",
            "result_ref": "runtime-003",
        }
    )

    assert result.decision is None


def test_authority_boundary():

    status = KernelBridgeContract().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
