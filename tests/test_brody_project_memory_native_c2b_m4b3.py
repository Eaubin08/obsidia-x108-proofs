from __future__ import annotations

from apps.obsidia_api.brody_project_memory_adapter import (
    build_project_memory_snapshot as build_adapter,
)
from apps.obsidia_api.brody_project_memory_runtime import (
    build_project_memory_snapshot as build_runtime,
)


def test_adapter_reads_canonical_native_index():
    snap = build_adapter()

    assert (
        snap["source_type"]
        == "OBSIDIA_NATIVE_MEMORY_PROJECT_SNAPSHOT"
    )

    assert (
        snap["source_mode"]
        == "OBSIDIA_NATIVE_MEMORY"
    )

    assert (
        snap["status"]
        == "BRODY_PROJECT_MEMORY_NATIVE_SOURCE_MAP_PASS"
    )

    assert snap["native_index_found"] is True
    assert snap["native_runtime_bound"] is True
    assert snap["native_memory_ready"] is True

    assert (
        snap["native_index_item_count"]
        == 3267
    )

    assert (
        snap["local_records_count"]
        == 3267
    )

    assert (
        snap["local_index_item_count"]
        == 3267
    )

    assert (
        snap["text_excerpt_records_count"]
        == 2363
    )

    assert (
        snap["contextual_material_status"]
        == "HAS_PROJECT_MEMORY"
    )

    assert snap["usable_material"] is True

    assert snap["readonly"] is True
    assert snap["memory_write"] is False
    assert snap["emits_act"] is False
    assert snap["emits_verdict"] is False
    assert snap["kernel_mutation"] is False

    assert (
        snap["decision_authority"]
        == "KX108_ONLY"
    )


def test_adapter_source_is_native_not_legacy_provider():
    snap = build_adapter()

    source = str(
        snap["source_file_used"]
    ).lower()

    assert (
        "_obsidia_native_memory"
        in source
    )

    assert (
        "_graphiti_readonly_indexes"
        not in source
    )

    surface = repr(snap).lower()

    assert "graphiti" not in surface
    assert "neo4j" not in surface


def test_candidate_ledger_remains_separate_local_source():
    snap = build_adapter()

    assert (
        "candidate_ledger_found"
        in snap
    )

    assert (
        "candidate_ledger_count"
        in snap
    )

    assert isinstance(
        snap["candidate_ledger_found"],
        bool,
    )

    assert isinstance(
        snap["candidate_ledger_count"],
        int,
    )


def test_foundation_a_runtime_uses_same_native_memory():
    snap = build_runtime()

    assert (
        snap["foundation"]
        == "PROJECT_MEMORY"
    )

    assert (
        snap["status"]
        == "FOUNDATION_A_READY"
    )

    assert (
        snap["source_mode"]
        == "OBSIDIA_NATIVE_MEMORY"
    )

    assert (
        snap["available_sources"][
            "obsidia_native_memory"
        ]
        is True
    )

    assert (
        snap["obsidia_native_memory"]
        is True
    )

    assert (
        "graphiti_v20"
        not in snap["available_sources"]
    )

    assert (
        "graphiti_v20"
        not in snap
    )

    assert snap["readonly"] is True
    assert snap["memory_write"] is False

    assert (
        snap["decision_authority"]
        == "KX108_ONLY"
    )
