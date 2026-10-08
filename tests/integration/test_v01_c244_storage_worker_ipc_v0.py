"""C2.44 process boundary fixture: no provider calls, no execution authority."""
from periphery.enterprise_offline_storage_worker_v0 import OfflineStorageWorkerV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c244-idempotency-key-00001"
NONCE="c244-proof-nonce-00001"

def test_worker_offline_flow_restart(tmp_path):
    path=tmp_path/"ledger.db"
    worker=OfflineStorageWorkerV0(path)
    assert worker.request_fixture("inspect",{"idempotency_key":KEY})=="BLOCK:C244_WORKER_UNAVAILABLE"
    worker.start()
    try:
        assert worker.request_fixture("enroll",{"scope":SCOPE})=="BLOCK:C236_GUARDS_NOT_READY"
        assert worker.request_fixture("initialize_fixture")=="C235_LOCAL_FIXTURE_GUARDS_INITIALIZED_NO_EXECUTION_AUTHORITY"
        assert worker.request_fixture("enroll",{"scope":SCOPE})=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
        assert worker.request_fixture("reserve",dict(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY))=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
        assert worker.request_fixture("execute",{})=="BLOCK:C244_OPERATION_DENIED"
    finally:
        worker.stop()
    restarted=OfflineStorageWorkerV0(path)
    restarted.start()
    try:
        assert restarted.request_fixture("close",dict(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION"))=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
        assert restarted.request_fixture("inspect",{"idempotency_key":KEY})=="CLOSED_NO_EXECUTION"
    finally:
        restarted.stop()

def test_worker_unavailable_after_forced_termination(tmp_path):
    worker=OfflineStorageWorkerV0(tmp_path/"ledger.db")
    worker.start()
    worker._process.terminate()
    worker._process.join(3)
    assert worker.request_fixture("inspect",{"idempotency_key":KEY})=="BLOCK:C244_WORKER_UNAVAILABLE"
    worker.stop()

def test_sql_and_extra_fields_denied(tmp_path):
    worker=OfflineStorageWorkerV0(tmp_path/"ledger.db")
    worker.start()
    try:
        worker.request_fixture("initialize_fixture")
        assert worker.request_fixture("raw_sql",{"sql":"DELETE FROM reservations"})=="BLOCK:C244_OPERATION_DENIED"
        assert worker.request_fixture("enroll",{"scope":SCOPE,"sql":"DROP TABLE scopes"})=="BLOCK:C243_FIELDS_DENIED"
    finally:
        worker.stop()
