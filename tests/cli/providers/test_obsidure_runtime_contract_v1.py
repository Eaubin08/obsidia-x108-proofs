import pytest

from scripts.providers.obsidure_runtime_contract_v1 import (
    ObsidureRuntimeRequest,
    ObsidureRuntimeResult,
    validate_request,
    ObsidureRuntimeContractError,
)


def test_valid_request():

    request = ObsidureRuntimeRequest(
        mission_id="mission-001",
        capability="proof",
        proof_target="theorem",
        payload={}
    )

    assert validate_request(request) is True


def test_missing_proof_target_blocked():

    request = ObsidureRuntimeRequest(
        mission_id="mission-001",
        capability="proof",
        proof_target="",
        payload={}
    )

    with pytest.raises(
        ObsidureRuntimeContractError
    ):
        validate_request(request)


def test_result_invariants():

    result = ObsidureRuntimeResult(
        mission_id="mission-001"
    )

    assert result.decision_authority is False
    assert result.execution_authority is False
    assert result.memory_write is False
    assert result.kernel_mutation is False
    assert result.emits_act is False


def test_verified_result():

    result = ObsidureRuntimeResult(
        mission_id="mission-001",
        proof={
            "status":"verified"
        }
    )

    data = result.to_dict()

    assert data["verified"] is True


def test_no_decision_output():

    result = ObsidureRuntimeResult(
        mission_id="mission-001"
    )

    data = result.to_dict()

    assert "decision" not in data
