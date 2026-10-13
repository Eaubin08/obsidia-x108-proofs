"""C2.48 live IPC client correlation under concurrent calls (offline fixture)."""
from concurrent.futures import ThreadPoolExecutor
from periphery.enterprise_offline_storage_worker_v0 import OfflineStorageWorkerV0
SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c248-idempotency-key-00001"
NONCE="c248-nonce-00000000001"

def test_stale_reply_does_not_poison_next_call(tmp_path):
    w=OfflineStorageWorkerV0(tmp_path/"ledger.db")
    w.start()
    try:
        assert w.request_fixture("initialize_fixture")=="C235_LOCAL_FIXTURE_GUARDS_INITIALIZED_NO_EXECUTION_AUTHORITY"
        w._responses.put((-1234,"EXECUTED"))
        assert w.request_fixture("enroll",{"scope":SCOPE})=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
        assert w.request_fixture("reserve",dict(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY))=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    finally:
        w.stop()

def test_simultaneous_calls_same_client_are_correlated(tmp_path):
    w=OfflineStorageWorkerV0(tmp_path/"ledger.db")
    w.start()
    try:
        w.request_fixture("initialize_fixture")
        assert w.request_fixture("enroll",{"scope":SCOPE})=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
        def reserve(i):
            return w.request_fixture("reserve",dict(scope=SCOPE,generation=0,
                nonce=NONCE,idempotency_key=KEY),timeout=10)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(reserve,range(8)))
        assert results.count("RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY")==1
        assert results.count("BLOCK:C228_REPLAY_OR_DUPLICATE")==7
    finally:
        w.stop()

def test_unknown_operation_denied(tmp_path):
    w=OfflineStorageWorkerV0(tmp_path/"ledger.db")
    w.start()
    try:
        assert w.request_fixture("execute",{})=="BLOCK:C244_OPERATION_DENIED"
    finally:
        w.stop()
