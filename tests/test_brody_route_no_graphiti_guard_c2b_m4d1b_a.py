from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app


ROUTE = Path(
    "apps/obsidia_api/routes/brody.py"
)


def test_route_has_no_graphiti_guard_runtime_owner():
    src = ROUTE.read_text(
        encoding="utf-8-sig"
    )

    assert "brody_graphiti_guard" not in src
    assert "evaluate_graphiti_guard" not in src
    assert "_fp_guard_fn" not in src
    assert '"graphiti_guard":' not in src


def _client():
    app.dependency_overrides[
        require_api_key
    ] = lambda: None

    return TestClient(app)


def test_normal_product_route_still_works():
    client = _client()

    r = client.post(
        "/api/brody/chat",
        json={
            "message": "Source test",
            "language": "fr",
        },
    )

    assert r.status_code == 200

    d = r.json()

    assert (
        d["source"]
        == "REAL_BRODY_RUNTIME"
    )

    assert (
        d["decision_authority"]
        == "KX108_ONLY"
    )

    assert d["emits_act"] is False


def test_compact_route_without_graphiti_guard():
    client = _client()

    r = client.post(
        "/api/brody/chat",
        json={
            "message": "metriques CIC",
            "language": "fr",
            "compact": True,
        },
    )

    assert r.status_code == 200

    d = r.json()

    assert (
        d["decision_authority"]
        == "KX108_ONLY"
    )

    assert d["emits_act"] is False


def test_explicit_memory_stays_native():
    client = _client()

    r = client.post(
        "/api/brody/chat",
        json={
            "message": (
                "retrouve contextpacket "
                "dans la memoire precedente"
            ),
            "language": "fr",
        },
    )

    assert r.status_code == 200

    d = r.json()

    memory = d.get(
        "memory_response_chain_snapshot",
        {},
    )

    assert (
        memory.get("source_mode")
        == "OBSIDIA_NATIVE_MEMORY"
    )

    assert (
        memory.get("retrieval_status")
        == "MEMORY_USABLE"
    )
