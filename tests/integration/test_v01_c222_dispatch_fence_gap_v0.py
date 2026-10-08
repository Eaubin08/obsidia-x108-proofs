"""C2.22 simulated revocation after check never permits dispatch."""
from periphery.enterprise_durable_revocation_ledger_v0 import DurableDelegationLedgerV0
from periphery.enterprise_dispatch_fence_gap_audit_v0 import inspect_dispatch_fence_v0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")

def test_precheck_can_be_stale_after_revocation(tmp_path):
    ledger=DurableDelegationLedgerV0(tmp_path/"ledger.db")
    ledger.register_fixture(SCOPE)
    verdict=inspect_dispatch_fence_v0(
        ledger=ledger,scope=SCOPE,generation=0,nonce="c222-initial-check-0001")
    assert verdict["ledger_observation"]=="CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    assert verdict["reason"]=="C222_NO_ATOMIC_REVOCATION_DISPATCH_FENCE"
    assert ledger.revoke(SCOPE) is True
    assert verdict["egress_allowed"] is False
    assert verdict["dispatch_attempted"] is False
    assert ledger.check_and_consume_fixture(
        SCOPE,generation=0,nonce="c222-after-revoke-0001",
        evidence_verified=True)=="BLOCK:C23_REVOKED"

def test_revoked_before_check_blocks(tmp_path):
    ledger=DurableDelegationLedgerV0(tmp_path/"ledger.db")
    ledger.register_fixture(SCOPE)
    ledger.revoke(SCOPE)
    v=inspect_dispatch_fence_v0(
        ledger=ledger,scope=SCOPE,generation=0,nonce="c222-revoked-0000001")
    assert v["reason"]=="C222_LEDGER_REJECTED"
    assert v["ledger_observation"]=="BLOCK:C23_REVOKED"
    assert v["dispatch_attempted"] is False

def test_untrusted_dispatch_hook_never_called(tmp_path):
    ledger=DurableDelegationLedgerV0(tmp_path/"ledger.db")
    ledger.register_fixture(SCOPE)
    def forbidden():
        raise AssertionError("No dispatch hook should be called")
    v=inspect_dispatch_fence_v0(
        ledger=ledger,scope=SCOPE,generation=0,
        nonce="c222-hook-000000001",post_check_hook=forbidden)
    assert v["reason"]=="C222_CALLER_HOOK_NOT_TRUSTED"
    assert v["dispatch_attempted"] is False
    assert ledger.check_and_consume_fixture(
        SCOPE,generation=0,nonce="c222-hook-000000001",
        evidence_verified=True)=="CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
