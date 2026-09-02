from scripts.kernel.kernel_bridge_validator_v1 import (
    KernelBridgeValidator,
)


def valid_receipt():

    return {
        "provider_id": "brody",
        "invocation_id": "mission-001",
        "result_ref": "runtime-001",
    }


def test_valid_bridge_validation():

    validator = KernelBridgeValidator()

    result = validator.validate(
        valid_receipt()
    )

    assert result.status == "VALIDATED"


def test_provider_verification():

    validator = KernelBridgeValidator()

    result = validator.validate(
        valid_receipt()
    )

    assert result.provider_verified is True


def test_runtime_verification():

    validator = KernelBridgeValidator()

    result = validator.validate(
        valid_receipt()
    )

    assert result.runtime_verified is True


def test_no_decision_output():

    validator = KernelBridgeValidator()

    result = validator.validate(
        valid_receipt()
    )

    assert result.decision is None


def test_kernel_boundary():

    status = KernelBridgeValidator().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
