from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app
from apps.obsidia_api.brody_capabilities_intent import (
    build_brody_capabilities_response,
    is_brody_capabilities_query,
)


PROVIDER_KEYS = {
    "graphiti_status",
    "neo4j_status",
    "graphiti_write",
    "neo4j_write",
}


def _assert_provider_neutral(data):
    assert PROVIDER_KEYS.isdisjoint(
        data.keys()
    )

    assert data["memory_write"] is False
    assert data["readonly"] is True
    assert data["emits_act"] is False

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


def _live(message):
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


def test_capabilities_detector():
    assert (
        is_brody_capabilities_query(
            "quelles sont tes capacites ?"
        )
        is True
    )


def test_direct_capabilities_provider_neutral():
    data = build_brody_capabilities_response(
        "quelles sont tes capacites ?"
    )

    assert (
        data["source"]
        == "BRODY_CAPABILITIES_INTENT"
    )

    _assert_provider_neutral(data)


def test_live_capabilities_provider_neutral():
    data = _live(
        "quelles sont tes capacites ?"
    )

    assert (
        data["source"]
        == "BRODY_CAPABILITIES_INTENT"
    )

    _assert_provider_neutral(data)


def test_main_runtime_remains_provider_neutral():
    data = _live(
        "Explain current Brody status"
    )

    assert "graphiti_write" not in data
    assert "neo4j_write" not in data

    assert data["memory_write"] is False

    assert (
        data["decision_authority"]
        == "KX108_ONLY"
    )
