import pytest

from scripts.providers.brody_runtime_contract_v1 import (
    BrodyRuntimeRequest,
    BrodyRuntimeResult,
    validate_request,
    BrodyRuntimeContractError,
)


def test_valid_request():

    request = BrodyRuntimeRequest(
        mission_id="mission-001",
        capability="analysis",
        payload={}
    )

    assert validate_request(request) is True


def test_missing_mission_blocked():

    request = BrodyRuntimeRequest(
        mission_id="",
        capability="analysis",
        payload={}
    )

    with pytest.raises(
        BrodyRuntimeContractError
    ):
        validate_request(request)


def test_result_invariants():

    result = BrodyRuntimeResult(
        mission_id="mission-001"
    )

    assert result.decision_authority is False
    assert result.execution_authority is False
    assert result.memory_write is False
    assert result.kernel_mutation is False
    assert result.emits_act is False


def test_result_export():

    result = BrodyRuntimeResult(
        mission_id="mission-001",
        result={
            "text":"hello"
        }
    )

    data = result.to_dict()

    assert data["provider_id"] == "brody"


def test_no_decision_field():

    result = BrodyRuntimeResult(
        mission_id="mission-001"
    )

    data = result.to_dict()

    assert "decision" not in data
