"""C2.4 prove no egress after simulated full proof composition."""
from dataclasses import replace
from datetime import datetime, timezone
from periphery.enterprise_scoped_delegation_proof_v0 import SCHEMA, ScopedDelegationProofV0, sign_fixture_only
from periphery.enterprise_durable_revocation_ledger_v0 import DurableDelegationLedgerV0
from periphery.enterprise_gateway_dryrun_composition_v0 import inspect_fixture_composition_v0
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
from periphery.world_calls.world_call_classifier import WorldCallClass

KEY = bytes(range(32))
SCOPE = ("org-a", "delegate-a", "calendar", "CALENDAR.EVENT.CREATE")

def case(tmp_path):
    ledger = DurableDelegationLedgerV0(tmp_path / "state.db")
    ledger.register_fixture(SCOPE)
    p = ScopedDelegationProofV0(
        SCHEMA, "fixture-issuer", "org-a", "human-a", "delegate-a",
        "calendar", "CALENDAR.EVENT.CREATE", "a"*64,
        "2099-10-08T13:00:00+00:00", "nonce-c24-0000001", ""
    )
    proof = sign_fixture_only(p, secret=KEY)
    verify = dict(
        trusted_issuer_id="fixture-issuer", verifier_secret=KEY,
        organization_id="org-a", principal_id="human-a",
        delegate_id="delegate-a", connector_id="calendar",
        capability_id="CALENDAR.EVENT.CREATE", action_request_hash="a"*64,
        now=datetime(2026,10,8,12,tzinfo=timezone.utc)
    )
    ticket = issue_sovereign_ticket(
        action_id="action-1", os3_ticket_id="os3-fixture",
        x108_gate="ACT", scope="calendar:write", autonomy_level=3,
        world_call_class="REVERSIBLE_WORLD_CALL"
    )
    params = dict(
        proof=proof, verifier_args=verify, ledger=ledger, scope=SCOPE,
        generation=0, nonce=proof.nonce, ticket=ticket,
        world_call_class=WorldCallClass.REVERSIBLE_WORLD_CALL,
        required_scope="calendar:write"
    )
    return ledger, params

def test_valid_fixture_never_grants_egress(tmp_path):
    _, p = case(tmp_path)
    result = inspect_fixture_composition_v0(**p)
    assert result["status"] == "NO_EXECUTION"
    assert result["egress_allowed"] is False
    assert result["kx108_live_verified"] is False

def test_revocation_blocks_even_if_ticket_created(tmp_path):
    ledger, p = case(tmp_path)
    assert ledger.revoke(SCOPE)
    result = inspect_fixture_composition_v0(**p)
    assert result["status"] == "BLOCK"
    assert result["reason"] == "BLOCK:C23_REVOKED"

def test_replay_blocks(tmp_path):
    _, p = case(tmp_path)
    inspect_fixture_composition_v0(**p)
    result = inspect_fixture_composition_v0(**p)
    assert result["reason"] == "BLOCK:C23_NONCE_REPLAY"

def test_forged_proof_blocks_before_consuming_nonce(tmp_path):
    _, p = case(tmp_path)
    bad = dict(p, proof=replace(p["proof"], signature="0"*64))
    result = inspect_fixture_composition_v0(**bad)
    assert result["status"] == "BLOCK"
    assert result["reason"] == "C22_SIGNATURE_INVALID"
    assert inspect_fixture_composition_v0(**p)["status"] == "NO_EXECUTION"

def test_gateway_refuses_forbidden_class(tmp_path):
    _, p = case(tmp_path)
    p["world_call_class"] = WorldCallClass.FORBIDDEN_WORLD_CALL
    result = inspect_fixture_composition_v0(**p)
    assert result["egress_allowed"] is False
    assert result["reason"] == "C25_GATEWAY_PREFLIGHT_DENIED"

def test_hold_denied_without_consuming_nonce(tmp_path):
    _, p = case(tmp_path)
    p["ticket"].x108_gate = "HOLD"
    denied = inspect_fixture_composition_v0(**p)
    assert denied["status"] == "BLOCK"
    assert denied["reason"] == "C25_KX108_ALLOW_NOT_VERIFIED"
    p["ticket"].x108_gate = "ACT"
    assert inspect_fixture_composition_v0(**p)["status"] == "NO_EXECUTION"

def test_block_denied_without_consuming_nonce(tmp_path):
    _, p = case(tmp_path)
    p["ticket"].x108_gate = "BLOCK"
    assert inspect_fixture_composition_v0(**p)["status"] == "BLOCK"
    p["ticket"].x108_gate = "ACT"
    assert inspect_fixture_composition_v0(**p)["status"] == "NO_EXECUTION"

def test_gateway_rejection_does_not_consume_nonce(tmp_path):
    _, p = case(tmp_path)
    p["world_call_class"] = WorldCallClass.FORBIDDEN_WORLD_CALL
    assert inspect_fixture_composition_v0(**p)["reason"] == "C25_GATEWAY_PREFLIGHT_DENIED"
    p["world_call_class"] = WorldCallClass.REVERSIBLE_WORLD_CALL
    assert inspect_fixture_composition_v0(**p)["status"] == "NO_EXECUTION"
