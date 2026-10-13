import sqlite3
import threading
from periphery.enterprise_guarded_offline_reservation_v0 import GuardedOfflineReservationV0
from periphery.enterprise_unified_sqlite_guards_v0 import UnifiedOfflineSqliteGuardsV0
from periphery.enterprise_transaction_guard_snapshot_v0 import inspect_guarded_snapshot_v0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c241-idempotency-key-00001"
NONCE="c241-nonce-00000000001"

def setup(tmp_path):
    path=tmp_path/"store.db"
    app=GuardedOfflineReservationV0(path)
    app.initialize_fixture()
    return path,app

def test_unified_inspect_and_snapshots_reject_keyword_padded_trigger(tmp_path):
    path,app=setup(tmp_path)
    assert app.enroll_fixture(SCOPE)=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
    with sqlite3.connect(path) as db:
        original=db.execute("SELECT sql FROM sqlite_master WHERE name='c230_receipt_no_delete'").fetchone()[0]
        db.execute("DROP TRIGGER c230_receipt_no_delete")
        db.execute(original.replace("SELECT RAISE(ABORT,", "SELECT 1; SELECT RAISE(ABORT,"))
    assert UnifiedOfflineSqliteGuardsV0(path).inspect()["reason"]=="C235_REQUIRED_GUARD_INVALID:CANONICAL_DEFINITION"
    assert inspect_guarded_snapshot_v0(path,"absent")["reason"]=="C237_REQUIRED_GUARD_MODIFIED"
    assert app.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="BLOCK:C236_GUARDS_NOT_READY"

def test_concurrent_reservation_single_success(tmp_path):
    path,app=setup(tmp_path)
    assert app.enroll_fixture(SCOPE)=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
    outcomes=[]
    lock=threading.Lock()
    def reserve():
        answer=GuardedOfflineReservationV0(path).reserve_fixture(
            scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)
        with lock:
            outcomes.append(answer)
    workers=[threading.Thread(target=reserve) for _ in range(12)]
    for t in workers:t.start()
    for t in workers:t.join()
    assert outcomes.count("RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY")==1
    assert outcomes.count("BLOCK:C228_REPLAY_OR_DUPLICATE")==11
    assert GuardedOfflineReservationV0(path).inspect_fixture(KEY)=="RESERVED_NO_EXECUTION"
