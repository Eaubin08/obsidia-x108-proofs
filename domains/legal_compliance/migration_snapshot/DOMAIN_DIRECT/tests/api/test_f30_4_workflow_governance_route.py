import asyncio

from apps.obsidia_api.routes.periphery_ops import (
    WorkflowGovernancePacketPayload,
    workflow_governance_packet,
)


def unwrap_safe_response(response):
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response


def assert_boundary(data):
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["readonly"] is True
    assert data["advisory_only"] is True
    assert data["context_signal_only"] is True
    assert data["allowed_to_decide"] is False
    assert data["can_decide"] is False
    assert data["can_emit_act"] is False
    assert data["emits_act"] is False
    assert data["emits_verdict"] is False
    assert data["workflow_decision"] is False
    assert data["memory_decision"] is False
    assert data["graphiti_decision"] is False
    assert data["brody_decision"] is False
    assert data["runtime_execute"] is False
    assert data["memory_write"] is False
    assert data["graphiti_write"] is False
    assert data["neo4j_write"] is False
    assert data["kernel_mutation"] is False
    assert data["x108_mutation"] is False


def test_f30_4_workflow_governance_packet_route_builds_readonly_snapshot():
    response = asyncio.run(workflow_governance_packet(WorkflowGovernancePacketPayload(
        sop_text=(
            "1. Receive customer request\\n"
            "2. Check contract and compliance requirements\\n"
            "3. Prepare response draft\\n"
            "4. Human review before sending"
        ),
        title="customer response SOP",
        session_id="f30-route-test",
        request_type="STRUCTURAL_PREPARATION",
    )))

    data = unwrap_safe_response(response)

    assert data["version"] == "WORKFLOW_GOVERNANCE_PACKET_ROUTE_V1"
    assert data["mode"] == "READONLY_WORKFLOW_GOVERNANCE_PACKET_ROUTE"
    assert data["snapshot_attached"] is True
    assert data["packet_attached"] is True
    assert data["x108_readonly_ingress_attached"] is True

    snapshot = data["workflow_governance_snapshot"]
    assert snapshot["snapshot_kind"] == "BRODY_WORKFLOW_GOVERNANCE_SNAPSHOT_READONLY_V5"
    assert snapshot["decision_authority"] == "KX108_ONLY"
    assert snapshot["boundary"]["decision_authority"] == "KX108_ONLY"
    assert snapshot["boundary"]["readonly"] is True
    assert snapshot["boundary"]["emits_act"] is False
    assert snapshot["boundary"]["kernel_mutation"] is False
    assert snapshot["boundary"]["x108_mutation"] is False

    packet = data["workflow_governance_packet"]
    assert "workflow_graph" in packet
    assert "obsidia_ir" in packet
    assert "context_packet" in packet
    assert "x108_readonly_ingress_envelope" in packet

    envelope = data["x108_readonly_ingress_envelope"]
    assert envelope["boundary"]["decision_authority"] == "KX108_ONLY"
    assert envelope["x108_merge"] is False
    assert envelope["x108_runtime_binding"] is False
    assert envelope["kernel_binding"] is False
    assert envelope["direct_runtime_call"] is False

    assert_boundary(data)


def test_f30_4_workflow_governance_route_detects_critical_readonly_context():
    response = asyncio.run(workflow_governance_packet(WorkflowGovernancePacketPayload(
        sop_text=(
            "1. Validate invoice\\n"
            "2. Trigger bank payment\\n"
            "3. Send confirmation email to client"
        ),
        title="payment SOP",
        session_id="f30-critical-test",
    )))

    data = unwrap_safe_response(response)
    packet = data["workflow_governance_packet"]
    envelope = data["x108_readonly_ingress_envelope"]

    assert data["decision_authority"] == "KX108_ONLY"
    assert data["emits_act"] is False
    assert data["runtime_execute"] is False

    graph = packet["workflow_graph"]
    assert graph["graph_kind"] == "workflow_graph_readonly_candidate"
    assert graph["boundary"]["decision_authority"] == "KX108_ONLY"
    assert graph["boundary"]["readonly"] is True

    ir = packet["obsidia_ir"]
    assert ir["authority"] == "KX108_ONLY"
    assert ir["candidate_only"] is True

    assert envelope["candidate_only"] is True
    assert envelope["direct_runtime_call"] is False

    assert_boundary(data)
