import asyncio

from apps.obsidia_api.routes.periphery_ops import SigmaEvaluatePayload, sigma_evaluate


def unwrap_safe_response(response):
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response


def assert_boundary(data):
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["readonly"] is True
    assert data["advisory_only"] is True
    assert data["emits_act"] is False
    assert data["emits_verdict"] is False
    assert data["memory_write"] is False
    assert data["graphiti_write"] is False
    assert data["neo4j_write"] is False
    assert data["kernel_mutation"] is False
    assert data["x108_mutation"] is False
    assert data["runtime_execute"] is False


def assert_env_boundary(env):
    assert env["decision_authority"] == "KX108_ONLY"
    assert env["readonly"] is True
    assert env["emits_act"] is False
    assert env["emits_verdict"] is False
    assert env["memory_write"] is False
    assert env["graphiti_write"] is False
    assert env["kernel_mutation"] is False
    assert env["x108_mutation"] is False
    assert "x108_gate" in env


def test_f23a6_2_sigma_evaluate_endpoint_trading():
    response = asyncio.run(sigma_evaluate(SigmaEvaluatePayload(
        domain="trading",
        payload={
            "symbol": "BTC/USDT",
            "prices": [100.0 + i for i in range(30)],
            "highs": [101.0 + i for i in range(30)],
            "lows": [99.0 + i for i in range(30)],
            "volumes": [1000.0 for _ in range(30)],
        },
    )))

    data = unwrap_safe_response(response)
    assert_boundary(data)
    assert data["domain_sigma_attached"] is True

    env = data["domain_sigma_envelope"]
    assert env["domain"] == "trading"
    assert_env_boundary(env)


def test_f23a6_2_sigma_evaluate_endpoint_bank():
    response = asyncio.run(sigma_evaluate(SigmaEvaluatePayload(
        domain="bank",
        payload={
            "amount": 42.0,
            "account_balance": 1000.0,
            "available_cash": 900.0,
        },
    )))

    data = unwrap_safe_response(response)
    assert_boundary(data)

    env = data["domain_sigma_envelope"]
    assert env["domain"] == "bank"
    assert_env_boundary(env)


def test_f23a6_2_sigma_evaluate_endpoint_unknown_domain_hold():
    response = asyncio.run(sigma_evaluate(SigmaEvaluatePayload(
        domain="unknown_domain",
        payload={},
    )))

    data = unwrap_safe_response(response)
    assert_boundary(data)

    env = data["domain_sigma_envelope"]
    assert env["domain"] == "unknown_domain"
    assert env["status"] == "UNSUPPORTED_DOMAIN"
    assert env["x108_gate"] == "HOLD"
    assert_env_boundary(env)
