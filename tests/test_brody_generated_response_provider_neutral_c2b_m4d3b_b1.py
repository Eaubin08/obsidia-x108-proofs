from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app


def _provider_free(value):
    low = str(value or "").lower()

    assert "graphiti" not in low
    assert "neo4j" not in low


def test_b1_generated_user_facing_surfaces_provider_neutral():
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

        cases = (
            (
                "NORMAL",
                "Explique moi le statut actuel de Brody.",
            ),
            (
                "RECALL",
                (
                    "retrouve contextpacket "
                    "dans la memoire precedente"
                ),
            ),
            (
                "WRITE",
                "write this to memory",
            ),
        )

        for name, message in cases:
            r = client.post(
                "/api/brody/chat",
                json={
                    "message": message,
                    "language": "fr",
                },
            )

            assert r.status_code == 200

            d = r.json()

            assert (
                d.get("source")
                == "REAL_BRODY_RUNTIME"
            )

            for value in (
                d.get("response"),
                d.get("final_answer"),
                d.get("response_md"),
            ):
                _provider_free(value)

            voice = d.get(
                "true_voice_snapshot",
                {},
            )

            _provider_free(
                voice.get(
                    "final_answer"
                )
            )

            domain = voice.get(
                "domain_raccord_snapshot",
                {},
            )

            _provider_free(
                domain.get(
                    "structural_answer"
                )
            )

            memory = d.get(
                "memory_response_chain_snapshot",
                {},
            )

            assert (
                memory.get("source_mode")
                == "OBSIDIA_NATIVE_MEMORY"
            )

            if name == "RECALL":
                assert (
                    memory.get(
                        "retrieval_status"
                    )
                    == "MEMORY_USABLE"
                )

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
