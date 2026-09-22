from scripts.kernel.kx108_recursive_meta_validation_boundary_v1 import (
    KX108RecursiveMetaValidationBoundary,
)


def valid_governance():
    return {
        "governance_status": "COMPLETED",
        "governance_authority": False,
        "decision_authority": False,
    }


def test_validation_passes():
    result = KX108RecursiveMetaValidationBoundary().validate(
        valid_governance()
    )
    assert result["validation_status"] == "VALIDATED"


def test_missing_governance_rejected():
    result = KX108RecursiveMetaValidationBoundary().validate({})
    assert result["validation_status"] == "REJECTED"


def test_governance_authority_rejected():
    state = valid_governance()
    state["governance_authority"] = True
    result = KX108RecursiveMetaValidationBoundary().validate(state)
    assert result["validation_status"] == "REJECTED"


def test_decision_authority_rejected():
    state = valid_governance()
    state["decision_authority"] = True
    result = KX108RecursiveMetaValidationBoundary().validate(state)
    assert result["validation_status"] == "REJECTED"


def test_kernel_integrity():
    status = KX108RecursiveMetaValidationBoundary().status()
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
