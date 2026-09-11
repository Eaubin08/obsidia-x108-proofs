from pathlib import Path

from apps.obsidia_api.brody_real_response_pipeline import (
    run_brody_real_response_pipeline,
)


PIPE = Path(
    "apps/obsidia_api/"
    "brody_real_response_pipeline.py"
)


def test_m4d1a_source_provider_zero():
    source = PIPE.read_text(
        encoding="utf-8-sig"
    ).lower()

    forbidden = (
        "graphiti",
        "neo4j",
        "8011",
        "7688",
        "7475",
        "neo4j_password",
        "_context_query",
    )

    for token in forbidden:
        assert token not in source


def test_m4d1a_runtime_sovereignty():
    out = run_brody_real_response_pipeline(
        "Source test",
        language="fr",
        session_id="m4d1a-r3",
    )

    assert (
        out["decision_authority"]
        == "KX108_ONLY"
    )

    assert out["readonly"] is True
    assert out["memory_write"] is False
    assert out["emits_act"] is False
    assert out["emits_verdict"] is False
    assert out["kernel_mutation"] is False
    assert out["x108_mutation"] is False

    assert out["source"] in {
        "REAL_BRODY_RUNTIME",
        "BACKEND_STUB_LAST_RESORT",
    }

    for key in out:
        low = str(key).lower()

        assert "graphiti" not in low
        assert "neo4j" not in low


def test_m4d1a_context_packet_provider_zero():
    out = run_brody_real_response_pipeline(
        "Source test",
        language="fr",
        session_id="m4d1a-r3-context",
    )

    packet = out[
        "context_packet"
    ]

    assert packet[
        "readonly"
    ] is True

    for key in packet:
        low = str(key).lower()

        assert "graphiti" not in low
        assert "neo4j" not in low
