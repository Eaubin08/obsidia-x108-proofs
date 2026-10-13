from periphery.enterprise_offline_transition_journal_v0 import OfflineTransitionJournalV0

def test_hash_chain_survives_restart(tmp_path):
    path=tmp_path/"events.db"
    journal=OfflineTransitionJournalV0(path)
    assert journal.append_fixture(idempotency_key="action-1",event_kind="RESERVED_NO_EXECUTION")=="APPENDED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    assert journal.append_fixture(idempotency_key="action-1",event_kind="CLOSED_NO_EXECUTION")=="APPENDED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    restarted=OfflineTransitionJournalV0(path)
    check=restarted.verify_local()
    assert check["event_count"]==2
    assert check["reason"]=="C227_LOCAL_CHAIN_CONSISTENT_NOT_ATTESTED"
    assert check["egress_allowed"] is False

def test_modified_transition_detected(tmp_path):
    journal=OfflineTransitionJournalV0(tmp_path/"events.db")
    journal.append_fixture(idempotency_key="action-1",event_kind="RESERVED_NO_EXECUTION")
    journal.append_fixture(idempotency_key="action-1",event_kind="ABANDONED_NO_EXECUTION")
    with journal._db() as db:
        db.execute("UPDATE transition_events SET event_kind=? WHERE sequence=1",("INVALIDATED",))
    assert journal.verify_local()["reason"]=="C227_HASH_CHAIN_INVALID"

def test_missing_middle_event_detected(tmp_path):
    journal=OfflineTransitionJournalV0(tmp_path/"events.db")
    for i in range(3):
        journal.append_fixture(idempotency_key=f"action-{i}",event_kind="RESERVED_NO_EXECUTION")
    with journal._db() as db:
        db.execute("DELETE FROM transition_events WHERE sequence=2")
    assert journal.verify_local()["reason"]=="C227_HASH_CHAIN_INVALID"

def test_invalid_state_never_appended(tmp_path):
    journal=OfflineTransitionJournalV0(tmp_path/"events.db")
    assert journal.append_fixture(idempotency_key="action-1",event_kind="EXECUTED")=="BLOCK:C227_EVENT_INVALID"
    assert journal.verify_local()["event_count"]==0
