"""Durable single-host ledger tests. None grants connector permission."""
from concurrent.futures import ThreadPoolExecutor
from periphery.enterprise_durable_revocation_ledger_v0 import DurableDelegationLedgerV0

SCOPE = ("org-a", "delegate-a", "calendar", "CALENDAR.EVENT.CREATE")


def test_restart_preserves_revocation(tmp_path):
    path = tmp_path / "state.db"
    first = DurableDelegationLedgerV0(path)
    first.register_fixture(SCOPE)
    assert first.revoke(SCOPE)
    second = DurableDelegationLedgerV0(path)
    assert second.check_and_consume_fixture(SCOPE, generation=0, nonce="nonce-00000000001", evidence_verified=True) == "BLOCK:C23_REVOKED"


def test_nonce_replay_survives_restart(tmp_path):
    path = tmp_path / "state.db"
    a = DurableDelegationLedgerV0(path)
    a.register_fixture(SCOPE)
    args = dict(generation=0, nonce="nonce-00000000002", evidence_verified=True)
    assert a.check_and_consume_fixture(SCOPE, **args) == "CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    assert DurableDelegationLedgerV0(path).check_and_consume_fixture(SCOPE, **args) == "BLOCK:C23_NONCE_REPLAY"


def test_concurrent_exact_nonce_has_single_winner(tmp_path):
    path = tmp_path / "state.db"
    ledger = DurableDelegationLedgerV0(path)
    ledger.register_fixture(SCOPE)
    def attempt(_):
        return DurableDelegationLedgerV0(path).check_and_consume_fixture(
            SCOPE, generation=0, nonce="nonce-concurrent-123", evidence_verified=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(attempt, range(12)))
    assert results.count("CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY") == 1
    assert results.count("BLOCK:C23_NONCE_REPLAY") == 11


def test_tenant_scope_is_separate_and_unregistered_is_denied(tmp_path):
    a = DurableDelegationLedgerV0(tmp_path / "state.db")
    a.register_fixture(SCOPE)
    other = ("org-b", *SCOPE[1:])
    assert a.check_and_consume_fixture(other, generation=0, nonce="nonce-00000000003", evidence_verified=True) == "BLOCK:C23_DELEGATION_UNKNOWN"
    a.register_fixture(other)
    a.revoke(SCOPE)
    assert a.check_and_consume_fixture(other, generation=0, nonce="nonce-00000000003", evidence_verified=True) == "CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"


def test_no_verified_claim_no_positive_check(tmp_path):
    a = DurableDelegationLedgerV0(tmp_path / "state.db")
    a.register_fixture(SCOPE)
    assert a.check_and_consume_fixture(SCOPE, generation=0, nonce="nonce-00000000004") == "BLOCK:C23_EVIDENCE_NOT_INDEPENDENTLY_VERIFIED"
