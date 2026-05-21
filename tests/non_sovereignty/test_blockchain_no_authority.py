"""
V5A Non-Sovereignty Test: Blockchain modules never claim authority.
No blockchain module can emit ACT, decide, or claim sovereignty.
"""
import pytest
from periphery.blockchain.wallet_security_gate import WalletSecurityDecision
from periphery.blockchain.transaction_simulator import TransactionSimulationResult
from periphery.blockchain.signature_boundary import SignatureBoundaryDecision
from periphery.blockchain.smart_contract_risk_gate import SmartContractRiskDecision
from periphery.blockchain.token_policy import TokenPolicyDecision
from periphery.blockchain.bridge_risk_gate import BridgeRiskDecision
from periphery.blockchain.oracle_freshness_gate import OracleFreshnessDecision


def test_wallet_security_no_authority():
    """WalletSecurityDecision has no decision_authority field — it defers to X108."""
    d = WalletSecurityDecision(
        request_id="test", request_type="read",
        blocked=False, reason="test",
    )
    assert not hasattr(d, "decision_authority") or getattr(d, "decision_authority", "KX108_ONLY") == "KX108_ONLY"


def test_transaction_simulator_no_authority():
    """TransactionSimulationResult is a simulation only — never broadcasts, never decides."""
    d = TransactionSimulationResult(
        tx_id="test", chain_id="test", action_type="READ_ONLY",
    )
    assert d.simulated is True
    assert d.broadcast_attempted is False
    assert d.real_tx_sent is False
    assert d.simulation_status == "DRY_RUN_ONLY"


def test_signature_boundary_no_authority():
    """SignatureBoundaryDecision blocks signing — never decides governance."""
    d = SignatureBoundaryDecision(
        request_id="test", signature_type="SIGN_MESSAGE",
        blocked=True, reason="test",
    )
    assert d.blocked is True
    assert d.signing_attempted is False
    assert d.key_exposed is False


def test_smart_contract_risk_no_authority():
    """SmartContractRiskDecision recommends BLOCK/HOLD — never allows deploy autonomously."""
    from periphery.blockchain.smart_contract_risk_gate import evaluate_smart_contract_risk
    d = evaluate_smart_contract_risk(
        contract_id="test", action="DEPLOY",
        has_audit=False, is_verified=False,
    )
    assert d.deploy_blocked is True
    assert d.gate == "BLOCK"


def test_token_policy_no_authority():
    """TokenPolicyDecision blocks all mint/deploy — never allows token creation."""
    from periphery.blockchain.token_policy import evaluate_token_policy
    d = evaluate_token_policy(
        token_id="gencoin_test", action="MINT",
        is_gencoin=True,
    )
    assert d.mint_allowed is False
    assert d.real_token_created is False


def test_bridge_risk_no_authority():
    """BridgeRiskDecision blocks mainnet bridges — real_bridge_allowed always False."""
    from periphery.blockchain.bridge_risk_gate import evaluate_bridge_risk
    d = evaluate_bridge_risk(
        bridge_id="test", source_chain="ethereum",
        dest_chain="polygon",
    )
    assert d.real_bridge_allowed is False


def test_oracle_freshness_no_authority():
    """OracleFreshnessDecision checks freshness — never decides on action execution."""
    from periphery.blockchain.oracle_freshness_gate import evaluate_oracle_freshness
    d = evaluate_oracle_freshness(
        oracle_id="test", last_update_iso=None,
    )
    assert d.is_fresh is False
    assert d.gate == "HOLD"
