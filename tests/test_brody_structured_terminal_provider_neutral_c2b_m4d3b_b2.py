from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app

from apps.obsidia_api.brody_real_response_pipeline import (
    run_brody_real_response_pipeline,
)

from apps.obsidia_api.brody_structured_response_engine_adapter import (
    make_structured_response_snapshot,
)

from apps.obsidia_api.brody_true_response_structure_adapter import (
    _import_terminal_dialogue,
    build_true_response_structure_snapshot,
)


def provider_free(value):
    low = str(value or "").lower()

    assert "graphiti" not in low
    assert "neo4j" not in low


def test_structured_generated_diagnostic_provider_neutral():
    result = run_brody_real_response_pipeline(
        message=(
            "Explique moi le statut actuel "
            "de Brody."
        ),
        language="fr",
        session_id="local",
    )

    assert (
        result["source"]
        == "REAL_BRODY_RUNTIME"
    )

    snapshot = (
        make_structured_response_snapshot(
            result
        )
    )

    assert (
        snapshot["status"]
        == "STRUCTURED_RESPONSE_ENGINE_PARTIAL"
    )

    assert (
        snapshot["query_stage"]
        == "PASS"
    )

    assert (
        snapshot["consumer_stage"]
        == "PASS"
    )

    assert (
        snapshot["engine_stage"]
        == "TERMINAL_FALLBACK"
    )

    assert (
        snapshot["text_material_status"]
        == "NO_MATERIAL"
    )

    assert snapshot["readonly"] is True

    assert (
        snapshot["memory_write"]
        is False
    )

    assert (
        snapshot["decision_authority"]
        == "KX108_ONLY"
    )

    provider_free(snapshot)


def test_true_response_structure_provider_neutral():
    snapshot = (
        build_true_response_structure_snapshot(
            workspace_root=Path.cwd(),
        )
    )

    provider_free(snapshot)

    identity = snapshot.get(
        "terminal_identity_excerpt",
        "",
    )

    assert (
        "Obsidia native"
        in identity
    )

    assert snapshot["readonly"] is True

    assert (
        snapshot["memory_write"]
        is False
    )

    assert (
        snapshot["decision_authority"]
        == "KX108_ONLY"
    )


def test_terminal_who_boundary_only_provider_neutral():
    td = _import_terminal_dialogue(
        Path.cwd()
    )

    assert td is not None

    who = td.command_response(":who")
    boundary = td.command_response(
        ":boundary"
    )

    assert isinstance(who, dict)
    assert isinstance(boundary, dict)

    provider_free(who)
    provider_free(boundary)

    assert who["readonly"] is True

    assert (
        who["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        who["kernel_mutation"]
        is False
    )

    assert boundary["readonly"] is True

    assert (
        boundary["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        boundary["kernel_mutation"]
        is False
    )


def test_terminal_legacy_provider_surfaces_deferred():
    path = Path(
        "periphery/brody_memory_readonly/"
        "terminal_structural_dialogue_readonly/"
        "brody_terminal_structural_dialogue_readonly_v1.py"
    )

    src = path.read_text(
        encoding="utf-8-sig"
    )

    assert (
        "query_mod.query_neo4j("
        "memory_query, limit)"
        in src
    )

    assert (
        '("graphiti", "Graphiti")'
        in src
    )


def test_route_generated_b2_surfaces():
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
                (
                    "Explique moi le statut "
                    "actuel de Brody."
                ),
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

        for _, message in cases:
            response = client.post(
                "/api/brody/chat",
                json={
                    "message": message,
                    "language": "fr",
                },
            )

            assert response.status_code == 200

            data = response.json()

            structured = data[
                "structured_response_snapshot"
            ]

            true_structure = data[
                "true_response_structure_snapshot"
            ]

            assert (
                data["source"]
                == "REAL_BRODY_RUNTIME"
            )

            assert (
                structured["status"]
                == "STRUCTURED_RESPONSE_ENGINE_PARTIAL"
            )

            assert (
                structured["engine_stage"]
                == "TERMINAL_FALLBACK"
            )

            assert (
                structured["consumer_stage"]
                == "PASS"
            )

            assert (
                structured[
                    "text_material_status"
                ]
                == "NO_MATERIAL"
            )

            provider_free(
                structured
            )

            provider_free(
                true_structure
            )

            for key in (
                "response",
                "final_answer",
                "response_md",
            ):
                provider_free(
                    data.get(key)
                )

            assert (
                structured[
                    "decision_authority"
                ]
                == "KX108_ONLY"
            )

            assert (
                structured["memory_write"]
                is False
            )

            assert (
                true_structure[
                    "decision_authority"
                ]
                == "KX108_ONLY"
            )

            assert (
                true_structure["memory_write"]
                is False
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
