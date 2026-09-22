from __future__ import annotations

import hashlib
import json
from pathlib import Path


STORE = (
    Path("_obsidia_native_memory")
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1"
)

MANIFEST = (
    STORE
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1_MANIFEST.json"
)

REPORT = (
    STORE
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1_MIGRATION_REPORT.json"
)

INDEX = (
    STORE
    / "obsidia_native_memory_records_v1.jsonl"
)


def _read_json(path: Path) -> dict:
    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def test_native_memory_manifest_is_runtime_bound_readonly():
    manifest = _read_json(MANIFEST)

    assert manifest["runtime_bound"] is True
    assert manifest["record_count"] == 3267
    assert (
        manifest["status"]
        == "MATERIALIZED_READONLY"
    )

    boundary = manifest["boundary"]

    assert boundary["readonly"] is True
    assert boundary["memory_write"] is False
    assert boundary["auto_promotion"] is False
    assert boundary["emits_act"] is False
    assert boundary["emits_verdict"] is False
    assert boundary["kernel_mutation"] is False
    assert boundary["x108_mutation"] is False
    assert (
        boundary["decision_authority"]
        == "KX108_ONLY"
    )


def test_native_index_identity_is_unchanged():
    manifest = _read_json(MANIFEST)

    assert (
        manifest["native_index_sha256"]
        == _sha256(INDEX)
    )

    assert (
        manifest["native_index_sha256"]
        == (
            "DBED6240A86CE71F1C6F144194ACB8C03718A9F82D449B31A221E5369D154540"
        )
    )


def test_m4a1_migration_report_remains_historical():
    report = _read_json(REPORT)

    assert report["migration"] == "C2B_M4A1_R1"
    assert report["status"] == "PASS"
    assert report["runtime_switched"] is False
    assert report["record_parity"] is True
    assert report["source_records"] == 3267
    assert report["native_records"] == 3267
    assert report["legacy_source_modified"] is False
    assert report["legacy_source_deleted"] is False


def test_migration_report_bytes_are_unchanged():
    assert (
        _sha256(REPORT)
        == (
            "63E2731383C073C0C5DE9AF1DD99BEB69F1BADC4B55238480C74DC046225F413"
        )
    )
