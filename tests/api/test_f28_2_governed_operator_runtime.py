import asyncio

from apps.obsidia_api.brody_runtime_context_adapter import build_runtime_context
from apps.obsidia_api.routes.periphery_ops import (
    GovernedOperatorRuntimePayload,
    periphery_governed_operator_runtime,
)
from periphery.cognitive_trees.tree_signal_packet import build_tree_signal_packet


DOMAIN_SIGMA = {
    "domain": "trading",
    "x108_gate": "HOLD",
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
    "domain_sigma_envelope": True,
}


def unwrap_safe_response(response):
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response


def assert_boundary(data):
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["readonly"] is True
    assert data["emits_act"] is False
    assert data["emits_verdict"] is False
    assert data["memory_write"] is False
    assert data["graphiti_write"] is False
    assert data["neo4j_write"] is False
    assert data["kernel_mutation"] is False
    assert data["x108_mutation"] is False


def test_f28_2_runtime_context_carries_tree_signal_snapshot():
    activations = [0.0] * 34
    for idx in (26, 27, 33):
        activations[idx] = 0.9

    tree_signal = build_tree_signal_packet(
        "f28-runtime-context-tree",
        activations,
        theta=0.15,
        domain_sigma_envelope=DOMAIN_SIGMA,
    ).to_dict()

    ctx = build_runtime_context(
        domain_sigma_envelope_snapshot=DOMAIN_SIGMA,
        tree_signal_packet_snapshot=tree_signal,
    )

    assert ctx["domain_sigma_ready"] is True
    assert ctx["tree_signal_ready"] is True
    assert ctx["tree_signal_packet_snapshot"]["version"] == "TREE_SIGNAL_PACKET_V1"
    assert ctx["tree_signal_version"] == "TREE_SIGNAL_PACKET_V1"
    assert ctx["tree_signal_dominant_count"] == 3
    assert "GOVERNANCE_SOVEREIGNTY_PATTERN" in ctx["tree_signal_patterns"]
    assert_boundary(ctx)


def test_f28_2_governed_operator_runtime_route_aggregates_sigma_tree_operator_context():
    activations = [0.0] * 34
    for idx in (26, 27, 33):
        activations[idx] = 0.9

    response = asyncio.run(periphery_governed_operator_runtime(GovernedOperatorRuntimePayload(
        runtime_id="f28-governed-runtime",
        domain="trading",
        sigma_payload={
            "symbol": "BTC/USDT",
            "prices": [100.0 + i for i in range(30)],
            "highs": [101.0 + i for i in range(30)],
            "lows": [99.0 + i for i in range(30)],
            "volumes": [1000.0 for _ in range(30)],
        },
        tree_signal_id="f28-route-tree",
        activations=activations,
        theta=0.15,
    )))

    data = unwrap_safe_response(response)

    assert data["version"] == "GOVERNED_OPERATOR_RUNTIME_V1"
    assert data["mode"] == "READONLY_GOVERNED_OPERATOR_RUNTIME"
    assert data["domain_sigma_attached"] is True
    assert data["tree_signal_attached"] is True
    assert data["operator_runtime_attached"] is True

    assert data["domain_sigma_envelope"]["decision_authority"] == "KX108_ONLY"
    assert data["tree_signal_packet"]["version"] == "TREE_SIGNAL_PACKET_V1"
    assert data["tree_signal_packet"]["decision_authority"] == "KX108_ONLY"

    view = data["operator_view_packet"]["operator_view_packet"]
    assert view["readiness"]["domain_sigma"] == "OK"
    assert view["readiness"]["tree_signal"] == "OK"
    assert view["summary"]["operator_can_decide"] is False

    ctx = data["runtime_context"]
    assert ctx["domain_sigma_ready"] is True
    assert ctx["tree_signal_ready"] is True
    assert ctx["tree_signal_version"] == "TREE_SIGNAL_PACKET_V1"

    assert_boundary(data)
    assert_boundary(ctx)
