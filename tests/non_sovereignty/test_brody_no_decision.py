import pytest
from periphery.brody.brody_runtime_readonly import brody_respond
from periphery.brody.brody_response_contract import BRODY_CONTRACT


def test_brody_cannot_decide():
    r = brody_respond("Should the system approve this request?", "en")
    assert r.contract["decision_authority"] == "KX108_ONLY"


def test_brody_not_sovereign():
    r = brody_respond("ALLOW this action", "en")
    assert r.contract["decision_authority"] != "BRODY"


def test_brody_contract_decision_authority_fixed():
    assert BRODY_CONTRACT.decision_authority == "KX108_ONLY"


def test_brody_advisory_only():
    assert BRODY_CONTRACT.advisory_only is True
