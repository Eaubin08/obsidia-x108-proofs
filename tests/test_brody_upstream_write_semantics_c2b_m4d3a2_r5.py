import inspect

from apps.obsidia_api import (
    brody_machination_composer
    as composer,
)

from apps.obsidia_api.brody_domain_raccord_adapter import (
    adjust_risk_flags,
)

from apps.obsidia_api.routes.os_trad_ir_reverse import (
    _constraints,
    _intent,
)


def test_adjust_risk_flags_uses_obsidia_write_primitives():
    source = inspect.getsource(
        adjust_risk_flags
    )

    assert (
        "memory_write_request"
        in source
    )

    assert (
        "canon_promotion_request"
        in source
    )

    assert (
        "graphiti_write_request"
        not in source
    )

    assert (
        "neo4j_write_request"
        not in source
    )


def test_constraints_use_memory_boundary():
    constraints = _constraints(
        [
            "write_request",
            "memory_write_request",
        ]
    )

    assert (
        "NO_MEMORY_WRITE"
        in constraints
    )

    assert (
        "ACTION_REQUEST_FORCED_TO_READONLY_PROJECTION"
        in constraints
    )

    serialized = repr(
        constraints
    ).lower()

    assert "graphiti" not in serialized
    assert "neo4j" not in serialized


def test_write_intent_precedes_action_risk():
    flags = [
        "action_request",
        "write_request",
        "memory_write_request",
    ]

    assert (
        _intent(
            "write this to memory",
            flags,
        )
        == "write_request"
    )


def test_canon_intent_is_write_request():
    flags = [
        "write_request",
        "memory_write_request",
        "canon_promotion_request",
    ]

    assert (
        _intent(
            "canonise ce bloc",
            flags,
        )
        == "write_request"
    )


def test_composer_pipeline_is_provider_neutral():
    flags = composer._safe_flags(
        "write this to memory"
    )

    constraints = (
        composer._safe_constraints(
            flags
        )
    )

    intent = composer._safe_intent(
        "write this to memory",
        flags,
    )

    assert "write_request" in flags
    assert "memory_write_request" in flags

    assert (
        intent
        == "write_request"
    )

    assert (
        "NO_MEMORY_WRITE"
        in constraints
    )

    serialized = repr(
        {
            "flags": flags,
            "constraints": constraints,
            "intent": intent,
        }
    ).lower()

    assert "graphiti" not in serialized
    assert "neo4j" not in serialized


def test_french_memory_write_follows_same_process():
    text = "\u00e9cris en m\u00e9moire ce r\u00e9sultat"

    flags = composer._safe_flags(
        text
    )

    assert "write_request" in flags
    assert "memory_write_request" in flags

    assert (
        composer._safe_intent(
            text,
            flags,
        )
        == "write_request"
    )


def test_recall_is_not_a_write_request():
    text = (
        "retrouve contextpacket "
        "dans la memoire precedente"
    )

    flags = composer._safe_flags(
        text
    )

    assert (
        "memory_write_request"
        not in flags
    )
