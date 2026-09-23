import pytest
from periphery.blockchain.transaction_simulator import simulate_transaction


def test_simulation_never_broadcasts():
    r = simulate_transaction("tx1", "testnet", "TRANSFER")
    assert r.broadcast_attempted is False
    assert r.real_tx_sent is False
    assert r.simulated is True


def test_mainnet_flagged_high_risk():
    r = simulate_transaction("tx2", "mainnet", "TRANSFER")
    assert r.risk_score == 1.0
    assert "MAINNET_BLOCKED_V4" in r.risk_flags


def test_deploy_is_high_risk():
    r = simulate_transaction("tx3", "testnet", "DEPLOY")
    assert r.risk_score >= 0.9
    assert "CONTRACT_DEPLOY_HIGH_RISK" in r.risk_flags


def test_simulation_status_dryrun():
    r = simulate_transaction("tx4", "sepolia", "TRANSFER", value_eth=0.1)
    assert r.simulation_status == "DRY_RUN_ONLY"


def test_dict_fields():
    r = simulate_transaction("tx5", "testnet", "CALL")
    d = r.to_dict()
    assert "tx_id" in d and "simulated" in d and "real_tx_sent" in d
