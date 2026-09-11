from pathlib import Path

from apps.obsidia_api import (
    brody_machination_composer
    as composer,
)


MACH = Path(
    "apps/obsidia_api/"
    "brody_machination_composer.py"
)


def test_composer_source_provider_zero():
    src = MACH.read_text(
        encoding="utf-8-sig"
    ).lower()

    assert "graphiti" not in src
    assert "neo4j" not in src


def test_obsidia_write_process_remains_canonical():
    src = MACH.read_text(
        encoding="utf-8-sig"
    )

    for required in (
        "write_request",
        "memory_write_request",
        "canon_promotion_request",
        "NO_MEMORY_WRITE",
        "NO_KERNEL_MUTATION",
        "NO_X108_MUTATION",
        "DECISION_AUTHORITY_KX108_ONLY",
        "has_memory_write_request",
    ):
        assert required in src


def test_memory_write_request_detected():
    flags = composer._safe_flags(
        "\u00e9cris en m\u00e9moire ce r\u00e9sultat"
    )

    assert "write_request" in flags
    assert "memory_write_request" in flags


def test_specialized_write_flag_is_folded_into_obsidia_memory_write(
    monkeypatch,
):
    def fake_risk_flags(_text):
        return [
            "write_request",
            "legacy_backend_write_request",
        ]

    monkeypatch.setattr(
        composer,
        "_risk_flags",
        fake_risk_flags,
    )

    monkeypatch.setattr(
        composer,
        "adjust_risk_flags",
        None,
    )

    flags = composer._safe_flags(
        "store this"
    )

    assert "write_request" in flags
    assert "memory_write_request" in flags

    assert (
        "legacy_backend_write_request"
        not in flags
    )


def test_no_provider_specific_write_constraint():
    flags = composer._safe_flags(
        "write this to memory"
    )

    constraints = (
        composer._safe_constraints(
            flags
        )
    )

    assert "NO_MEMORY_WRITE" in constraints

    assert (
        "ACTION_REQUEST_FORCED_TO_READONLY_PROJECTION"
        in constraints
    )

    serialized = repr(
        constraints
    ).lower()

    assert "graphiti" not in serialized
    assert "neo4j" not in serialized


def test_write_intent_stays_write_intent():
    flags = [
        "write_request",
        "memory_write_request",
    ]

    assert (
        composer._safe_intent(
            "write this to memory",
            flags,
        )
        == "write_request"
    )


def test_support_route_follows_obsidia_boundary():
    packet = composer.build_support_routes(
        user_message=(
            "write this to memory"
        ),
        language="en",
        session_id="m4d3a2",
    )

    ir = (
        packet[
            "ir_candidate"
        ][
            "ir_candidate"
        ]
    )

    projection = (
        packet[
            "os_reverse"
        ][
            "projection"
        ]
    )

    assert (
        "REQUEST_REQUIRES_WRITE_BUT_ROUTE_IS_READONLY"
        in ir[
            "contradictions"
        ]
    )

    assert (
        "NO_MEMORY_WRITE"
        in ir[
            "constraints"
        ]
    )

    assert (
        ir[
            "memory_write"
        ]
        is False
    )

    assert (
        ir[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        "promotion canonique"
        in projection[
            "summary"
        ]
    )
