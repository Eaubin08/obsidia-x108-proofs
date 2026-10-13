"""C2.21 deterministic local SQLite concurrency tests; NO dispatch authority."""
from concurrent.futures import ThreadPoolExecutor
from periphery.enterprise_durable_revocation_ledger_v0 import DurableDelegationLedgerV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")

def test_concurrent_same_nonce_at_most_once(tmp_path):
    path=tmp_path/"ledger.db"
    DurableDelegationLedgerV0(path).register_fixture(SCOPE)
    def use(_):
        return DurableDelegationLedgerV0(path).check_and_consume_fixture(
            SCOPE,generation=0,nonce="c221-shared-nonce-001",evidence_verified=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes=list(pool.map(use,range(24)))
    assert outcomes.count("CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY")==1
    assert outcomes.count("BLOCK:C23_NONCE_REPLAY")==23

def test_revocation_blocks_after_restart(tmp_path):
    path=tmp_path/"ledger.db"
    original=DurableDelegationLedgerV0(path)
    original.register_fixture(SCOPE)
    assert original.revoke(SCOPE)
    reopened=DurableDelegationLedgerV0(path)
    assert reopened.check_and_consume_fixture(
        SCOPE,generation=0,nonce="c221-after-revoke-001",
        evidence_verified=True)=="BLOCK:C23_REVOKED"

def test_revocation_race_never_permits_action(tmp_path):
    path=tmp_path/"ledger.db"
    DurableDelegationLedgerV0(path).register_fixture(SCOPE)
    def attempt(n):
        ledger=DurableDelegationLedgerV0(path)
        if n==0:
            return ("revoke",ledger.revoke(SCOPE))
        return ("check",ledger.check_and_consume_fixture(
            SCOPE,generation=0,nonce=f"c221-race-{n:018d}",
            evidence_verified=True))
    with ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(attempt,range(20)))
    assert ("revoke",True) in results
    for kind,result in results:
        if kind=="check":
            assert result in ("CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY","BLOCK:C23_REVOKED")
    after=DurableDelegationLedgerV0(path)
    assert after.check_and_consume_fixture(
        SCOPE,generation=0,nonce="c221-final-check-001",
        evidence_verified=True)=="BLOCK:C23_REVOKED"

def test_scope_isolation(tmp_path):
    ledger=DurableDelegationLedgerV0(tmp_path/"ledger.db")
    other=("org-b","delegate-a","GMAIL","gmail:send")
    ledger.register_fixture(SCOPE)
    ledger.register_fixture(other)
    ledger.revoke(SCOPE)
    assert ledger.check_and_consume_fixture(
        other,generation=0,nonce="c221-independent-001",
        evidence_verified=True)=="CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    assert ledger.check_and_consume_fixture(
        SCOPE,generation=0,nonce="c221-independent-001",
        evidence_verified=True)=="BLOCK:C23_REVOKED"
