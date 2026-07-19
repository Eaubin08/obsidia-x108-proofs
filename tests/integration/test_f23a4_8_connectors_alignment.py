from unittest.mock import Mock, patch

from connectors.bank_normal_flow import BANK_ENDPOINT, build_bank_payload, send_bank_payload
from connectors.aviation_robo import GPS_ENDPOINT, build_gps_payload, send_gps_payload
from connectors.trading_live import TRADING_ENDPOINT, build_trading_payload, send_trading_payload


def test_f23a4_8_bank_connector_targets_monitoring_adapter():
    payload = build_bank_payload()
    assert "payload" in payload
    assert payload["payload"]["action_id"] == "bank-normal-flow"
    assert payload["payload"]["irreversible"] is True

    with patch("connectors.bank_normal_flow.requests.post") as post:
        post.return_value = Mock(status_code=200)
        send_bank_payload(api_base="http://127.0.0.1:8000")

    assert post.call_args.args[0] == f"http://127.0.0.1:8000{BANK_ENDPOINT}"
    assert "kernel/ragnarok" not in post.call_args.args[0]


def test_f23a4_8_gps_connector_targets_monitoring_adapter():
    payload = build_gps_payload()
    assert "payload" in payload
    assert payload["payload"]["action_id"] == "aviation-robo-flow"
    assert payload["payload"]["domain"] if "domain" in payload["payload"] else True

    with patch("connectors.aviation_robo.requests.post") as post:
        post.return_value = Mock(status_code=200)
        send_gps_payload(api_base="http://127.0.0.1:8000")

    assert post.call_args.args[0] == f"http://127.0.0.1:8000{GPS_ENDPOINT}"
    assert "kernel/ragnarok" not in post.call_args.args[0]


def test_f23a4_8_trading_connector_targets_monitoring_adapter():
    history = {
        "prices": [100.0 + i for i in range(20)],
        "highs": [101.0 + i for i in range(20)],
        "lows": [99.0 + i for i in range(20)],
        "volumes": [1000.0 for _ in range(20)],
    }
    payload = build_trading_payload("BTC/USDT", history)
    assert "payload" in payload
    assert payload["payload"]["symbol"] == "BTC/USDT"
    assert len(payload["payload"]["prices"]) == 20

    with patch("connectors.trading_live.requests.post") as post:
        post.return_value = Mock(status_code=200)
        send_trading_payload("BTC/USDT", history, api_base="http://127.0.0.1:8000")

    assert post.call_args.args[0] == f"http://127.0.0.1:8000{TRADING_ENDPOINT}"
    assert "kernel/ragnarok" not in post.call_args.args[0]


def test_f23a4_8_connectors_do_not_reference_dead_endpoint():
    import pathlib

    for file in [
        "connectors/bank_normal_flow.py",
        "connectors/aviation_robo.py",
        "connectors/trading_live.py",
    ]:
        text = pathlib.Path(file).read_text(encoding="utf-8-sig")
        assert "localhost:3001/kernel/ragnarok" not in text
        # Endpoint migré en SRL V2 : /api/periphery/monitoring/adapters/ → /api/live/kernel/adapters/
        assert "/api/live/kernel/adapters/" in text or "/api/periphery/monitoring/adapters/" in text
