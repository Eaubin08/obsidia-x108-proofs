import asyncio

from apps.obsidia_api.routes.periphery_ops import (
    f35_investor_demo_runtime_readiness,
    f35_operator_runtime_panel_data,
    f35_operator_runtime_panel_html,
    f35_workbench_runtime_connector,
)


def unwrap(response):
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
    assert data["runtime_execute"] is False
    assert data["memory_write"] is False
    assert data["graphiti_write"] is False
    assert data["neo4j_write"] is False
    assert data["kernel_mutation"] is False
    assert data["x108_mutation"] is False


def test_f35_1_operator_json_panel_ready_readonly():
    data = unwrap(asyncio.run(f35_operator_runtime_panel_data()))

    assert data["surface_id"] == "F35_C01_OPERATOR_LIVE_RUNTIME_PANEL"
    assert data["surface_kind"] == "operator_json_panel"
    assert data["summary"]["entrypoint_id"] == "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY"
    assert data["summary"]["integration_status"] == "READY_READONLY"
    assert data["summary"]["surfaces_ready"] == 7
    assert data["summary"]["surfaces_missing"] == 0
    assert len(data["surface_rows"]) == 7
    assert_boundary(data)


def test_f35_1_operator_html_panel_contains_runtime_boundary():
    response = asyncio.run(f35_operator_runtime_panel_html())

    body = response.body.decode("utf-8")
    assert response.status_code == 200
    assert "Obsidia Operator Runtime Panel" in body
    assert "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY" in body
    assert "DECISION_AUTHORITY=KX108_ONLY" in body
    assert "emits_act=false" in body
    assert "runtime_execute=false" in body


def test_f35_1_investor_demo_packet_ready_readonly():
    data = unwrap(asyncio.run(f35_investor_demo_runtime_readiness()))

    assert data["surface_id"] == "F35_C02_INVESTOR_DEMO_PACKET"
    assert data["surface_kind"] == "investor_demo_readiness_packet"
    assert data["readiness"]["runtime_ready"] is True
    assert data["readiness"]["surfaces_ready"] == 7
    assert data["readiness"]["surfaces_missing"] == 0
    assert "No ACT emission." in data["proof_points"]
    assert data["boundary"]["decision_authority"] == "KX108_ONLY"


def test_f35_1_workbench_connector_ready_readonly():
    data = unwrap(asyncio.run(f35_workbench_runtime_connector()))

    assert data["surface_id"] == "F35_C03_WORKBENCH_CONNECTOR_SURFACE"
    assert data["surface_kind"] == "workbench_runtime_connector"
    assert data["connector_status"] == "READY_READONLY"
    assert len(data["tabs"]) == 4
    assert data["runtime_summary"]["entrypoint_id"] == "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY"
    assert data["runtime_summary"]["integration_status"] == "READY_READONLY"
    assert data["runtime_summary"]["surfaces_ready"] == 7
    assert data["runtime_summary"]["surfaces_missing"] == 0
    assert len(data["surface_rows"]) == 7
    assert_boundary(data)
