"""
API proof: /api/periphery/governance/agent-x108-context.

Real HTTP path: registered agent -> AgentResult -> canonical ContextPacket
-> validator -> X108 context boundary -> X108 dry-run admission.

Read-only. Dry-run only. No ACT, no memory write, no kernel mutation.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from periphery.agent_registry import run_registered_agent
from periphery.common import ActionCandidate
from periphery.context.agent_result_context_adapter import (
    agent_result_to_context_packet,
)

ROUTE = "/api/periphery/governance/agent-x108-context"
AGENT_ID = "DATA_PURITY_AGENT"

_ACTION = {
    "action_id": "api_flow_001",
    "domain": "bank",
    "actor_id": "api-test",
    "intent": "inspect",
    "action_type": "query",
    "irreversible": False,
    "timestamp_plan": "2026-09-03T00:00:00+00:00",
    "payload": {"amount": 10},
}


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app

    return TestClient(app)


def _post(client, agent_id=AGENT_ID, **action_overrides):
    action = {**_ACTION, **action_overrides}
    return client.post(ROUTE, json={"agent_id": agent_id, "action": action})


def test_route_returns_canonical_agent_to_x108_context_result(client):
    resp = _post(client)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["agent_id"] == AGENT_ID
    assert data["agent_layer"] == "DATA"
    assert data["action_id"] == "api_flow_001"
    assert data["context_id"].startswith("cp-agent-")
    assert data["boundary"] == "AGENT_TO_X108_CONTEXT_DRY_RUN_ONLY"


def test_route_context_id_matches_the_canonical_binder(client):
    """The API context really derives from the real AgentResult of this action."""
    action = ActionCandidate(
        action_id="api_flow_001",
        domain="bank",
        actor_id="api-test",
        intent="inspect",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-09-03T00:00:00+00:00",
        payload={"amount": 10},
    )
    expected = agent_result_to_context_packet(run_registered_agent(AGENT_ID, action))

    data = _post(client).json()

    assert data["context_id"] == expected.context_id
    assert data["context_packet_refs"] == [expected.context_id]


def test_route_preserves_agent_provenance(client):
    data = _post(client).json()

    assert f"agent:{AGENT_ID}" in data["evidence_refs"]
    assert data["context_projection"]["source"] == f"agent:{AGENT_ID}"
    assert data["context_projection"]["action_id"] == "api_flow_001"


def test_route_locks_non_sovereignty_invariants(client):
    data = _post(client).json()

    assert data["readonly"] is True
    assert data["advisory_only"] is True
    assert data["emits_act"] is False
    assert data["emits_decision"] is False
    assert data["runtime_allowed_now"] is False
    assert data["memory_write"] is False
    assert data["kernel_mutation"] is False
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["dry_run"] is True
    assert data["allowed_to_decide"] is False


def test_route_reports_validator_and_boundary_pass(client):
    data = _post(client).json()

    assert data["context_validation"]["valid"] is True
    assert data["context_validation"]["violations"] == []
    assert data["context_boundary"]["passed"] is True
    assert data["context_boundary"]["violations"] == []
    assert data["context_boundary"]["decision_authority"] == "KX108_ONLY"


def test_route_normal_context_is_allow_context_only(client):
    data = _post(client).json()

    assert data["critical_action_requested"] is False
    assert data["x108_decision"] == "ALLOW_CONTEXT_ONLY"
    assert data["x108_gate_status"] == "X108_EVALUATED_DRY_RUN"
    assert data["x108_ticket_id"].startswith("dt-dryrun-")
    assert data["context_admitted"] is True


def test_route_irreversible_action_is_held(client):
    data = _post(client, action_id="api_flow_critical", irreversible=True).json()

    assert data["critical_action_requested"] is True
    assert data["x108_decision"] == "HOLD"
    assert data["context_admitted"] is False
    assert "CRITICAL_ACTION_REQUIRES_HOLD" in data["reason_codes"]


def test_route_never_emits_act(client):
    for irreversible in (False, True):
        data = _post(client, irreversible=irreversible).json()
        assert data["x108_decision"] in {"BLOCK", "HOLD", "ALLOW_CONTEXT_ONLY"}
        assert data["x108_decision"] != "ACT"
        assert data["emits_act"] is False
        assert data["real_action"] is False


def test_route_rejects_agents52_config_as_not_executable(client):
    resp = _post(client, agent_id="SECRET_GUARD")
    assert resp.status_code == 422, resp.text
    assert "AGENTS52_CONFIG_NOT_EXECUTABLE" in resp.json()["detail"]


def test_route_rejects_unknown_agent(client):
    resp = _post(client, agent_id="NONEXISTENT_AGENT_XYZ_999")
    assert resp.status_code == 404, resp.text
    assert "UNKNOWN_OPERATIONAL_AGENT" in resp.json()["detail"]


def test_agent_run_route_contract_is_unchanged(client):
    """The pre-existing agent-run endpoint keeps its own bounded contract."""
    resp = client.post(
        "/api/periphery/governance/agent-run",
        json={"agent_id": AGENT_ID, "action": _ACTION},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["agent_id"] == AGENT_ID
    assert data["action_id"] == "api_flow_001"
    assert data["emits_act"] is False
    assert data["decision_authority"] == "KX108_ONLY"
    assert "x108_decision" not in data
