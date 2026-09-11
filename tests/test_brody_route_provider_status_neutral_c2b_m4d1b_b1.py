from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app


ROUTE = Path(
    "apps/obsidia_api/routes/brody.py"
)


def test_route_old_source_label_removed():
    src = ROUTE.read_text(
        encoding="utf-8-sig"
    )

    assert (
        "REAL_BRODY_RUNTIME_NO_GRAPHITI"
        not in src
    )

    assert (
        "REAL_BRODY_RUNTIME"
        in src
    )


def test_route_dead_top_level_status_literals_removed():
    src = ROUTE.read_text(
        encoding="utf-8-sig"
    )

    assert '"graphiti_status":' not in src
    assert '"graphiti_blocker":' not in src
    assert '"neo4j_status":' not in src


def _post(payload):
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
            json=payload,
        )

        assert (
            r.status_code
            == 200
        ), r.text[:2000]

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


def test_normal_product_top_level_status_neutral():
    d = _post(
        {
            "message": "Source test",
            "language": "fr",
        }
    )

    assert (
        d["source"]
        == "REAL_BRODY_RUNTIME"
    )

    for key in (
        "graphiti_status",
        "graphiti_blocker",
        "neo4j_status",
    ):
        assert key not in d

    assert "graphiti_write" not in d
    assert "neo4j_write" not in d
    assert d.get("memory_write") is False


def test_native_memory_stays_effective():
    d = _post(
        {
            "message": (
                "retrouve contextpacket "
                "dans la memoire precedente"
            ),
            "language": "fr",
        }
    )

    memory = d.get(
        "memory_response_chain_snapshot",
        {},
    )

    assert (
        d["source"]
        == "REAL_BRODY_RUNTIME"
    )

    assert (
        memory.get("source_mode")
        == "OBSIDIA_NATIVE_MEMORY"
    )

    assert (
        memory.get("retrieval_status")
        == "MEMORY_USABLE"
    )

    for key in (
        "graphiti_status",
        "graphiti_blocker",
        "neo4j_status",
    ):
        assert key not in d
