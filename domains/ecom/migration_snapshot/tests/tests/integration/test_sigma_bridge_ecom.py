from periphery.common import PeripheralSignalPacket
from periphery.sigma_bridge import run_ecom_with_periphery
from sigma.contracts import EcomState


def make_ecom_state(**kwargs):
    state = EcomState(session_id=kwargs.pop("session_id", "f23a45-ecom"))
    for key, value in kwargs.items():
        setattr(state, key, value)
    return state


def test_f23a4_5_sigma_bridge_ecom_hold_packet():
    state = make_ecom_state(
        session_id="f23a45-ecom",
        traffic_quality=0.8,
        basket_intent_score=0.8,
        stock_ok=True,
        margin_rate=0.25,
        customer_trust=0.8,
        conversion_readiness=0.8,
        roas=2.5,
        fulfillment_risk=0.2,
        intent_conflict_score=0.1,
        checkout_friction_score=0.1,
        merchant_policy_score=0.8,
        x108_compliance_rate=0.95,
        order_value=49.0,
    )

    packet = PeripheralSignalPacket(
        action_id="f23a45-ecom-action",
        domain="ecom",
        extra_metrics={"source": "F23A4_5_TEST"},
        unknowns=[],
        risk_flags=[],
        contradictions=[],
        evidence_refs=["test:f23a4_5:ecom"],
        recommended_gate="HOLD",
        can_emit_act=False,
    )

    envelope = run_ecom_with_periphery(state, packet)

    assert envelope.domain == "ecom"
    assert envelope.x108_gate in {"ALLOW", "HOLD", "BLOCK"}
    assert envelope.source == "canonical_framework"
    assert envelope.raw_engine["domain"] == "ecom"
    assert envelope.raw_engine["vote_count"] == 12
    assert "PERIPHERY_RECOMMENDS_HOLD" in envelope.unknowns
    assert "test:f23a4_5:ecom" in envelope.evidence_refs


def test_f23a4_5_sigma_bridge_ecom_blocks_sovereign_packet():
    state = make_ecom_state(session_id="f23a45-ecom-block-check")

    packet = PeripheralSignalPacket(
        action_id="bad-packet",
        domain="ecom",
        recommended_gate="HOLD",
        can_emit_act=True,
    )

    try:
        run_ecom_with_periphery(state, packet)
    except AssertionError as exc:
        assert "PERIPHERY_CANNOT_EMIT_ACT" in str(exc)
    else:
        raise AssertionError("Sovereign packet must be rejected")
