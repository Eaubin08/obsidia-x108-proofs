from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")

def test_legacy_reserve_and_close_are_journaled(tmp_path):
    x=AtomicOfflineReservationJournalV0(tmp_path/"ledger.db")
    x.enroll_fixture(SCOPE)
    assert x.reserve_fixture(scope=SCOPE,generation=0,nonce="c229-nonce-00000001",idempotency_key="c229-key-000000001")=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert x.close_fixture(idempotency_key="c229-key-000000001",disposition="ABANDONED_NO_EXECUTION")=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert x.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

def test_legacy_duplicate_and_forbidden_close_fail_closed(tmp_path):
    x=AtomicOfflineReservationJournalV0(tmp_path/"ledger.db")
    x.enroll_fixture(SCOPE)
    params=dict(scope=SCOPE,generation=0,nonce="c229-nonce-00000002",idempotency_key="c229-key-000000002")
    x.reserve_fixture(**params)
    assert x.reserve_fixture(**params)=="BLOCK:C228_REPLAY_OR_DUPLICATE"
    assert x.close_fixture(idempotency_key=params["idempotency_key"],disposition="EXECUTED")=="BLOCK:C228_DISPOSITION_INVALID"
    assert x.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"
