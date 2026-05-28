import asyncio

from periphery.cognitive_trees.tree_signal_packet import build_tree_signal_packet
from apps.obsidia_api.routes.periphery_ops import TreeSignalPayload, periphery_tree_signal


DOMAIN_SIGMA = {
    "domain": "trading",
    "x108_gate": "HOLD",
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "emits_act": False,
    "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
    "domain_sigma_envelope": True,
}


def unwrap_safe_response(response):
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response


def assert_tree_boundary(packet):
    assert packet["decision_authority"] == "KX108_ONLY"
    assert packet["readonly"] is True
    assert packet["advisory_only"] is True
    assert packet["context_signal_only"] is True
    assert packet["can_decide"] is False
    assert packet["can_emit_act"] is False
    assert packet["emits_act"] is False
    assert packet["emits_verdict"] is False
    assert packet["memory_write"] is False
    assert packet["graphiti_write"] is False
    assert packet["neo4j_write"] is False
    assert packet["kernel_mutation"] is False
    assert packet["x108_mutation"] is False


def test_f27_1_tree_signal_packet_detects_pattern_and_stays_readonly():
    activations = [0.0] * 34
    for idx in (2, 3, 4):
        activations[idx] = 0.9

    packet = build_tree_signal_packet(
        "f27-tree-signal",
        activations,
        theta=0.15,
        domain_sigma_envelope=DOMAIN_SIGMA,
    ).to_dict()

    assert packet["version"] == "TREE_SIGNAL_PACKET_V1"
    assert packet["mode"] == "READONLY_TREE_SIGNAL"
    assert packet["tree_signal_packet"] is True
    assert packet["dominant_count"] >= 3
    assert "LANGUAGE_PATTERN_DETECTED" in packet["patterns_detected"]
    assert packet["domain_sigma_attached"] is True
    assert packet["domain_sigma_envelope"]["domain"] == "trading"
    assert_tree_boundary(packet)


def test_f27_1_tree_signal_endpoint_returns_safe_packet():
    activations = [0.0] * 34
    for idx in (7, 8, 29):
        activations[idx] = 0.8

    response = asyncio.run(periphery_tree_signal(TreeSignalPayload(
        signal_id="f27-endpoint",
        activations=activations,
        theta=0.15,
        domain_sigma_envelope=DOMAIN_SIGMA,
    )))

    data = unwrap_safe_response(response)

    assert data["version"] == "TREE_SIGNAL_PACKET_V1"
    assert data["tree_signal_packet"] is True
    assert "RISK_CONFLICT_PATTERN" in data["patterns_detected"]
    assert data["domain_sigma_attached"] is True
    assert data["domain_sigma_envelope"]["decision_authority"] == "KX108_ONLY"
    assert_tree_boundary(data)


def test_f27_1_tree_signal_packet_without_domain_sigma_is_backward_safe():
    packet = build_tree_signal_packet("f27-no-sigma", [0.1] * 34).to_dict()

    assert packet["domain_sigma_attached"] is False
    assert packet["domain_sigma_envelope"] == {}
    assert_tree_boundary(packet)
