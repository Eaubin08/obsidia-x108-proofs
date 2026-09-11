from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app


ROUTE = Path(
    "apps/obsidia_api/routes/brody.py"
)

MACH = Path(
    "apps/obsidia_api/"
    "brody_machination_composer.py"
)


def test_machination_direct_provider_context_removed():
    src = MACH.read_text(
        encoding="utf-8-sig"
    )

    for forbidden in (
        "graphiti_status",
        "neo4j_status",
        "graphiti_context",
        "graphiti_refs",
        "/api/periphery/graphiti/context-adapt",
    ):
        assert forbidden not in src


def test_route_no_longer_supplies_provider_status():
    src = ROUTE.read_text(
        encoding="utf-8-sig"
    )

    assert (
        'graphiti_status='
        'r.get("graphiti_status", ""),'
        not in src
    )

    assert (
        'neo4j_status='
        'r.get("neo4j_status", ""),'
        not in src
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


def test_machination_direct_surface_is_provider_neutral():
    data = _post(
        "Source test"
    )

    packet = data[
        "machination_packet"
    ]

    assert (
        packet["source"]
        == "BRODY_NATIVE_MACHINATION_PACKET_V1"
    )

    assert (
        packet["status"]
        == "MACHINATION_PACKET_READY"
    )

    assert (
        packet["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        packet["memory_write"]
        is False
    )

    assert (
        "graphiti"
        not in packet
    )

    os_trad = packet[
        "support_routes"
    ][
        "os_trad"
    ]

    assert (
        "graphiti_context"
        not in os_trad
    )

    ir = packet[
        "support_routes"
    ][
        "ir_candidate"
    ][
        "ir_candidate"
    ]

    assert (
        "graphiti_refs"
        not in ir
    )

    assert (
        "memory_refs"
        in ir
    )


def test_native_memory_stays_effective():
    data = _post(
        (
            "retrouve contextpacket "
            "dans la memoire precedente"
        )
    )

    memory = data.get(
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
