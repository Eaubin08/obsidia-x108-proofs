from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet
from apps.obsidia_api.brody_runtime_context_adapter import build_runtime_context


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


def test_f23a6_1_operator_view_packet_carries_domain_sigma_envelope():
    packet = build_operator_view_packet(domain_sigma_envelope=DOMAIN_SIGMA)
    view = packet["operator_view_packet"]

    assert view["domain_sigma_attached"] is True
    assert view["domain_sigma_envelope"]["domain"] == "trading"
    assert view["domain_sigma_envelope"]["x108_gate"] == "HOLD"
    assert view["readiness"]["domain_sigma"] == "OK"
    assert view["evidence"]["domain_sigma_domain"] == "trading"
    assert view["evidence"]["domain_sigma_gate"] == "HOLD"
    assert view["evidence"]["domain_sigma_authority"] == "KX108_ONLY"
    assert view["evidence"]["domain_sigma_emits_act"] is False

    assert view["decision_authority"] == "KX108_ONLY"
    assert view["readonly"] is True
    assert view["emits_act"] is False
    assert view["emits_verdict"] is False
    assert view["kernel_mutation"] is False
    assert view["x108_mutation"] is False
    assert view["summary"]["operator_can_decide"] is False
    assert view["summary"]["domain_sigma_ready"] is True


def test_f23a6_1_runtime_context_carries_domain_sigma_envelope_snapshot():
    ctx = build_runtime_context(domain_sigma_envelope_snapshot=DOMAIN_SIGMA)

    assert ctx["domain_sigma_envelope_snapshot"]["domain"] == "trading"
    assert ctx["domain_sigma_ready"] is True
    assert ctx["domain_sigma_domain"] == "trading"
    assert ctx["domain_sigma_gate"] == "HOLD"
    assert ctx["domain_sigma_authority"] == "KX108_ONLY"

    assert ctx["decision_authority"] == "KX108_ONLY"
    assert ctx["readonly"] is True
    assert ctx["emits_act"] is False
    assert ctx["emits_verdict"] is False
    assert ctx["kernel_mutation"] is False
    assert ctx["x108_mutation"] is False


def test_f23a6_1_backward_compatibility_without_domain_sigma():
    packet = build_operator_view_packet()
    view = packet["operator_view_packet"]
    assert view["domain_sigma_attached"] is False
    assert view["readiness"]["domain_sigma"] == "NOT_READY"

    ctx = build_runtime_context()
    assert ctx["domain_sigma_envelope_snapshot"] == {}
    assert ctx["domain_sigma_ready"] is False
    assert ctx["domain_sigma_domain"] == "UNKNOWN"
