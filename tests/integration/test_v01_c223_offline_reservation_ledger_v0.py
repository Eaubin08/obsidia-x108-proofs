"""C2.23 local-only reservation, replay, and revocation tests."""
from concurrent.futures import ThreadPoolExecutor
from periphery.enterprise_offline_atomic_reservation_ledger_v0 import OfflineReservationLedgerV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c223-idempotency-key-0001"
NONCE="c223-proof-nonce-000001"

def test_reservation_then_revocation_persists(tmp_path):
    path=tmp_path/"reservations.db"
    ledger=OfflineReservationLedgerV0(path)
    ledger.enroll_fixture(SCOPE)
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    assert ledger.inspect(KEY)=="RESERVED_NO_EXECUTION"
    assert ledger.revoke(SCOPE)
    restarted=OfflineReservationLedgerV0(path)
    assert restarted.inspect(KEY)=="INVALIDATED"
    assert restarted.reserve_fixture(scope=SCOPE,generation=0,nonce="c223-proof-nonce-000002",
        idempotency_key="c223-idempotency-key-0002")=="BLOCK:C223_REVOKED"

def test_concurrent_duplicate_reservations_at_most_once(tmp_path):
    path=tmp_path/"reservations.db"
    OfflineReservationLedgerV0(path).enroll_fixture(SCOPE)
    def reserve(_):
        return OfflineReservationLedgerV0(path).reserve_fixture(
            scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(reserve,range(24)))
    assert results.count("RESERVED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY")==1
    assert results.count("BLOCK:C223_REPLAY_OR_IDEMPOTENCY_DUPLICATE")==23

def test_same_nonce_new_key_and_same_key_new_nonce_both_block(tmp_path):
    ledger=OfflineReservationLedgerV0(tmp_path/"reservations.db")
    ledger.enroll_fixture(SCOPE)
    ledger.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,
        idempotency_key="c223-another-idempotency")=="BLOCK:C223_REPLAY_OR_IDEMPOTENCY_DUPLICATE"
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,nonce="c223-another-proof-nonce",
        idempotency_key=KEY)=="BLOCK:C223_REPLAY_OR_IDEMPOTENCY_DUPLICATE"

def test_wrong_generation_and_other_organization(tmp_path):
    ledger=OfflineReservationLedgerV0(tmp_path/"reservations.db")
    ledger.enroll_fixture(SCOPE)
    assert ledger.reserve_fixture(scope=SCOPE,generation=1,nonce=NONCE,
        idempotency_key=KEY)=="BLOCK:C223_STALE_GENERATION"
    assert ledger.reserve_fixture(scope=("org-b",*SCOPE[1:]),generation=0,
        nonce=NONCE,idempotency_key=KEY)=="BLOCK:C223_SCOPE_UNKNOWN"
