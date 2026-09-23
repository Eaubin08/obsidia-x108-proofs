from sigma.evaluate import evaluate_sigma_domain


def assert_boundary(packet):
    assert packet["decision_authority"] == "KX108_ONLY"
    assert packet["readonly"] is True
    assert packet["advisory_only"] is True
    assert packet["emits_act"] is False
    assert packet["emits_verdict"] is False
    assert packet["memory_write"] is False
    assert packet["graphiti_write"] is False
    assert packet["neo4j_write"] is False
    assert packet["kernel_mutation"] is False
    assert packet["x108_mutation"] is False
    assert packet["runtime_execute"] is False
    assert packet["domain_sigma_envelope"] is True


def test_f23a4_4_sigma_evaluate_bank():
    packet = evaluate_sigma_domain("bank", {
        "amount": 42.0,
        "account_balance": 1000.0,
        "available_cash": 900.0,
        "counterparty_known": True,
        "policy_limit": 5000.0,
        "elapsed_s": 108.0,
    })

    assert packet["domain"] == "bank"
    assert "x108_gate" in packet
    assert_boundary(packet)


def test_f23a4_4_sigma_evaluate_trading():
    packet = evaluate_sigma_domain("trading", {
        "symbol": "BTC/USDT",
        "prices": [100.0 + i for i in range(30)],
        "highs": [101.0 + i for i in range(30)],
        "lows": [99.0 + i for i in range(30)],
        "volumes": [1000.0 for _ in range(30)],
        "spreads_bps": [5.0 for _ in range(30)],
        "btc_reference_prices": [100.0 + i for i in range(30)],
        "sentiment_scores": [0.1],
        "event_risk_scores": [0.2],
    })

    assert packet["domain"] == "trading"
    assert "x108_gate" in packet
    assert_boundary(packet)


def test_f23a4_4_sigma_evaluate_ecom():
    packet = evaluate_sigma_domain("ecom", {
        "traffic_quality": 0.8,
        "basket_intent_score": 0.8,
        "stock_ok": True,
        "margin_rate": 0.3,
        "customer_trust": 0.8,
        "conversion_readiness": 0.8,
        "roas": 2.5,
        "fulfillment_risk": 0.2,
        "intent_conflict_score": 0.1,
        "checkout_friction_score": 0.1,
        "merchant_policy_score": 0.8,
        "x108_compliance_rate": 0.95,
        "order_value": 50.0,
    })

    assert packet["domain"] == "ecom"
    assert "x108_gate" in packet
    assert_boundary(packet)


def test_f23a4_4_sigma_evaluate_gps_defense_aviation():
    packet = evaluate_sigma_domain("gps_defense_aviation", {
        "mission_id": "M-F23A44",
        "flight_id": "F-F23A44",
        "altitude": 1200.0,
        "ground_speed": 240.0,
        "gps_status": "ONLINE",
        "satellites_count": 12,
        "signal_noise_ratio": 0.9,
        "gps_available": True,
    })

    assert packet["domain"] == "gps_defense_aviation"
    assert "x108_gate" in packet
    assert_boundary(packet)


def test_f23a4_4_sigma_evaluate_unknown_domain_is_hold_only():
    packet = evaluate_sigma_domain("unknown_domain", {})

    assert packet["status"] == "UNSUPPORTED_DOMAIN"
    # F62B: x108_gate is now the normalized F62 dict; legacy "HOLD" preserved in
    # pipeline_x108_gate_observed (informational only, not authoritative).
    assert isinstance(packet["x108_gate"], dict)
    assert packet.get("pipeline_x108_gate_observed") == "HOLD"
    assert "UNSUPPORTED_SIGMA_DOMAIN" in packet["unknowns"]
    assert_boundary(packet)
