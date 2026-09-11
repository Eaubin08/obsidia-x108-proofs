from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STORE = (
    ROOT
    / "_obsidia_native_memory"
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1"
)

INDEX = (
    STORE
    / "obsidia_native_memory_records_v1.jsonl"
)

MANIFEST = (
    STORE
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1_MANIFEST.json"
)

REPORT = (
    STORE
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1_MIGRATION_REPORT.json"
)

EXPECTED = 3267

FORBIDDEN_RUNTIME_KEYS = {
    "graphiti_write",
    "neo4j_write",
    "graphiti_allowed",
    "graphiti_status",
    "neo4j_status",
}

PROVIDER_TAGS = {
    "graphiti",
    "neo4j",
}


def _records():
    return [
        json.loads(line)
        for line in INDEX.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def test_native_index_exists_and_has_full_parity():
    assert INDEX.exists()

    records = _records()

    assert len(records) == EXPECTED
    assert len({
        r["native_id"]
        for r in records
    }) == EXPECTED


def test_native_records_are_readonly_non_sovereign():
    for record in _records():
        assert record["readonly"] is True
        assert record["memory_write"] is False
        assert record["auto_promotion"] is False

        assert (
            record["allowed_to_decide"]
            is False
        )

        assert (
            record["allowed_to_act"]
            is False
        )

        assert (
            record["kernel_mutation"]
            is False
        )

        assert (
            record["x108_mutation"]
            is False
        )

        assert record["emits_act"] is False

        assert (
            record["decision_authority"]
            == "KX108_ONLY"
        )


def test_native_runtime_schema_has_no_provider_keys():
    for record in _records():
        assert (
            FORBIDDEN_RUNTIME_KEYS
            .isdisjoint(record.keys())
        )


def test_native_index_tags_are_provider_neutral():
    for record in _records():
        tags = {
            str(tag).casefold()
            for tag in record.get(
                "tags",
                [],
            )
        }

        assert tags.isdisjoint(
            PROVIDER_TAGS
        )


def test_source_material_is_preserved():
    records = _records()

    assert any(
        str(
            r.get("text_excerpt") or ""
        ).strip()
        for r in records
    )

    assert any(
        str(
            r.get("source_ref") or ""
        ).strip()
        for r in records
    )

    assert any(
        str(
            r.get("source_sha256") or ""
        ).strip()
        for r in records
    )


def test_manifest_matches_native_artifact():
    manifest = json.loads(
        MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    assert (
        manifest["record_count"]
        == EXPECTED
    )

    assert (
        manifest["native_index_sha256"]
        == _sha256(INDEX)
    )

    assert isinstance(
        manifest["runtime_bound"],
        bool,
    )

    assert (
        manifest["boundary"][
            "decision_authority"
        ]
        == "KX108_ONLY"
    )


def test_migration_report_proves_no_runtime_switch():
    report = json.loads(
        REPORT.read_text(
            encoding="utf-8"
        )
    )

    assert report["status"] == "PASS"
    assert report["record_parity"] is True
    assert report["source_records"] == EXPECTED
    assert report["native_records"] == EXPECTED

    assert (
        report["runtime_switched"]
        is False
    )

    assert (
        report["legacy_source_modified"]
        is False
    )

    assert (
        report["legacy_source_deleted"]
        is False
    )
