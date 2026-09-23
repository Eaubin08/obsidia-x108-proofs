import asyncio

from apps.obsidia_api.routes.brody_monitoring import (
    MonitorGovernedRuntimePayload,
    monitor_governed_runtime,
)


def unwrap_safe_response(response):
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response


def assert_monitor_boundary(data):
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["readonly"] is True
    assert data["advisory_only"] is True
    assert data["context_signal_only"] is True
    assert data["can_decide"] is False
    assert data["can_emit_act"] is False
    assert data["emits_act"] is False
    assert data["emits_verdict"] is False
    assert data["memory_write"] is False
    assert data["graphiti_write"] is False
    assert data["neo4j_write"] is False
    assert data["runtime_execute"] is False
    assert data["kernel_mutation"] is False
    assert data["x108_mutation"] is False


def test_f26_1_monitor_observes_governed_runtime_chain():
    activations = [0.0] * 34
    for idx in (26, 27, 33):
        activations[idx] = 0.9

    response = asyncio.run(monitor_governed_runtime(MonitorGovernedRuntimePayload(
        runtime_id="f26-monitor-smoke",
        domain="trading",
        sigma_payload={
            "symbol": "BTC/USDT",
            "prices": [100.0 + i for i in range(30)],
            "highs": [101.0 + i for i in range(30)],
            "lows": [99.0 + i for i in range(30)],
            "volumes": [1000.0 for _ in range(30)],
        },
        tree_signal_id="f26-monitor-tree",
        activations=activations,
        theta=0.15,
    )))

    data = unwrap_safe_response(response)

    assert data["version"] == "MONITOR_GOVERNED_RUNTIME_V1"
    assert data["observed_runtime_version"] == "GOVERNED_OPERATOR_RUNTIME_V1"
    assert data["mode"] == "READONLY_MONITOR_GOVERNED_RUNTIME"

    assert data["domain_sigma_attached"] is True
    assert data["tree_signal_attached"] is True
    assert data["operator_view_attached"] is True
    assert data["runtime_context_attached"] is True
    assert data["monitor_observes_governed_runtime"] is True

    assert data["domain_sigma_envelope"]["decision_authority"] == "KX108_ONLY"
    assert data["tree_signal_packet"]["version"] == "TREE_SIGNAL_PACKET_V1"
    assert "GOVERNANCE_SOVEREIGNTY_PATTERN" in data["tree_signal_packet"]["patterns_detected"]

    view = data["operator_view_packet"]["operator_view_packet"]
    assert view["readiness"]["domain_sigma"] == "OK"
    assert view["readiness"]["tree_signal"] == "OK"
    assert view["summary"]["operator_can_decide"] is False

    ctx = data["runtime_context"]
    assert ctx["domain_sigma_ready"] is True
    assert ctx["tree_signal_ready"] is True
    assert ctx["tree_signal_version"] == "TREE_SIGNAL_PACKET_V1"
    assert ctx["decision_authority"] == "KX108_ONLY"

    assert_monitor_boundary(data)
