import os
import json
import tempfile
import pytest
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket
from periphery.gencoin_debt_model import compute_debt
from periphery.gencoin_distribution import compute_distribution
from periphery.gencoin_ledger import append_ledger_entry, read_ledger


def _make_action(gross=100.0):
    return ActionCandidate(
        action_id="ledger_test_001",
        domain="bank",
        actor_id="tester",
        intent="test",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={"gross_value": gross},
    )


def _make_envelope():
    class E:
        x108_gate = "ALLOW"
        reason_code = "CONFIDENCE_HIGH"
        severity = "INFO"
        metrics = {}
        unknowns = []
        risk_flags = []
        contradictions = []
        evidence_refs = []
    return E()


def test_ledger_append_only_no_overwrite(tmp_path):
    path = str(tmp_path / "ledger.jsonl")
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    envelope = _make_envelope()
    ticket = build_os3_ticket(action, packet, envelope)
    debt = compute_debt(action, packet)
    dist = compute_distribution(action.action_id, 50.0)

    append_ledger_entry(ticket, debt, dist, ledger_path=path)
    append_ledger_entry(ticket, debt, dist, ledger_path=path)

    entries = read_ledger(path)
    assert len(entries) == 2
    assert entries[0]["ledger_id"] != entries[1]["ledger_id"]


def test_ledger_entry_fields(tmp_path):
    path = str(tmp_path / "ledger.jsonl")
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    envelope = _make_envelope()
    ticket = build_os3_ticket(action, packet, envelope)
    debt = compute_debt(action, packet)
    dist = compute_distribution(action.action_id, 50.0)

    entry = append_ledger_entry(ticket, debt, dist, ledger_path=path)
    d = entry.to_dict()

    required_fields = [
        "ledger_id", "os3_ticket_id", "action_id", "x108_gate",
        "proof_valid", "gross_value", "total_debt", "net_value",
        "gencoin_candidate", "mint_allowed", "distribution",
        "input_hash", "output_hash", "trace_hash", "timestamp",
    ]
    for field in required_fields:
        assert field in d, f"Missing field: {field}"


def test_ledger_gencoin_zero_on_hold(tmp_path):
    path = str(tmp_path / "ledger.jsonl")
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    envelope = _make_envelope()
    ticket = build_os3_ticket(action, packet, envelope)
    ticket.x108_gate = "HOLD"
    debt = compute_debt(action, packet)
    dist = compute_distribution(action.action_id, 0.0)

    entry = append_ledger_entry(ticket, debt, dist, ledger_path=path)
    assert entry.gencoin_candidate == 0.0
    assert not entry.mint_allowed
