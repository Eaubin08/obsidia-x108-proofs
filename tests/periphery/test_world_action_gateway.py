from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket
from periphery.world_action_gateway import evaluate_world_action_readiness

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


def test_world_action_is_dry_run_only_even_allow():
    action = ActionCandidate("a", "bank", "actor", "intent", "act", True, "", payload={})
    packet = PeripheralSignalPacket("a", "bank")
    envelope = DummyEnvelope("ALLOW", "OK")
    ticket = build_os3_ticket(action, packet, envelope)
    readiness = evaluate_world_action_readiness(action, envelope, ticket)
    assert readiness.ready_for_controlled_execution is True
    assert readiness.world_action_allowed is False
    assert readiness.dry_run_only is True
