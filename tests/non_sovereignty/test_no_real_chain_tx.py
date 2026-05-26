"""
Non-sovereignty: no real chain transactions. Simulation only.
"""
import pytest
from periphery.blockchain.transaction_simulator import simulate_transaction


def test_simulate_never_broadcasts():
    r = simulate_transaction("ns_tx1", "mainnet", "TRANSFER")
    assert r.broadcast_attempted is False
    assert r.real_tx_sent is False


def test_simulate_testnet_no_broadcast():
    r = simulate_transaction("ns_tx2", "sepolia", "CALL")
    assert r.real_tx_sent is False
    assert r.simulation_status == "DRY_RUN_ONLY"


def test_simulate_any_chain_no_real_tx():
    for chain in ("mainnet", "polygon", "bsc", "avalanche", "testnet"):
        r = simulate_transaction(f"ns_tx_{chain}", chain, "TRANSFER")
        assert r.real_tx_sent is False, f"real_tx_sent must be False for {chain}"
