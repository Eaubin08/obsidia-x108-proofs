"""
Readonly validator for the BRODY_LEGACY_ARCHIVE_TOOLING_AND_REVIEW Wave005_F index.

Source: periphery/agents/brody_legacy_archive_tooling_review.index.json

ARCHITECTURE: JSON_FIRST_READONLY_DOCUMENTARY_INDEX
AUTHORITY:    NON_SOVEREIGN -- KX108_ONLY decision authority.

No agent is invoked, no model is called, no memory is written.
can_decide=false / can_act=false / emits_act=false / memory_write=false
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

_INDEX_REL_PARTS = (
    "periphery",
    "agents",
    "brody_legacy_archive_tooling_review.index.json",
)

_SUPPORTED_SCHEMA = "1.0"
_EXPECTED_INDEX_ID = "BRODY_LEGACY_ARCHIVE_TOOLING_REVIEW_INDEX_V1"

_REQUIRED_ENTRY_FIELDS = (
    "path",
    "sha256",
    "role",
    "canonicality_status",
    "relation_type",
    "owner_subsystem",
    "status",
    "semantic_verdict",
    "executability_status",
)

_VALID_ROLES = frozenset({
    "BRODY_FREEZE_REPORT",
    "BRODY_FREEZE_FOUNDATION_DOC",
    "BRODY_FREEZE_MANIFEST",
    "BRODY_FREEZE_RECOVERY_ARTIFACT",
    "BRODY_TOOLING_MODULE",
    "BRODY_UI_COMPONENT",
    "BRODY_UI_FALLBACK_MODULE",
    "BRODY_LEGACY_TEST",
    "BRODY_UI_TEST",
})

_VALID_RELATION_TYPES = frozenset({
    "FREEZE_REPORT_LINKED_TO_ARCHIVE_INDEX",
    "FREEZE_FOUNDATION_DOC_LINKED_TO_CANONICAL_SPEC",
    "FREEZE_MANIFEST_LINKED_TO_FOUNDATION_DOC",
    "FREEZE_MANIFEST_LINKED_TO_ARCHIVE_INDEX",
    "FREEZE_RECOVERY_ARTIFACT_LINKED_TO_VALIDATION_RUN",
    "TOOLING_MODULE_LINKED_TO_RUNTIME_API",
    "UI_COMPONENT_LINKED_TO_WORKBENCH_APP",
    "UI_FALLBACK_MODULE_LINKED_TO_RUNTIME_API",
    "LEGACY_TEST_LINKED_TO_BRODY_API",
    "UI_TEST_LINKED_TO_UI_COMPONENT",
})

_VALID_EXECUTABILITY = frozenset({
    "EXECUTABLE_PASSES",
    "EXECUTABLE_FAILS",
    "EXECUTABLE_INTERMITTENT",
    "NOT_A_TEST",
    "NOT_EXECUTABLE",
})

_FORBIDDEN_SOLE_PROOFS = frozenset({
    "FILE_EXISTS",
    "SHA256_VERIFIED",
    "INDEXED",
    "DOCUMENT_ONLY",
    "RUNTIME_REPORT",
    "NOT_EXECUTABLE",
})


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists():
            return p
    raise RuntimeError("Cannot locate repository root from " + str(here))


def _load_index() -> dict:
    root = _repo_root()
    index_path = root.joinpath(*_INDEX_REL_PARTS)
    with open(index_path, encoding="utf-8") as f:
        raw = json.load(f)
    if raw.get("schema_version") != _SUPPORTED_SCHEMA:
        raise ValueError(
            f"Unsupported schema_version: {raw.get('schema_version')!r}"
        )
    if raw.get("index_id") != _EXPECTED_INDEX_ID:
        raise ValueError(
            f"Unexpected index_id: {raw.get('index_id')!r}"
        )
    return raw


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_index() -> dict:
    """Return a deep copy of the index metadata (no entries)."""
    raw = _load_index()
    return copy.deepcopy({k: v for k, v in raw.items() if k != "entries"})


def get_entries() -> list[dict]:
    """Return a deep copy of all 66 index entries."""
    raw = _load_index()
    return copy.deepcopy(raw.get("entries", []))


def validate_all_paths_exist() -> dict[str, bool]:
    """Return mapping path -> exists for every entry."""
    root = _repo_root()
    result: dict[str, bool] = {}
    for entry in get_entries():
        p = root / entry["path"]
        result[entry["path"]] = p.is_file()
    return result


def validate_sha256(entry: dict) -> bool:
    """Verify the SHA256 of a single entry against the index claim."""
    root = _repo_root()
    p = root / entry["path"]
    if not p.is_file():
        return False
    return _sha256_file(p) == entry["sha256"]


def get_entries_by_role(role: str) -> list[dict]:
    return [e for e in get_entries() if e.get("role") == role]


def get_entries_by_executability(status: str) -> list[dict]:
    return [e for e in get_entries() if e.get("executability_status") == status]


def get_entries_by_relation_type(rel_type: str) -> list[dict]:
    return [e for e in get_entries() if e.get("relation_type") == rel_type]


def get_md_artifact_entries() -> list[dict]:
    return [e for e in get_entries() if e["path"].endswith(".md")]


def get_json_artifact_entries() -> list[dict]:
    return [e for e in get_entries() if e["path"].endswith(".json")]


def get_txt_artifact_entries() -> list[dict]:
    return [e for e in get_entries() if e["path"].endswith(".txt")]


def get_py_source_entries() -> list[dict]:
    return [e for e in get_entries() if e["path"].endswith(".py")]


def get_tsx_entries() -> list[dict]:
    return [e for e in get_entries() if e["path"].endswith(".tsx")]


def get_ts_entries() -> list[dict]:
    return [e for e in get_entries() if e["path"].endswith(".ts")]


def get_freeze_report_entries() -> list[dict]:
    return get_entries_by_role("BRODY_FREEZE_REPORT")


def get_freeze_foundation_doc_entries() -> list[dict]:
    return get_entries_by_role("BRODY_FREEZE_FOUNDATION_DOC")


def get_freeze_manifest_entries() -> list[dict]:
    return get_entries_by_role("BRODY_FREEZE_MANIFEST")


def get_freeze_recovery_artifact_entries() -> list[dict]:
    return get_entries_by_role("BRODY_FREEZE_RECOVERY_ARTIFACT")


def get_tooling_module_entries() -> list[dict]:
    return get_entries_by_role("BRODY_TOOLING_MODULE")


def get_ui_component_entries() -> list[dict]:
    return get_entries_by_role("BRODY_UI_COMPONENT")


def get_ui_fallback_module_entries() -> list[dict]:
    return get_entries_by_role("BRODY_UI_FALLBACK_MODULE")


def get_legacy_test_entries() -> list[dict]:
    return get_entries_by_role("BRODY_LEGACY_TEST")


def get_ui_test_entries() -> list[dict]:
    return get_entries_by_role("BRODY_UI_TEST")


def get_blocker_queue() -> list[dict]:
    raw = _load_index()
    return copy.deepcopy(raw.get("wave005f_blocker_queue", []))


def get_governance_invariants() -> dict:
    raw = _load_index()
    return copy.deepcopy(raw.get("governance_claims", {}))


def get_scope_reconciliation() -> dict:
    raw = _load_index()
    return copy.deepcopy(raw.get("scope_reconciliation", {}))


def get_remaining_population() -> dict:
    raw = _load_index()
    return copy.deepcopy(raw.get("remaining_population", {}))


def is_scope_complete() -> bool:
    raw = _load_index()
    return bool(raw.get("scope_complete", False))


def get_covered_slice() -> str:
    raw = _load_index()
    return raw.get("covered_slice", "")


def has_executable_tests() -> bool:
    """Returns True because Wave005_F includes 2 executable test files."""
    entries = get_entries()
    return any(
        e.get("executability_status") == "EXECUTABLE_PASSES"
        for e in entries
    )


def get_relation_evidence_audit() -> dict:
    raw = _load_index()
    return copy.deepcopy(raw.get("relation_evidence_audit", {}))


def get_primary_proved_count() -> int:
    return get_relation_evidence_audit().get("primary_summary", {}).get("files_with_proved_relation", 0)


def get_primary_blocker_count() -> int:
    raw = _load_index()
    return int(raw.get("primary_files_with_explicit_blocker", 0))


def get_primary_unresolved_count() -> int:
    raw = _load_index()
    return int(raw.get("primary_files_unresolved", 0))


def get_union_recalculation() -> dict:
    audit = get_relation_evidence_audit()
    return copy.deepcopy(audit.get("union_recalculation", {}))


def get_group_rules() -> dict:
    audit = get_relation_evidence_audit()
    return copy.deepcopy(audit.get("group_rules", {}))


def get_final_status() -> str:
    raw = _load_index()
    return raw.get("final_status", "")


def summary() -> dict:
    entries = get_entries()
    from collections import Counter
    return {
        "total": len(entries),
        "by_role": dict(Counter(e["role"] for e in entries)),
        "by_relation_type": dict(Counter(e["relation_type"] for e in entries)),
        "by_executability": dict(Counter(e["executability_status"] for e in entries)),
        "by_semantic_verdict": dict(Counter(e["semantic_verdict"] for e in entries)),
        "md_count": sum(1 for e in entries if e["path"].endswith(".md")),
        "json_count": sum(1 for e in entries if e["path"].endswith(".json")),
        "txt_count": sum(1 for e in entries if e["path"].endswith(".txt")),
        "py_count": sum(1 for e in entries if e["path"].endswith(".py")),
        "tsx_count": sum(1 for e in entries if e["path"].endswith(".tsx")),
        "ts_count": sum(1 for e in entries if e["path"].endswith(".ts")),
        "not_executable_count": sum(1 for e in entries if e.get("executability_status") == "NOT_EXECUTABLE"),
        "not_a_test_count": sum(1 for e in entries if e.get("executability_status") == "NOT_A_TEST"),
        "executable_passes_count": sum(1 for e in entries if e.get("executability_status") == "EXECUTABLE_PASSES"),
    }
