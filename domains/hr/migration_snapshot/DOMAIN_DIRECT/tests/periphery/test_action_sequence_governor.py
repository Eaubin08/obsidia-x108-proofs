from periphery.common import ActionCandidate
from periphery.action_sequence_governor import ActionStep, ActionSequence, govern_action_sequence

def test_async_sequence_holds():
    action = ActionCandidate("a", "trading", "actor", "intent", "act", True, "", payload={})
    seq = ActionSequence("a", [ActionStep("s1", "api", async_step=True)])
    p = govern_action_sequence(action, seq)
    assert "ASYNC_RECHECK_REQUIRED" in p.unknowns
    assert p.recommended_gate == "HOLD"
