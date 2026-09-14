"""
Readonly validator for the AGENT_SOURCE_PACK_DOCUMENTATION Wave003 index.

Source: periphery/agents/agent_source_pack_documentation.index.json

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
    "agent_source_pack_documentation.index.json",
)

_SUPPORTED_SCHEMA = "1.0"
_EXPECTED_INDEX_ID = "AGENT_SOURCE_PACK_DOCUMENTATION_INDEX_V1"

_REQUIRED_ENTRY_FIELDS = (
    "path",
    "sha256",
    "role",
    "canonicality_status",
    "relation_type",
    "owner_subsystem",
    "status",
)


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
    """Return a deep copy of all index entries."""
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


def get_entries_by_family(family: str) -> list[dict]:
    return [e for e in get_entries() if e.get("directory_family") == family]


def get_entries_by_relation_type(relation: str) -> list[dict]:
    return [e for e in get_entries() if e.get("relation_type") == relation]


def get_blocked_entries() -> list[dict]:
    return [e for e in get_entries() if (e.get("status") or "").startswith("BLOCKED")]


def summary() -> dict:
    entries = get_entries()
    from collections import Counter
    return {
        "total": len(entries),
        "by_role": dict(Counter(e["role"] for e in entries)),
        "by_relation_type": dict(Counter(e["relation_type"] for e in entries)),
        "by_canonicality": dict(Counter(e["canonicality_status"] for e in entries)),
        "blocked": sum(1 for e in entries if (e.get("status") or "").startswith("BLOCKED")),
    }
