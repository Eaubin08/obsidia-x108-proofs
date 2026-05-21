import pytest
from periphery.brody.brody_response_contract import BRODY_CONTRACT, BrodyResponseContract


def test_singleton_readonly():
    assert BRODY_CONTRACT.readonly is True


def test_singleton_emits_act_false():
    assert BRODY_CONTRACT.emits_act is False


def test_singleton_emits_verdict_false():
    assert BRODY_CONTRACT.emits_verdict is False


def test_singleton_decision_authority():
    assert BRODY_CONTRACT.decision_authority == "KX108_ONLY"


def test_validate_passes():
    BRODY_CONTRACT.validate()


def test_invalid_contract_raises():
    bad = BrodyResponseContract(
        readonly=False,
        advisory_only=True,
        emits_act=False,
        emits_verdict=False,
        decision_authority="KX108_ONLY",
        memory_write=False,
        kernel_mutation=False,
    )
    with pytest.raises(AssertionError):
        bad.validate()
