from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c228-idempotency-0001"
NONCE="c228-proof-nonce-00001"

def make(tmp_path):
    x=AtomicOfflineReservationJournalV0(tmp_path/"state.db")
    x.enroll_fixture(SCOPE)
    assert x.reserve_logged_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    return x

def test_close_and_restart_journal(tmp_path):
    x=make(tmp_path)
    assert x.close_logged_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    y=AtomicOfflineReservationJournalV0(tmp_path/"state.db")
    assert y.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"
    assert y.receipt(KEY)["status"]=="CLOSED_NO_EXECUTION"

def test_revocation_invalidates_and_logs(tmp_path):
    x=make(tmp_path)
    assert x.revoke(SCOPE)
    y=AtomicOfflineReservationJournalV0(tmp_path/"state.db")
    assert y.inspect(KEY)=="INVALIDATED"
    assert y.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

def test_direct_state_mutation_detected(tmp_path):
    x=make(tmp_path)
    with x._connect() as db:
        db.execute("UPDATE reservations SET status='CLOSED_NO_EXECUTION' WHERE idempotency_key=?",(KEY,))
    assert x.verify_logged_fixture()=="BLOCK:C228_STATE_JOURNAL_MISMATCH"

def test_inherited_close_is_journaled(tmp_path):
    x=make(tmp_path)
    x.close_fixture(idempotency_key=KEY,disposition="ABANDONED_NO_EXECUTION")
    assert x.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

def test_duplicate_never_adds_event(tmp_path):
    x=make(tmp_path)
    assert x.reserve_logged_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="BLOCK:C228_REPLAY_OR_DUPLICATE"
    assert x.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"
