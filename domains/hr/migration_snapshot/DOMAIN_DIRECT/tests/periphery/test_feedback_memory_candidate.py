from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket
from periphery.feedback_memory_candidate import build_feedback_memory_candidate

class DummyEnvelope:
    def __init__(self, gate='ALLOW', reason='OK'):
        self.x108_gate = gate
        self.reason_code = reason
        self.severity = 'INFO'
        self.metrics = {}
        self.unknowns = []
        self.risk_flags = []
        self.contradictions = []
        self.evidence_refs = []


def test_feedback_memory_candidate_never_writes():
    action = ActionCandidate("a", "bank", "actor", "intent", "act", True, "", payload={})
    packet = PeripheralSignalPacket("a", "bank")
    ticket = build_os3_ticket(action, packet, DummyEnvelope("ALLOW", "OK"))
    candidate = build_feedback_memory_candidate(action, ticket, {"ok": True})
    assert candidate.memory_write_allowed is False
