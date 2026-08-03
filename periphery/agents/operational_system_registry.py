"""
Readonly registry for the PYTHON_OPERATIONAL_AGENT_SYSTEM — Wave 002.

Loads and validates operational_system_manifest.json, proving that all 167
unresolved source files exist on disk and match their recorded SHA256.

AUTHORITY: NON_SOVEREIGN — KX108_ONLY decision authority.
WAVE: AGENTS_FILE_WIRING_WAVE_002
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

_MANIFEST_REL = "periphery/agents/operational_system_manifest.json"
_SUPPORTED_SCHEMA = "1.0"
_EXPECTED_ENTRY_COUNT = 167

_CACHE: dict | None = None
_CACHE_SHA: str = ""


def _repo_root() -> Path:
    # __file__ = periphery/agents/operational_system_registry.py
    # .parent   = periphery/agents/
    # .parent   = periphery/
    # .parent   = repo root
    return Path(__file__).resolve().parent.parent.parent


def _manifest_path() -> Path:
    return _repo_root() / _MANIFEST_REL


def _manifest_rel_path() -> str:
    return _MANIFEST_REL


def load_operational_manifest() -> dict:
    """Load and validate operational_system_manifest.json.

    Validates: schema_version, entry_count, path uniqueness,
    existence of all files, SHA256 of all files, authority fields.
    Returns a defensive deep copy. Cached after first successful call.
    Raises FileNotFoundError or ValueError on any violation.
    """
    global _CACHE, _CACHE_SHA
    if _CACHE is not None:
        return copy.deepcopy(_CACHE)

    path = _manifest_path()
    if not path.exists():
        raise FileNotFoundError(
            f"WAVE002_OPERATIONAL_MANIFEST_MISSING:{_MANIFEST_REL}"
        )

    raw = path.read_bytes()
    manifest = json.loads(raw)

    schema = manifest.get("schema_version")
    if schema != _SUPPORTED_SCHEMA:
        raise ValueError(
            f"WAVE002_MANIFEST_UNSUPPORTED_SCHEMA:{schema!r}"
            f" expected={_SUPPORTED_SCHEMA!r}"
        )

    if manifest.get("authority") != "NON_SOVEREIGN":
        raise ValueError(
            f"WAVE002_MANIFEST_AUTHORITY_VIOLATION:{manifest.get('authority')!r}"
        )

    if manifest.get("readonly") is not True:
        raise ValueError("WAVE002_MANIFEST_READONLY_VIOLATION")

    entries: list[dict] = manifest.get("entries", [])
    if len(entries) != _EXPECTED_ENTRY_COUNT:
        raise ValueError(
            f"WAVE002_MANIFEST_ENTRY_COUNT:{len(entries)}"
            f" expected={_EXPECTED_ENTRY_COUNT}"
        )

    paths = [e["path"] for e in entries]
    if len(paths) != len(set(paths)):
        raise ValueError("WAVE002_MANIFEST_DUPLICATE_PATH")

    repo = _repo_root()
    missing: list[str] = []
    mismatched: list[str] = []
    for entry in entries:
        rel = entry["path"]
        try:
            abs_path = (repo / rel).resolve()
            abs_path.relative_to(repo.resolve())
        except ValueError:
            raise ValueError(f"WAVE002_MANIFEST_PATH_ESCAPE:{rel}")
        if not abs_path.exists():
            missing.append(rel)
            continue
        actual_sha = hashlib.sha256(abs_path.read_bytes()).hexdigest()
        if actual_sha != entry["sha256"]:
            mismatched.append(rel)

    if missing:
        raise ValueError(f"WAVE002_MANIFEST_MISSING_FILES:{missing}")
    if mismatched:
        raise ValueError(f"WAVE002_MANIFEST_SHA256_MISMATCH:{mismatched}")

    _CACHE_SHA = hashlib.sha256(raw).hexdigest()
    _CACHE = manifest
    return copy.deepcopy(_CACHE)


def get_wave002_provenance() -> dict:
    """Return provenance metadata for PYTHON_OPERATIONAL_AGENT_SYSTEM Wave 002."""
    load_operational_manifest()
    return {
        "system": "PYTHON_OPERATIONAL_AGENT_SYSTEM",
        "wave": "AGENTS_FILE_WIRING_WAVE_002",
        "manifest_path": _MANIFEST_REL,
        "manifest_sha256": _CACHE_SHA,
        "entry_count": _EXPECTED_ENTRY_COUNT,
        "files_validated": _CACHE is not None,
        "authority": "NON_SOVEREIGN",
        "readonly": True,
        "can_decide": False,
        "can_act": False,
        "emits_act": False,
        "memory_write": False,
        "groups": sorted(set(e["group"] for e in (_CACHE or {}).get("entries", []))),
    }
