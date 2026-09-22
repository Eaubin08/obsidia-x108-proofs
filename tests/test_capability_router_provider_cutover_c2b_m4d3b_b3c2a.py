from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app

import runtime_wiring.source_runtime.capability_path_router as router


def _caps(result):
    return [
        cap
        for path in result.get(
            "ranked_runtime_paths",
            [],
        )
        for cap in path.get(
            "capability_chain",
            [],
        )
    ]


def test_router_source_provider_zero():
    source = Path(
        "runtime_wiring/source_runtime/"
        "capability_path_router.py"
    ).read_text(
        encoding="utf-8-sig"
    ).lower()

    assert "graphiti" not in source
    assert "neo4j" not in source


def test_generic_memory_intent():
    assert (
        router._INTENT_TO_CAPABILITIES[
            "MEMORY_CONTEXT"
        ]
        == [
            "MEMORY_REINTEGRATION_CONTEXT"
        ]
    )

    assert (
        "MEMORY_GRAPHITI"
        not in router._INTENT_KEYWORDS
    )

    assert (
        "GRAPHITI_READONLY"
        not in router._INTENT_KEYWORDS
    )


def test_provider_capability_not_routable():
    assert (
        "GRAPHITI_READONLY_CONTEXT"
        not in router._CAPABILITY_SCORE
    )

    assert (
        "GRAPHITI_READONLY_CONTEXT"
        not in router._CAPABILITY_PATH_TEMPLATES
    )


def test_write_memory_routes_generic_memory():
    result = router.route_capability_path(
        "write this to memory",
        max_paths=5,
    )

    caps = _caps(result)

    assert (
        "MEMORY_REINTEGRATION_CONTEXT"
        in caps
    )

    assert (
        "GRAPHITI_READONLY_CONTEXT"
        not in caps
    )


def test_legacy_provider_words_do_not_route_provider():
    result = router.route_capability_path(
        "graphiti v20 readonly client",
        max_paths=5,
    )

    text = repr(
        result.get(
            "ranked_runtime_paths",
            [],
        )
    ).lower()

    assert "graphiti" not in text
    assert "neo4j" not in text


def test_live_write_path_provider_zero():
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

        response = client.post(
            "/api/brody/chat",
            json={
                "message":
                    "write this to memory",
                "language": "fr",
            },
        )

        assert response.status_code == 200

        data = response.json()

        ranked = data[
            "source_pack_context"
        ].get(
            "ranked_runtime_paths",
            [],
        )

        text = repr(ranked).lower()

        assert "graphiti" not in text
        assert "neo4j" not in text

        caps = [
            cap
            for path in ranked
            for cap in path.get(
                "capability_chain",
                [],
            )
        ]

        assert (
            "MEMORY_REINTEGRATION_CONTEXT"
            in caps
        )

        assert data["memory_write"] is False

        assert (
            data["decision_authority"]
            == "KX108_ONLY"
        )

        w3 = (
            data[
                "cognitive_runtime_receipt"
            ][
                "components"
            ][
                "W3_BRODY"
            ]
        )

        assert "DEGRADED" not in str(w3)

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
