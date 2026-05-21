"""
V5A Internal Flow: Blockchain security dry-run demonstration.
Demonstrates: Wallet security gate, transaction simulator (dry-run),
signature boundary, smart contract risk gate, token policy, bridge risk gate.
All blockchain operations are simulated. No real chain interaction.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from periphery.blockchain.wallet_security_gate import evaluate_wallet_request
from periphery.blockchain.transaction_simulator import simulate_transaction
from periphery.blockchain.signature_boundary import evaluate_signature_request, assert_no_private_key_in_payload
from periphery.blockchain.smart_contract_risk_gate import evaluate_smart_contract_risk
from periphery.blockchain.token_policy import evaluate_token_policy
from periphery.blockchain.bridge_risk_gate import evaluate_bridge_risk
from periphery.blockchain.oracle_freshness_gate import evaluate_oracle_freshness
from periphery.blockchain.chain_context import build_chain_context
from periphery.blockchain.blockchain_action_classifier import BlockchainActionClass


def run(action_id: str = "v5a_bc_001", domain: str = "bank") -> dict:
    # Wallet security — no connection, no private key
    wallet = evaluate_wallet_request(
        request_id=action_id,
        request_type="balance_check",
        payload={"action_id": action_id},
    )

    # Transaction simulator — dry-run only, never broadcasts
    sim = simulate_transaction(
        tx_id=action_id,
        chain_id="ethereum",
        action_type="READ_ONLY",
        value_eth=0.0,
    )

    # Signature boundary — blocks all signing
    sig = evaluate_signature_request(
        request_id=action_id,
        signature_type="SIGN_MESSAGE",
    )

    # Assert no private key in payload
    try:
        assert_no_private_key_in_payload({"safe": "data"})
        payload_clean = True
    except AssertionError:
        payload_clean = False

    # Smart contract risk gate
    sc = evaluate_smart_contract_risk(
        contract_id=action_id,
        action="DEPLOY",
        has_audit=False,
    )

    # Token policy — Gencoin is NOT a token
    token = evaluate_token_policy(
        token_id="gencoin_internal",
        action="MINT",
        is_gencoin=True,
    )

    # Bridge risk gate
    bridge = evaluate_bridge_risk(
        bridge_id=action_id,
        source_chain="ethereum",
        dest_chain="polygon",
    )

    # Oracle freshness
    oracle = evaluate_oracle_freshness(
        oracle_id=action_id,
        last_update_iso=datetime.now(timezone.utc).isoformat(),
    )

    # Chain context
    chain = build_chain_context("1")

    return {
        "action_id": action_id,
        "wallet_blocked": wallet.blocked,
        "wallet_real_access": wallet.real_wallet_access_allowed,
        "simulator_real_tx_sent": sim.real_tx_sent,
        "simulator_broadcast": sim.broadcast_attempted,
        "simulator_dry_run": sim.simulated,
        "signature_blocked": sig.blocked,
        "signature_signing": sig.signing_attempted,
        "payload_no_private_key": payload_clean,
        "smart_contract_deploy_blocked": sc.deploy_blocked,
        "smart_contract_gate": sc.gate,
        "token_mint_allowed": token.mint_allowed,
        "token_real_created": token.real_token_created,
        "bridge_real_allowed": bridge.real_bridge_allowed,
        "bridge_gate": bridge.gate,
        "oracle_fresh": oracle.is_fresh,
        "chain_read_only": chain.read_only,
        "chain_real_rpc": chain.real_rpc_connected,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    assert result["wallet_real_access"] is False, "CRITICAL: no real wallet access"
    assert result["simulator_real_tx_sent"] is False, "CRITICAL: no real tx"
    assert result["simulator_broadcast"] is False, "CRITICAL: no broadcast"
    assert result["signature_blocked"] is True, "CRITICAL: signing must be blocked"
    assert result["signature_signing"] is False, "CRITICAL: no signing attempted"
    assert result["smart_contract_deploy_blocked"] is True, "CRITICAL: deploy blocked without audit"
    assert result["token_mint_allowed"] is False, "CRITICAL: Gencoin mint blocked"
    assert result["token_real_created"] is False, "CRITICAL: no real token"
    assert result["bridge_real_allowed"] is False, "CRITICAL: no real bridge"
    assert result["chain_read_only"] is True, "CRITICAL: chain context read-only"
    assert result["chain_real_rpc"] is False, "CRITICAL: no real RPC"
    print("OK blockchain_security_dryrun_flow — all blockchain ops blocked")
