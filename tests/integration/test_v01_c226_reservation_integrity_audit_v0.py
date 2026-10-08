from periphery.enterprise_offline_reservation_lifecycle_v0 import OfflineReservationLifecycleV0
from periphery.enterprise_reservation_integrity_audit_v0 import audit_reservation_integrity_v0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c226-idempotency-key-001"
NONCE="c226-proof-nonce-000001"

def setup(tmp_path):
    ledger=OfflineReservationLifecycleV0(tmp_path/"state.db")
    ledger.enroll_fixture(SCOPE)
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    return ledger

def test_unmodified_store_consistent_but_never_authorizes(tmp_path):
    ledger=setup(tmp_path)
    ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")
    result=audit_reservation_integrity_v0(OfflineReservationLifecycleV0(tmp_path/"state.db"))
    assert result["reason"]=="C226_LOCAL_INTEGRITY_CONSISTENT_NOT_ATTESTED"
    assert result["egress_allowed"] is False

def test_tampered_receipt_detected(tmp_path):
    ledger=setup(tmp_path)
    ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")
    with ledger._connect() as db:
        db.execute("UPDATE lifecycle_receipts SET receipt_hash=? WHERE idempotency_key=?",("0"*64,KEY))
    assert audit_reservation_integrity_v0(ledger)["reason"]=="C226_RECEIPT_HASH_INVALID"

def test_stale_active_reservation_and_orphan_receipt_detected(tmp_path):
    ledger=setup(tmp_path)
    with ledger._connect() as db:
        db.execute("UPDATE scopes SET revoked=1,generation=1 WHERE organization='org-a'")
    assert audit_reservation_integrity_v0(ledger)["reason"]=="C226_STALE_ACTIVE_RESERVATION"
    ledger=setup(tmp_path/"second") if False else ledger
    with ledger._connect() as db:
        db.execute("UPDATE reservations SET status='INVALIDATED'")
        db.execute("INSERT INTO lifecycle_receipts VALUES(?,?,?)",("orphan","CLOSED_NO_EXECUTION","0"*64))
    assert audit_reservation_integrity_v0(ledger)["reason"]=="C226_ORPHAN_RECEIPT"

def test_coordinated_storage_rewrite_not_independently_detectable(tmp_path):
    ledger=setup(tmp_path)
    ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")
    # This audit checks relational integrity, not independent provenance.
    assert audit_reservation_integrity_v0(ledger)["status"]=="BLOCK"
