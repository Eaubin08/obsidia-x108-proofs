from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_RECORDS = 3267

REPO = Path(__file__).resolve().parents[2]

LEGACY_INDEX = (
    REPO
    / "_graphiti_readonly_indexes"
    / "GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854"
    / "graphiti_readonly_records_v2.jsonl"
)

OUT_DIR = (
    REPO
    / "_obsidia_native_memory"
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1"
)

OUT_INDEX = OUT_DIR / "obsidia_native_memory_records_v1.jsonl"

MANIFEST = (
    OUT_DIR
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1_MANIFEST.json"
)

REPORT = (
    OUT_DIR
    / "OBSIDIA_NATIVE_MEMORY_INDEX_V1_MIGRATION_REPORT.json"
)

PROVIDER_TAGS = {
    "graphiti",
    "neo4j",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _parse_inner(outer: dict[str, Any]) -> dict[str, Any]:
    """
    Reproduce the historical readonly index normalization contract.

    The JSON-encoded `text` object is the canonical inner representation
    used by the legacy local loader. `payload` is fallback-only.

    This matters for schema records where:
      text.title  = semantic schema title (e.g. NodeContinuum)
      outer.title = source filename      (e.g. NodeContinuum.schema.json)
    """
    raw = outer.get("text")

    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)

            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    payload = outer.get("payload")

    if isinstance(payload, dict):
        return payload

    return {}


def _safe_tags(
    outer: dict[str, Any],
    inner: dict[str, Any],
) -> list[str]:
    raw = outer.get("tags")

    if not isinstance(raw, list):
        raw = inner.get("tags")

    if not isinstance(raw, list):
        raw = []

    out: list[str] = []
    seen: set[str] = set()

    for value in raw:
        tag = str(value).strip()

        if not tag:
            continue

        key = tag.casefold()

        # Provider identity is not part of native indexing metadata.
        if key in PROVIDER_TAGS:
            continue

        if key in seen:
            continue

        seen.add(key)
        out.append(tag)

    return out


def _native_record(
    *,
    ordinal: int,
    raw_line: str,
    outer: dict[str, Any],
) -> dict[str, Any]:
    inner = _parse_inner(outer)

    title = str(
        inner.get("title")
        or outer.get("title")
        or ""
    ).strip()

    source_original_path = str(
        inner.get("source_original_path")
        or ""
    ).strip()

    normalized_path = str(
        inner.get("normalized_md_path")
        or ""
    ).strip()

    outer_path = str(
        outer.get("path")
        or ""
    ).strip()

    source_ref = (
        source_original_path
        or normalized_path
        or outer_path
        or title
        or f"native-memory-record-{ordinal:06d}"
    )

    text_excerpt = str(
        inner.get("text_excerpt")
        or outer.get("text_excerpt")
        or ""
    )

    source_sha256 = str(
        inner.get("source_original_sha256")
        or outer.get("file_sha256")
        or outer.get("body_sha256")
        or ""
    ).strip()

    text_sha256 = str(
        inner.get("text_sha256")
        or ""
    ).strip()

    if not text_sha256:
        text_sha256 = _sha256_text(text_excerpt)

    legacy_line_sha256 = _sha256_text(
        raw_line.rstrip("\r\n")
    )

    native_seed = "|".join([
        source_ref,
        source_sha256,
        text_sha256,
        title,
        str(ordinal),
    ])

    native_hash = _sha256_text(native_seed)

    taxonomy = inner.get("taxonomy_v164d")

    if not isinstance(taxonomy, dict):
        taxonomy = {}

    content_usable = inner.get("content_usable")

    if not isinstance(content_usable, bool):
        content_usable = bool(text_excerpt.strip())

    return {
        "native_id": (
            f"OBSIDIA_MEM_V1_{ordinal:06d}_"
            f"{native_hash[:12]}"
        ),
        "schema_version": "OBSIDIA_NATIVE_MEMORY_RECORD_V1",

        "title": title,
        "source_ref": source_ref,
        "source_original_path": source_original_path,
        "normalized_source_path": normalized_path,

        "source_sha256": source_sha256,
        "text_sha256": text_sha256,
        "legacy_line_sha256": legacy_line_sha256,

        "original_extension": str(
            inner.get("original_extension") or ""
        ),
        "extraction_status": str(
            inner.get("extraction_status") or ""
        ),
        "extractor": str(
            inner.get("extractor") or ""
        ),
        "content_usable": content_usable,

        "tags": _safe_tags(outer, inner),

        "tree_id": outer.get("tree_id"),
        "category": outer.get("category"),
        "taxonomy": taxonomy,

        # Existing runtime retrieval material.
        "text_excerpt": text_excerpt,

        # Provider-neutral origin.
        "source_type": "OBSIDIA_NATIVE_MIGRATED_PROJECT_MEMORY",

        # Absolute governance invariants.
        "readonly": True,
        "memory_authority": False,
        "memory_decision": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "memory_write": False,
        "auto_promotion": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "emits_act": False,
        "emits_verdict": False,
        "decision_authority": "KX108_ONLY",
    }


def main() -> None:
    if not LEGACY_INDEX.exists():
        raise SystemExit(
            f"LEGACY_INDEX_NOT_FOUND:{LEGACY_INDEX}"
        )

    source_bytes = LEGACY_INDEX.read_bytes()
    source_sha256 = _sha256_bytes(source_bytes)

    lines = source_bytes.decode(
        "utf-8",
        errors="strict",
    ).splitlines()

    lines = [
        line
        for line in lines
        if line.strip()
    ]

    if len(lines) != EXPECTED_RECORDS:
        raise SystemExit(
            "SOURCE_RECORD_COUNT_MISMATCH:"
            f"{len(lines)}!={EXPECTED_RECORDS}"
        )

    records: list[dict[str, Any]] = []

    parse_errors: list[dict[str, Any]] = []

    for ordinal, raw_line in enumerate(lines):
        try:
            outer = json.loads(raw_line)

            if not isinstance(outer, dict):
                raise TypeError(
                    f"record is {type(outer).__name__}"
                )

            records.append(
                _native_record(
                    ordinal=ordinal,
                    raw_line=raw_line,
                    outer=outer,
                )
            )

        except Exception as exc:
            parse_errors.append({
                "ordinal": ordinal,
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
            })

    if parse_errors:
        raise SystemExit(
            "SOURCE_PARSE_ERRORS:"
            + json.dumps(
                parse_errors[:20],
                ensure_ascii=False,
            )
        )

    if len(records) != EXPECTED_RECORDS:
        raise SystemExit(
            "MIGRATED_RECORD_COUNT_MISMATCH:"
            f"{len(records)}!={EXPECTED_RECORDS}"
        )

    ids = [
        record["native_id"]
        for record in records
    ]

    if len(ids) != len(set(ids)):
        raise SystemExit(
            "DUPLICATE_NATIVE_IDS"
        )

    excerpt_count = sum(
        1
        for record in records
        if str(
            record.get("text_excerpt") or ""
        ).strip()
    )

    usable_count = sum(
        1
        for record in records
        if record.get("content_usable") is True
    )

    provider_tags_remaining = []

    for record in records:
        for tag in record.get("tags", []):
            if str(tag).casefold() in PROVIDER_TAGS:
                provider_tags_remaining.append({
                    "native_id": record["native_id"],
                    "tag": tag,
                })

    if provider_tags_remaining:
        raise SystemExit(
            "PROVIDER_TAGS_REMAIN:"
            + json.dumps(
                provider_tags_remaining[:20],
                ensure_ascii=False,
            )
        )

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp_index = OUT_INDEX.with_suffix(
        OUT_INDEX.suffix + ".tmp"
    )

    with tmp_index.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as fh:
        for record in records:
            fh.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            fh.write("\n")

    # Validate serialized artifact before atomic replacement.
    serialized_lines = (
        tmp_index
        .read_text(encoding="utf-8")
        .splitlines()
    )

    if len(serialized_lines) != EXPECTED_RECORDS:
        raise SystemExit(
            "SERIALIZED_COUNT_MISMATCH:"
            f"{len(serialized_lines)}"
        )

    for line in serialized_lines:
        json.loads(line)

    os.replace(
        tmp_index,
        OUT_INDEX,
    )

    native_bytes = OUT_INDEX.read_bytes()
    native_sha256 = _sha256_bytes(native_bytes)

    manifest = {
        "schema_version": (
            "OBSIDIA_NATIVE_MEMORY_INDEX_V1"
        ),
        "status": "MATERIALIZED_READONLY",
        "record_count": len(records),
        "text_excerpt_records_count": excerpt_count,
        "content_usable_records_count": usable_count,
        "source_file_sha256": source_sha256,
        "native_index_sha256": native_sha256,
        "native_index_file": (
            "_obsidia_native_memory/"
            "OBSIDIA_NATIVE_MEMORY_INDEX_V1/"
            "obsidia_native_memory_records_v1.jsonl"
        ),

        # Audit provenance only.
        # Runtime readers must not need this path.
        "legacy_migration_source": str(
            LEGACY_INDEX.relative_to(REPO)
        ),

        "provider_specific_runtime_metadata_removed": [
            "provider identity from source_type",
            "provider-specific exact tags",
            "provider write permissions",
            "provider availability state",
        ],

        "content_preservation": {
            "text_excerpt": "PRESERVED_VERBATIM",
            "source_original_path": "PRESERVED",
            "source_sha256": "PRESERVED_WHEN_AVAILABLE",
            "text_sha256": "PRESERVED_OR_RECOMPUTED",
            "taxonomy": "PRESERVED_WHEN_AVAILABLE",
        },

        "boundary": {
            "readonly": True,
            "memory_write": False,
            "auto_promotion": False,
            "kernel_mutation": False,
            "x108_mutation": False,
            "emits_act": False,
            "emits_verdict": False,
            "decision_authority": "KX108_ONLY",
        },

        "runtime_bound": False,
        "created_at": _now(),
    }

    report = {
        "migration": "C2B_M4A1_R1",
        "status": "PASS",
        "source_records": len(lines),
        "native_records": len(records),
        "record_parity": (
            len(lines)
            == len(records)
            == EXPECTED_RECORDS
        ),
        "unique_native_ids": len(set(ids)),
        "text_excerpt_records_count": excerpt_count,
        "content_usable_records_count": usable_count,
        "provider_exact_tags_remaining": 0,
        "source_sha256": source_sha256,
        "native_sha256": native_sha256,
        "runtime_switched": False,
        "legacy_source_modified": False,
        "legacy_source_deleted": False,
        "decision_authority": "KX108_ONLY",
        "memory_write": False,
        "emits_act": False,
        "created_at": _now(),
    }

    MANIFEST.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    REPORT.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "SOURCE_RECORDS =",
        len(lines),
    )
    print(
        "NATIVE_RECORDS =",
        len(records),
    )
    print(
        "TEXT_EXCERPT_RECORDS =",
        excerpt_count,
    )
    print(
        "CONTENT_USABLE_RECORDS =",
        usable_count,
    )
    print(
        "SOURCE_SHA256 =",
        source_sha256,
    )
    print(
        "NATIVE_SHA256 =",
        native_sha256,
    )
    print(
        "M4A1_MATERIALIZATION = PASS"
    )


if __name__ == "__main__":
    main()
