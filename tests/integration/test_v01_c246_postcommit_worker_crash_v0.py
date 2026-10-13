"""C2.46 deterministic worker crash after SQLite commit and before IPC reply."""
from periphery.enterprise_ipc_postcommit_crash_fixture_v0 import CrashInjectedStorageWorkerV0
from periphery.enterprise_ipc_ambiguous_commit_recovery_v0 import reconcile_ambiguous_reservation_fixture_v0
from periphery.enterprise_offline_storage_worker_v0 import OfflineStorageWorkerV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c246-idempotency-key-00001"
NONCE="c246-nonce-00000000001"

def test_postcommit_worker_crash_recovered_without_duplicate(tmp_path):
    path=tmp_path/"ledger.db"
    worker=CrashInjectedStorageWorkerV0(path)
    worker.start()
    try:
        assert worker.request("initialize_fixture")=="C235_LOCAL_FIXTURE_GUARDS_INITIALIZED_NO_EXECUTION_AUTHORITY"
        assert worker.request("enroll",{"scope":SCOPE})=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
        result=worker.request("reserve_then_crash",
            dict(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY))
        assert result=="BLOCK:C246_AMBIGUOUS_IPC_RESPONSE"
        worker.process.join(3)
        assert worker.process.exitcode==87
    finally:
        worker.stop()
    recovered=reconcile_ambiguous_reservation_fixture_v0(path,idempotency_key=KEY)
    assert recovered["reason"]=="C245_RESERVATION_FOUND_NO_EXECUTION"
    assert recovered["automatic_retry"] is False
    restarted=OfflineStorageWorkerV0(path)
    restarted.start()
    try:
        assert restarted.request_fixture("reserve",
            dict(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY))=="BLOCK:C228_REPLAY_OR_DUPLICATE"
    finally:
        restarted.stop()

def test_uninitialized_worker_stays_fail_closed(tmp_path):
    worker=CrashInjectedStorageWorkerV0(tmp_path/"ledger.db")
    worker.start()
    try:
        assert worker.request("reserve_then_crash",
            dict(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY))=="BLOCK:C236_GUARDS_NOT_READY"
    finally:
        worker.stop()
