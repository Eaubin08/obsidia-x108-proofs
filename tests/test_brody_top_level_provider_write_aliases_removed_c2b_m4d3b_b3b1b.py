from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app
from apps.obsidia_api.safe_response import safe_backend_response
from apps.obsidia_api.brody_capabilities_intent import (
    is_brody_capabilities_query,
)


def _post(message):
    sentinel = object()

    old = app.dependency_overrides.get(
        require_api_key,
        sentinel,
    )

    app.dependency_overrides[
        require_api_key
    ] = lambda: None

    try:
        client = TestClient(app)

        r = client.post(
            "/api/brody/chat",
            json={
                "message": message,
                "language": "fr",
            },
        )

        assert r.status_code == 200

        return r.json()

    finally:
        if old is sentinel:
            app.dependency_overrides.pop(
                require_api_key,
                None,
            )
        else:
            app.dependency_overrides[
                require_api_key
            ] = old


def _assert_provider_neutral_top_level(data):
    assert "graphiti_write" not in data
    assert "neo4j_write" not in data

    assert data["memory_write"] is False
    assert data["memory_write_enabled"] is False
    assert data["brody_can_write_memory"] is False

    assert data["readonly"] is True
    assert data["allowed_to_act"] is False
    assert data["allowed_to_decide"] is False
    assert data["emits_act"] is False
    assert data["kernel_mutation"] is False

    assert (
        data["decision_authority"]
        == "KX108_ONLY"
    )


def test_safe_backend_response_no_provider_write_aliases():
    out = safe_backend_response(
        {
            "status": "TEST",
            "memory_write": False,
            "decision_authority": "KX108_ONLY",
        },
        source="B3B1B_TEST",
    )

    assert "graphiti_write" not in out
    assert "neo4j_write" not in out
    assert out["memory_write"] is False

    assert (
        out["decision_authority"]
        == "KX108_ONLY"
    )


def test_normal_top_level_provider_neutral():
    data = _post(
        "Explain current Brody status"
    )

    _assert_provider_neutral_top_level(
        data
    )


def test_recall_top_level_provider_neutral():
    data = _post(
        "retrouve contextpacket dans la memoire precedente"
    )

    _assert_provider_neutral_top_level(
        data
    )

    memory = data[
        "memory_response_chain_snapshot"
    ]

    assert (
        memory["source_mode"]
        == "OBSIDIA_NATIVE_MEMORY"
    )

    assert (
        memory["retrieval_status"]
        == "MEMORY_USABLE"
    )


def test_write_top_level_provider_neutral():
    data = _post(
        "write this to memory"
    )

    _assert_provider_neutral_top_level(
        data
    )


def test_capabilities_provider_neutral_after_b3b1c():
    message = next(
        m
        for m in (
            "quelles sont tes capacites ?",
            "capabilities",
        )
        if is_brody_capabilities_query(m)
    )

    data = _post(message)

    assert (
        data["source"]
        == "BRODY_CAPABILITIES_INTENT"
    )

    assert "graphiti_status" not in data
    assert "neo4j_status" not in data
    assert "graphiti_write" not in data
    assert "neo4j_write" not in data

    assert data["memory_write"] is False
    assert data["readonly"] is True

    assert (
        data["decision_authority"]
        == "KX108_ONLY"
    )

    text = (
        str(data.get("response", ""))
        + " "
        + str(data.get("final_answer", ""))
    ).lower()

    assert "graphiti" not in text
    assert "neo4j" not in text
