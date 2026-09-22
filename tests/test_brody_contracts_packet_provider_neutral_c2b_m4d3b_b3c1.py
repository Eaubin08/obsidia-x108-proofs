from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.brody_contracts_packet import (
    build_brody_contracts_packet,
)
from apps.obsidia_api.main import app


def _packet():
    return build_brody_contracts_packet(
        user_message="write this to memory",
        authority_snapshot={},
    )


def _assert_provider_neutral(value):
    text = repr(value).lower()
    assert "graphiti" not in text
    assert "neo4j" not in text


def test_source_provider_zero():
    source = Path(
        "apps/obsidia_api/brody_contracts_packet.py"
    ).read_text(
        encoding="utf-8-sig"
    ).lower()

    assert "graphiti" not in source
    assert "neo4j" not in source


def test_packet_provider_zero():
    packet = _packet()

    _assert_provider_neutral(packet)

    assert packet["readonly"] is True
    assert packet["decision_authority"] == "KX108_ONLY"


def test_native_memory_contract_preserved():
    packet = _packet()
    memory = packet["memory_contract"]

    assert memory["memory_read"] is True
    assert memory["memory_candidate_prepare"] is True
    assert memory["memory_write"] is False
    assert memory["memory_commit"] is False
    assert memory["requires_operator_validation"] is True
    assert memory["decision_authority"] == "KX108_ONLY"


def test_permission_matrix_uses_memory_only():
    permissions = _packet()["permission_matrix"]

    assert "graphiti" not in permissions
    assert "neo4j" not in permissions

    assert permissions["brody"]["can_write_memory"] is False
    assert permissions["memory"]["can_read"] is True
    assert permissions["memory"]["memory_write"] is False
    assert permissions["memory"]["can_commit"] is False


def test_authority_boundary_signal_memory_preserved():
    packet = _packet()

    authority = packet["authority_contract"]
    boundary = packet["boundary_contract"]
    signal = packet["signal_contract"]

    assert authority["memory_authority"] == "CANDIDATE_ONLY"
    assert boundary["memory_write"] is False
    assert "memory_signal" in signal["allowed_signal_families"]

    _assert_provider_neutral(authority)
    _assert_provider_neutral(boundary)
    _assert_provider_neutral(signal)


def test_live_contract_packet_provider_zero_w3_ready():
    sentinel = object()
    old = app.dependency_overrides.get(require_api_key, sentinel)

    app.dependency_overrides[require_api_key] = lambda: None

    try:
        client = TestClient(app)

        response = client.post(
            "/api/brody/chat",
            json={
                "message": "write this to memory",
                "language": "fr",
            },
        )

        assert response.status_code == 200

        data = response.json()

        contracts = data["contracts"]
        nested = data["machination_packet"]["contracts"]

        _assert_provider_neutral(contracts)
        _assert_provider_neutral(nested)

        assert contracts["memory_contract"]["memory_write"] is False
        assert contracts["memory_contract"]["memory_commit"] is False

        assert data["memory_write"] is False
        assert data["decision_authority"] == "KX108_ONLY"

        w3 = (
            data["cognitive_runtime_receipt"]
            ["components"]
            ["W3_BRODY"]
        )

        assert "DEGRADED" not in str(w3)

    finally:
        if old is sentinel:
            app.dependency_overrides.pop(require_api_key, None)
        else:
            app.dependency_overrides[require_api_key] = old
