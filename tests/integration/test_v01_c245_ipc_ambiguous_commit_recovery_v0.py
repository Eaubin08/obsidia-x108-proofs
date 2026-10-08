"""C2.45 ambiguous response after commit: recovery must not resend."""
from periphery.enterprise_offline_storage_worker_v0 import OfflineStorageWorkerV0
from periphery.enterprise_ipc_ambiguous_commit_recovery_v0 import reconcile_ambiguous_reservation_fixture_v0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c245-idempotency-key-00001"
NONCE="c245-nonce-00000000001"

def test_committed_reservation_with_lost_ipc_reply(tmp_path):
    path=tmp_path/"ledger.db"
    worker=OfflineStorageWorkerV0(path)
    worker.start()
    try:
        assert worker.request_fixture("initialize_fixture")=="C235_LOCAL_FIXTURE_GUARDS_INITIALIZED_NO_EXECUTION_AUTHORITY"
        assert worker.request_fixture("enroll",{"scope":SCOPE})=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
        assert worker.request_fixture("reserve",dict(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY))=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    finally:
        worker.stop()
    # Simulates loss of the reply after the DB commit: client reconciles by key.
    r=reconcile_ambiguous_reservation_fixture_v0(path,idempotency_key=KEY)
    assert r["reason"]=="C245_RESERVATION_FOUND_NO_EXECUTION"
    assert r["automatic_retry"] is False
    restarted=OfflineStorageWorkerV0(path)
    restarted.start()
    try:
        assert restarted.request_fixture("reserve",dict(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY))=="BLOCK:C228_REPLAY_OR_DUPLICATE"
    finally:
        restarted.stop()

def test_unknown_key_does_not_retry(tmp_path):
    path=tmp_path/"ledger.db"
    worker=OfflineStorageWorkerV0(path)
    worker.start()
    try:
        worker.request_fixture("initialize_fixture")
    finally:
        worker.stop()
    r=reconcile_ambiguous_reservation_fixture_v0(path,idempotency_key="c245-missing-key-00001")
    assert r["reason"]=="C245_RESERVATION_NOT_FOUND_NO_AUTO_RETRY"
    assert not r["automatic_retry"] and not r["egress_allowed"]

def test_uninitialized_storage_blocks_reconciliation(tmp_path):
    r=reconcile_ambiguous_reservation_fixture_v0(tmp_path/"new.db",idempotency_key=KEY)
    assert r["reason"]=="C245_STORAGE_GUARD_OR_STATE_UNAVAILABLE"
    assert r["status"]=="BLOCK"
