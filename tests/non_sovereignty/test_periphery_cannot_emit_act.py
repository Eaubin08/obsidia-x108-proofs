from periphery.agent_registry import AGENT_REGISTRY
from periphery.common import ActionCandidate


def test_periphery_cannot_emit_act():
    action = ActionCandidate(
        action_id="nsov_periphery",
        domain="bank",
        actor_id="tester",
        intent="registry_check",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={},
    )

    for agent_id, run_agent in AGENT_REGISTRY.items():
        result = run_agent(action)

        assert result.packet.can_emit_act is False, agent_id
        result.assert_non_sovereign()
