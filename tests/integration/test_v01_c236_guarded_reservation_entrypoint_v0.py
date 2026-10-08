import sqlite3
import threading
from periphery.enterprise_guarded_offline_reservation_v0 import GuardedOfflineReservationV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c236-idempotency-key-00001"
NONCE="c236-fixture-nonce-000001"

def test_uninitialized_startup_denies_every_operation(tmp_path):
    app=GuardedOfflineReservationV0(tmp_path/"ledger.db")
    assert app.enroll_fixture(SCOPE)=="BLOCK:C236_GUARDS_NOT_READY"
    assert app.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="BLOCK:C236_GUARDS_NOT_READY"
    assert app.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="BLOCK:C236_GUARDS_NOT_READY"
    assert app.revoke_fixture(SCOPE)=="BLOCK:C236_GUARDS_NOT_READY"

def test_initialized_path_is_offline_and_logged(tmp_path):
    path=tmp_path/"ledger.db"
    app=GuardedOfflineReservationV0(path)
    app.initialize_fixture()
    assert app.enroll_fixture(SCOPE)=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
    assert app.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    restarted=GuardedOfflineReservationV0(path)
    assert restarted.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert restarted.inspect_fixture(KEY)=="CLOSED_NO_EXECUTION"

def test_dropped_guard_blocks_future_operations(tmp_path):
    path=tmp_path/"ledger.db"
    app=GuardedOfflineReservationV0(path)
    app.initialize_fixture()
    app.enroll_fixture(SCOPE)
    with sqlite3.connect(path) as db:
        db.execute("DROP TRIGGER c234_reservation_binding_immutable")
    assert app.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="BLOCK:C236_GUARDS_NOT_READY"

def test_repeated_initialization_across_threads(tmp_path):
    path=tmp_path/"ledger.db"
    app=GuardedOfflineReservationV0(path)
    results=[]
    def install():
        try:
            results.append(app.initialize_fixture())
        except Exception as exc:
            results.append(type(exc).__name__)
    threads=[threading.Thread(target=install) for _ in range(4)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert len(results)==4
    assert all(x=="C235_LOCAL_FIXTURE_GUARDS_INITIALIZED_NO_EXECUTION_AUTHORITY" for x in results)
