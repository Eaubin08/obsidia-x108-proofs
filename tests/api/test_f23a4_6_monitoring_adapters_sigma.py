import asyncio

from apps.obsidia_api.routes.brody_monitoring import (
    AdapterPayload,
    monitor_bank,
    monitor_gps,
    monitor_trading,
)


def unwrap_safe_response(response):
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response


def assert_monitoring_boundary(data):
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


def assert_sigma_envelope(data, domain):
    assert data["domain_sigma_attached"] is True
    assert "domain_sigma_envelope" in data

    env = data["domain_sigma_envelope"]
    assert env["domain"] == domain
    assert env["decision_authority"] == "KX108_ONLY"
    assert env["readonly"] is True
    assert env["emits_act"] is False
    assert env["emits_verdict"] is False
    assert env["memory_write"] is False
    assert env["graphiti_write"] is False
    assert env["kernel_mutation"] is False
    assert env["x108_mutation"] is False
    assert "x108_gate" in env


def test_f23a4_6_monitoring_bank_adapter_has_sigma_envelope():
    response = asyncio.run(monitor_bank(AdapterPayload(payload={"amount": 42.0})))
    data = unwrap_safe_response(response)

    assert "action" in data
    assert "state_keys" in data
    assert "periphery_control_packet" in data
    assert_monitoring_boundary(data)
    assert_sigma_envelope(data, "bank")


def test_f23a4_6_monitoring_trading_adapter_has_sigma_envelope():
    response = asyncio.run(monitor_trading(AdapterPayload(payload={"symbol": "BTC/USDT"})))
    data = unwrap_safe_response(response)

    assert "action" in data
    assert "state_keys" in data
    assert "periphery_control_packet" in data
    assert_monitoring_boundary(data)
    assert_sigma_envelope(data, "trading")


def test_f23a4_6_monitoring_gps_adapter_has_sigma_envelope():
    response = asyncio.run(monitor_gps(AdapterPayload(payload={"mission_id": "F23A46"})))
    data = unwrap_safe_response(response)

    assert "action" in data
    assert "state_keys" in data
    assert "periphery_control_packet" in data
    assert_monitoring_boundary(data)
    assert_sigma_envelope(data, "gps_defense_aviation")
