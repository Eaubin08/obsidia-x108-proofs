from periphery.action_lifecycle import ActionLifecycleTrace, ActionPhase

def test_valid_lifecycle():
    t = ActionLifecycleTrace("a")
    t.advance(ActionPhase.ACTION_CANDIDATE_BUILT)
    assert t.current == ActionPhase.ACTION_CANDIDATE_BUILT

def test_invalid_lifecycle_jump_rejected():
    t = ActionLifecycleTrace("a")
    try:
        t.advance(ActionPhase.X108_EVALUATED)
    except ValueError:
        return
    raise AssertionError("expected invalid transition")
