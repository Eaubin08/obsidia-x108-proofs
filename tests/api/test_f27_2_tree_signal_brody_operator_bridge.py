from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet
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


def assert_operator_boundary(view):
    assert view["decision_authority"] == "KX108_ONLY"
    assert view["readonly"] is True
    assert view["emits_act"] is False
    assert view["emits_verdict"] is False
    assert view["memory_write"] is False
    assert view["graphiti_write"] is False
    assert view["neo4j_write"] is False
    assert view["kernel_mutation"] is False
    assert view["x108_mutation"] is False
    assert view["summary"]["operator_can_decide"] is False
    assert view["summary"]["operator_can_write"] is False


def test_f27_2_tree_signal_plugs_into_brody_operator_view():
    activations = [0.0] * 34
    for idx in (26, 27, 33):
        activations[idx] = 0.9

    tree_signal = build_tree_signal_packet(
        "f27-operator-tree-signal",
        activations,
        theta=0.15,
        domain_sigma_envelope=DOMAIN_SIGMA,
    ).to_dict()

    packet = build_operator_view_packet(
        domain_sigma_envelope=DOMAIN_SIGMA,
        tree_signal_packet=tree_signal,
    )

    view = packet["operator_view_packet"]

    assert view["readiness"]["domain_sigma"] == "OK"
    assert view["readiness"]["tree_signal"] == "OK"
    assert view["domain_sigma_attached"] is True
    assert view["domain_sigma_envelope"]["domain"] == "trading"

    assert view["evidence"]["domain_sigma_domain"] == "trading"
    assert view["evidence"]["domain_sigma_gate"] == "HOLD"
    assert view["evidence"]["tree_formal_computation"] is None

    assert "GOVERNANCE_SOVEREIGNTY_PATTERN" in tree_signal["patterns_detected"]
    assert tree_signal["tree_signal_packet"] is True
    assert tree_signal["domain_sigma_attached"] is True
    assert tree_signal["can_decide"] is False
    assert tree_signal["can_emit_act"] is False
    assert tree_signal["emits_act"] is False

    assert_operator_boundary(view)


def test_f27_2_operator_stays_partial_without_tree_signal():
    packet = build_operator_view_packet(domain_sigma_envelope=DOMAIN_SIGMA)
    view = packet["operator_view_packet"]

    assert view["readiness"]["domain_sigma"] == "OK"
    assert view["readiness"]["tree_signal"] == "NOT_READY"
    assert view["summary"]["operator_can_decide"] is False
    assert_operator_boundary(view)
