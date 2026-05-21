"""
Non-sovereignty: no smart contract deployment without audit. No real deploy in V4.
"""
import pytest
from periphery.blockchain.smart_contract_risk_gate import evaluate_smart_contract_risk
from periphery.blockchain.blockchain_action_classifier import classify_blockchain_action, BlockchainActionClass


def test_deploy_without_audit_blocked():
    r = evaluate_smart_contract_risk("ns_sc1", "DEPLOY", has_audit=False)
    assert r.gate == "BLOCK"
    assert r.deploy_blocked is True


def test_deploy_action_class_blocked():
    r = classify_blockchain_action("ns_sc2", BlockchainActionClass.SMART_CONTRACT_DEPLOY)
    assert r.gate == "BLOCK"
    assert r.real_chain_action_allowed is False


def test_deploy_with_audit_still_requires_review():
    r = evaluate_smart_contract_risk("ns_sc3", "DEPLOY", has_audit=True, is_verified=True)
    assert r.deploy_blocked is False
