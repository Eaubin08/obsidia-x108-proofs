import pytest
from periphery.blockchain.bridge_risk_gate import evaluate_bridge_risk


def test_mainnet_bridge_blocked():
    r = evaluate_bridge_risk("br1", "mainnet", "polygon_mainnet")
    assert r.gate == "BLOCK"
    assert r.real_bridge_allowed is False
    assert "MAINNET_BRIDGE_BLOCKED_V4" in r.risk_flags


def test_unevaluated_bridge_hold():
    r = evaluate_bridge_risk("br2", "testnet", "mumbai", bridge_audited=False)
    assert r.gate == "HOLD"
    assert "BRIDGE_RISK_UNEVALUATED" in r.risk_flags


def test_real_bridge_never_allowed():
    r = evaluate_bridge_risk("br3", "goerli", "mumbai", bridge_audited=True, liquidity_verified=True)
    assert r.real_bridge_allowed is False


def test_dict_fields():
    r = evaluate_bridge_risk("br4", "testnet", "testnet2")
    d = r.to_dict()
    assert "gate" in d and "risk_flags" in d and "real_bridge_allowed" in d
