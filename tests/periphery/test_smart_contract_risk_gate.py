import pytest
from periphery.blockchain.smart_contract_risk_gate import evaluate_smart_contract_risk


def test_deploy_without_audit_blocked():
    r = evaluate_smart_contract_risk("sc1", "DEPLOY", has_audit=False)
    assert r.gate == "BLOCK"
    assert r.deploy_blocked is True
    assert "DEPLOY_WITHOUT_AUDIT" in r.risk_flags


def test_deploy_with_audit_allowed():
    r = evaluate_smart_contract_risk("sc2", "DEPLOY", has_audit=True, is_verified=True)
    assert r.gate == "ALLOW"
    assert r.deploy_blocked is False


def test_unbounded_approval_hold():
    r = evaluate_smart_contract_risk("sc3", "APPROVE", has_unbounded_approval=True)
    assert r.gate == "HOLD"
    assert "UNBOUNDED_TOKEN_APPROVAL" in r.risk_flags


def test_read_view_no_flags():
    r = evaluate_smart_contract_risk("sc4", "VIEW", is_verified=True)
    assert r.gate == "ALLOW"


def test_dict_fields():
    r = evaluate_smart_contract_risk("sc5", "CALL")
    d = r.to_dict()
    assert "gate" in d and "deploy_blocked" in d and "risk_flags" in d
