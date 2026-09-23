"""
V5A Non-Sovereignty Test: Transaction simulator never broadcasts.
Every simulation result must have broadcast_attempted=False, real_tx_sent=False.
"""
import pytest
from periphery.blockchain.transaction_simulator import simulate_transaction


def test_simulate_read_only_never_broadcasts():
    """READ_ONLY transactions are simulated — never broadcast."""
    r = simulate_transaction(
        tx_id="test_ro",
        chain_id="ethereum",
        action_type="READ_ONLY",
    )
    assert r.simulated is True
    assert r.broadcast_attempted is False
    assert r.real_tx_sent is False
    assert r.simulation_status == "DRY_RUN_ONLY"


def test_simulate_deploy_never_broadcasts():
    """DEPLOY transactions are high-risk simulated — never broadcast."""
    r = simulate_transaction(
        tx_id="test_deploy",
        chain_id="polygon",
        action_type="DEPLOY",
    )
    assert r.simulated is True
    assert r.broadcast_attempted is False
    assert r.real_tx_sent is False
    assert "CONTRACT_DEPLOY_HIGH_RISK" in r.risk_flags
    assert r.risk_score >= 0.9


def test_simulate_high_value_never_broadcasts():
    """High-value transactions are flagged — never broadcast."""
    r = simulate_transaction(
        tx_id="test_high",
        chain_id="polygon",
        action_type="TRANSFER",
        value_eth=10.0,
    )
    assert r.broadcast_attempted is False
    assert r.real_tx_sent is False
    assert "HIGH_VALUE_TRANSFER" in r.risk_flags


def test_simulate_mainnet_blocked():
    """Mainnet transactions are blocked with risk_score=1.0 — never broadcast."""
    r = simulate_transaction(
        tx_id="test_mainnet",
        chain_id="ethereum",
        action_type="TRANSFER",
        value_eth=0.1,
    )
    assert r.broadcast_attempted is False
    assert r.real_tx_sent is False
    assert r.risk_score == 1.0
    assert "MAINNET_BLOCKED_V4" in r.risk_flags


def test_all_chain_ids_never_broadcast():
    """Every chain ID must result in broadcast_attempted=False, real_tx_sent=False."""
    chain_ids = ["ethereum", "polygon", "bsc", "avalanche", "arbitrum", "optimism"]
    for chain_id in chain_ids:
        r = simulate_transaction(
            tx_id=f"test_{chain_id}",
            chain_id=chain_id,
            action_type="READ_ONLY",
        )
        assert r.broadcast_attempted is False, f"Chain {chain_id}: broadcast_attempted must be False"
        assert r.real_tx_sent is False, f"Chain {chain_id}: real_tx_sent must be False"
