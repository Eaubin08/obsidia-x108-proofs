from periphery.agent_contracts import NonSovereignAgentSpec, AgentLayer

def test_agent_spec_safe():
    NonSovereignAgentSpec("A", AgentLayer.DATA, "test").assert_safe()

def test_agent_spec_rejects_act():
    spec = NonSovereignAgentSpec("A", AgentLayer.DATA, "test", can_emit_act=True)
    try:
        spec.assert_safe()
    except AssertionError:
        return
    raise AssertionError("expected failure")
