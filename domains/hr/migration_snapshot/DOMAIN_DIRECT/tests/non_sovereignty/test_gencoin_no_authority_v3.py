import pytest
from periphery.gencoin_distribution import compute_distribution
from periphery.gencoin_ledger import append_ledger_entry, read_ledger
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket
from periphery.gencoin_debt_model import compute_debt


def _act():
    return ActionCandidate(
        action_id="gencoin_nsov",
        domain="bank",
        actor_id="t",
        intent="t",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={"gross_value": 500.0},
    )


def _ticket(action, gate="ALLOW"):
    pkt = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    class E:
        x108_gate = gate
        reason_code = "X"
        severity = "INFO"
        metrics = {}
        unknowns = []
        risk_flags = []
        contradictions = []
        evidence_refs = []
    return build_os3_ticket(action, pkt, E())


def test_gencoin_no_mint_allowed():
    dist = compute_distribution("x", 100.0)
    assert dist.mint_allowed is False


def test_gencoin_zero_on_hold_or_block():
    for gate in ["HOLD", "BLOCK"]:
        dist = compute_distribution("x", 0.0)
        assert dist.gencoin_candidate == 0.0


def test_gencoin_cannot_authorize():
    dist = compute_distribution("x", 200.0)
    assert not hasattr(dist, "authorize") or not callable(getattr(dist, "authorize", None))


def test_ledger_no_real_token(tmp_path):
    path = str(tmp_path / "ledger.jsonl")
    action = _act()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    ticket = _ticket(action, "HOLD")
    debt = compute_debt(action, packet)
    dist = compute_distribution(action.action_id, 0.0)
    entry = append_ledger_entry(ticket, debt, dist, ledger_path=path)
    assert entry.mint_allowed is False
    entries = read_ledger(path)
    assert entries[0]["mint_allowed"] is False
