from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app


ALIASES = (
    "graphiti_memory_readonly_activation_status",
    "real_graphiti_component_found",
    "graphiti_read_enabled",
    "graphiti_write_enabled",
    "graphiti_memory_context_refs",
    "graphiti_memory_context_status",
    "graphiti_nodes",
    "graphiti_rels",
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


def _assert_surface(data):
    for key in ALIASES:
        assert key not in data

    assert data["readonly"] is True
    assert data["memory_write"] is False

    assert (
        data["memory_write_enabled"]
        is False
    )

    assert (
        data["brody_can_write_memory"]
        is False
    )

    assert (
        data["memory_read_enabled"]
        is True
    )

    assert (
        data["real_memory_component_found"]
        is True
    )

    assert (
        data["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        data["source"]
        == "REAL_BRODY_RUNTIME"
    )

    assert (
        "graphiti_write"
        not in data
    )

    assert (
        "neo4j_write"
        not in data
    )

    assert (
        "brody_can_write_graphiti"
        not in data
    )

    assert (
        data.get("brody_can_write_memory")
        is False
    )


def test_normal():
    data = _post(
        "Explain current Brody status"
    )

    _assert_surface(data)


def test_recall_native_memory():
    data = _post(
        "retrouve contextpacket dans la memoire precedente"
    )

    _assert_surface(data)

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


def test_write_boundary():
    data = _post(
        "write this to memory"
    )

    _assert_surface(data)

    assert (
        data["memory_write"]
        is False
    )

    assert (
        data["memory_write_enabled"]
        is False
    )
