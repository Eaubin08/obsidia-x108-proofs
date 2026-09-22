from pathlib import Path
import ast

from apps.obsidia_api.brody_existing_reverse_os_bridge import (
    build_existing_ir_candidate,
    build_existing_reverse_os_projection,
)


def _constraint_names(ir):
    return [
        item.get("constraint")
        for item in ir.get(
            "constraints",
            [],
        )
        if isinstance(item, dict)
    ]


def _build_ir(message):
    return build_existing_ir_candidate(
        user_message=message,
        intent="write_request",
        semantic_query_snapshot={},
        authority_snapshot={},
        reverse_flow={},
    )


def _build_projection(message):
    return build_existing_reverse_os_projection(
        user_message=message,
        intent="write_request",
        semantic_query_snapshot={},
        authority_snapshot={},
    )


def test_ir_uses_canonical_memory_write_boundary():
    ir = _build_ir(
        "write this to memory"
    )

    constraints = _constraint_names(ir)

    assert "NO_MEMORY_WRITE" in constraints
    assert "NO_GRAPHITI_WRITE" not in constraints

    assert ir["memory_write"] is False
    assert "graphiti_write" not in ir

    assert ir["readonly"] is True

    assert (
        ir["decision_authority"]
        == "KX108_ONLY"
    )


def test_projection_removes_provider_write_fields():
    out = _build_projection(
        "write this to memory"
    )

    ir = out["ir_candidate"]
    trace = out["translation_trace"]

    assert "graphiti_write" not in ir
    assert "graphiti_write" not in trace
    assert "graphiti_write" not in out

    assert ir["memory_write"] is False
    assert trace["memory_write"] is False
    assert out["memory_write"] is False

    assert (
        out["decision_authority"]
        == "KX108_ONLY"
    )


def test_legacy_provider_word_is_still_recognized_only_as_entity():
    ir = _build_ir(
        "ecris dans Graphiti maintenant"
    )

    entities = ir.get(
        "entities",
        [],
    )

    graphiti = [
        item
        for item in entities
        if (
            isinstance(item, dict)
            and item.get("entity")
            == "GRAPHITI"
        )
    ]

    assert len(graphiti) == 1

    assert (
        graphiti[0]["source_token"]
        == "graphiti"
    )

    assert "graphiti_write" not in ir

    assert "NO_GRAPHITI_WRITE" not in (
        _constraint_names(ir)
    )

    assert "NO_MEMORY_WRITE" in (
        _constraint_names(ir)
    )


def test_reverse_os_source_has_only_deferred_lexical_graphiti():
    path = Path(
        "apps/obsidia_api/"
        "brody_existing_reverse_os_bridge.py"
    )

    source = path.read_text(
        encoding="utf-8-sig"
    )

    ast.parse(source)

    assert "NO_GRAPHITI_WRITE" not in source
    assert "graphiti_write_false" not in source
    assert '"graphiti_write": False' not in source

    assert (
        source.count(
            '("graphiti", "GRAPHITI")'
        )
        == 1
    )

    assert "NO_MEMORY_WRITE" in source
    assert '"memory_write": False' in source
