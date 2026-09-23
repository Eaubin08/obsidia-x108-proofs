from dataclasses import dataclass

from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import OS3ProofTicket
from periphery.gencoin import compute_gencoin


def _ticket(gate="ALLOW"):
    return OS3ProofTicket(
        ticket_id="t",
        action_id="a",
        domain="bank",
        x108_gate=gate,
        reason_code="test",
        severity="S0",
        scores={},
        unknowns=[],
        risk_flags=[],
        contradictions=[],
        evidence_refs=[],
        input_hash="i",
        output_hash="o",
        trace_hash="tr",
        merkle_root="m",
        replay_status="NOT_RUN",
    )


def test_gencoin_zero_on_hold():
    a = ActionCandidate("a","bank","actor","intent","act",True,"", payload={"gross_value":10,"total_debt":1})
    p = PeripheralSignalPacket("a","bank")
    gc = compute_gencoin(a, p, _ticket("HOLD"))
    assert gc.gencoin_candidate == 0


def test_gencoin_positive_after_allow():
    a = ActionCandidate("a","bank","actor","intent","act",True,"", payload={"gross_value":10,"total_debt":1})
    p = PeripheralSignalPacket("a","bank")
    gc = compute_gencoin(a, p, _ticket("ALLOW"))
    assert gc.gencoin_candidate == 9
