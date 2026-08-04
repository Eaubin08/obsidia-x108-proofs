"""
Readonly validator for the BRODY_INTEGRATION_RUNTIME_AND_API_SYSTEM Wave005_B index.

Source: periphery/agents/brody_integration_runtime_api_system.index.json

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
    "brody_integration_runtime_api_system.index.json",
)

_SUPPORTED_SCHEMA = "1.0"
_EXPECTED_INDEX_ID = "BRODY_INTEGRATION_RUNTIME_API_SYSTEM_INDEX_V1"

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
    "INTEGRATION_RUNTIME_READONLY_MODULE",
    "API_PROTOCOL_SOURCE_MODULE",
    "EXECUTABLE_UNIT_TEST",
})

_VALID_RELATION_TYPES = frozenset({
    "INTEGRATION_RUNTIME_LINKED_TO_GOVERNANCE_INDEX",
    "API_PROTOCOL_LINKED_TO_GOVERNANCE_INDEX",
    "EXECUTABLE_TEST_LINKED_TO_SOURCE_COMPONENT",
})

_VALID_EXECUTABILITY = frozenset({
    "EXECUTABLE_PASSES",
    "EXECUTABLE_FAILS",
    "EXECUTABLE_INTERMITTENT",
    "NOT_A_TEST",
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
    """Return a deep copy of all 144 index entries."""
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


def get_entries_by_family(family: str) -> list[dict]:
    return [e for e in get_entries() if e.get("brody_family") == family]


def get_integration_runtime_entries() -> list[dict]:
    return get_entries_by_role("INTEGRATION_RUNTIME_READONLY_MODULE")


def get_api_protocol_entries() -> list[dict]:
    return get_entries_by_role("API_PROTOCOL_SOURCE_MODULE")


def get_test_entries() -> list[dict]:
    return get_entries_by_role("EXECUTABLE_UNIT_TEST")


def get_failing_test_entries() -> list[dict]:
    return [e for e in get_entries() if e.get("executability_status") == "EXECUTABLE_FAILS"]


def get_intermittent_test_entries() -> list[dict]:
    return [e for e in get_entries() if e.get("executability_status") == "EXECUTABLE_INTERMITTENT"]


def get_blocked_source_entries() -> list[dict]:
    return [e for e in get_entries() if e.get("relation_type") == "BLOCKED_SOURCE_WITHOUT_CONSUMER"]


def get_blocker_queue() -> list[dict]:
    raw = _load_index()
    return copy.deepcopy(raw.get("wave005b_blocker_queue", []))


def get_governance_invariants() -> dict:
    """Return the governance_claims block from the index."""
    raw = _load_index()
    return copy.deepcopy(raw.get("governance_claims", {}))


def get_scope_reconciliation() -> dict:
    """Return scope_reconciliation block — population accounting for Wave005_B."""
    raw = _load_index()
    return copy.deepcopy(raw.get("scope_reconciliation", {}))


def get_remaining_population() -> dict:
    """Return remaining_population block — WAVE005_C through WAVE005_F."""
    raw = _load_index()
    return copy.deepcopy(raw.get("remaining_population", {}))


def is_scope_complete() -> bool:
    """Return False — this index covers WAVE005_B only (scope_complete=false)."""
    raw = _load_index()
    return bool(raw.get("scope_complete", False))


def get_covered_slice() -> str:
    """Return the slice identifier for this index."""
    raw = _load_index()
    return raw.get("covered_slice", "")


def summary() -> dict:
    entries = get_entries()
    from collections import Counter
    return {
        "total": len(entries),
        "by_role": dict(Counter(e["role"] for e in entries)),
        "by_relation_type": dict(Counter(e["relation_type"] for e in entries)),
        "by_executability": dict(Counter(e["executability_status"] for e in entries)),
        "by_semantic_verdict": dict(Counter(e["semantic_verdict"] for e in entries)),
        "by_family": dict(Counter(e.get("brody_family", "?") for e in entries)),
        "executable_fails_count": sum(1 for e in entries if e.get("executability_status") == "EXECUTABLE_FAILS"),
        "executable_intermittent_count": sum(1 for e in entries if e.get("executability_status") == "EXECUTABLE_INTERMITTENT"),
        "source_files_count": sum(1 for e in entries if e.get("executability_status") == "NOT_A_TEST"),
        "blocked_source_count": sum(1 for e in entries if e.get("relation_type") == "BLOCKED_SOURCE_WITHOUT_CONSUMER"),
    }
