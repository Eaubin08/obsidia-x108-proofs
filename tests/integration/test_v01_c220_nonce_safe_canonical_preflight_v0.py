"""C2.20 complete canonical producer fixture through preflight, no nonce burn."""
import importlib.util
from pathlib import Path
from periphery.enterprise_nonce_safe_canonical_preflight_v0 import inspect_nonce_safe_canonical_preflight_v0
from periphery.enterprise_durable_revocation_ledger_v0 import DurableDelegationLedgerV0
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
from scripts import obsidia_kx108_decision_store as store

def test_real_kx108_record_and_local_ticket_block_without_consuming_nonce(tmp_path):
    path=Path(__file__).with_name("test_world_action_pre_execution_v0.py")
    spec=importlib.util.spec_from_file_location("fixture_c220",path)
    fixture=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    request=fixture.build_request()
    approval=fixture.build_approval(request)
    produced=fixture.run(tmp_path,request)
    assert produced.x108_gate=="ALLOW"
    record=store.load_kx108_decision_record(produced.decision_record_id,tmp_path/"decisions")
    ticket=issue_sovereign_ticket(action_id=request["request_id"],
        os3_ticket_id="fixture-os3",x108_gate="ALLOW",
        scope=request["required_scope"],autonomy_level=3,
        world_call_class="REVERSIBLE_WORLD_CALL")
    scope=("org-a","delegate-a","GMAIL","gmail:send")
    ledger=DurableDelegationLedgerV0(tmp_path/"ledger.db")
    ledger.register_fixture(scope)
    nonce="c220-fixture-nonce-001"
    result=inspect_nonce_safe_canonical_preflight_v0(
        request=request,approval=approval,record=record,ticket=ticket,
        delegation_inputs={"revocation_ledger":ledger,"nonce":nonce})
    assert result["reason"]=="C220_SOVEREIGN_BLOCKED:C28_TICKET_NOT_AUTHENTICATED_TO_KX108_RECORD"
    assert result["nonce_consumed"] is False
    assert result["egress_allowed"] is False
    # Proof that C2.20 has NOT burned the nonce even after upstream BLOCK:
    assert ledger.check_and_consume_fixture(
        scope,generation=0,nonce=nonce,evidence_verified=True
    )=="CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"

def test_incomplete_context_never_consumes_nonce():
    result=inspect_nonce_safe_canonical_preflight_v0(
        request=None,approval=None,record=None,ticket=None,delegation_inputs=None)
    assert result["status"]=="BLOCK"
    assert result["nonce_consumed"] is False
