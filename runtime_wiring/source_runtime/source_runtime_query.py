# runtime_wiring/source_runtime/source_runtime_query.py
# Query the source registry for relevant entries, then hydrate them in read-only mode.
# Returns hydrated ContextPackets ready for X108 routing.
# Never loads all 15298 entries — targeted, limit-enforced queries only.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from runtime_wiring.source_registry.registry_loader import load_registry_json
from runtime_wiring.source_registry.registry_types import SourceFileRegistryEntry
from runtime_wiring.source_registry.registry_to_adapter_dry_run import (
    _FORBIDDEN_DECISIONS,
    _FORBIDDEN_QUARANTINE,
)
from runtime_wiring.source_runtime.source_pack_resolver import is_source_pack_available
from runtime_wiring.source_runtime.source_context_hydrator import (
    HydrationError,
    hydrate_entry,
)
from runtime_wiring.packet_types import ContextPacket

_PREFERRED_EXTENSIONS = frozenset({".md", ".yaml", ".yml"})
_DEFAULT_LIMIT = 5
_MAX_LIMIT = 20


@dataclass
class QueryResult:
    family: str
    registry_id: str
    file_name: str
    internal_path: str
    context_packet: ContextPacket
    content_preview: str
    content_hash: str
    bytes_read: int
    hydration_status: str  # "OK" or "SKIPPED:<reason>"


def _is_routable(entry: SourceFileRegistryEntry) -> bool:
    """True if entry can be hydrated (not forbidden, pack available, safe extension)."""
    if entry.recommended_decision in _FORBIDDEN_DECISIONS:
        return False
    if entry.quarantine_status in _FORBIDDEN_QUARANTINE:
        return False
    if entry.extension.lower() in (".py", ".pyc"):
        return False
    if not is_source_pack_available(entry.source_zip):
        return False
    return True


def query_source_packs(
    families: Optional[List[str]] = None,
    keyword: Optional[str] = None,
    extensions: Optional[List[str]] = None,
    limit: int = _DEFAULT_LIMIT,
    prefer_short_files: bool = True,
) -> List[QueryResult]:
    """
    Query the source registry, hydrate matching entries in read-only mode.

    Args:
        families: Restrict to these source families. None = all.
        keyword: Filter by keyword in file_name or internal_path (case-insensitive).
        extensions: Restrict to these extensions (e.g. [".md", ".yaml"]).
        limit: Max entries to hydrate. Capped at _MAX_LIMIT.
        prefer_short_files: Prefer shorter files (faster preview loading).

    Returns:
        List of QueryResult. Never raises — failed hydrations are marked SKIPPED.
    """
    limit = min(max(1, limit), _MAX_LIMIT)
    exts = frozenset(e.lower() for e in extensions) if extensions else _PREFERRED_EXTENSIONS

    try:
        all_entries = load_registry_json()
    except FileNotFoundError:
        return []

    # Filter
    candidates: List[SourceFileRegistryEntry] = []
    for e in all_entries:
        if families and e.source_family not in families:
            continue
        if not _is_routable(e):
            continue
        if exts and e.extension.lower() not in exts:
            continue
        if keyword and keyword.lower() not in e.file_name.lower() and keyword.lower() not in e.internal_path.lower():
            continue
        candidates.append(e)

    # Sort: prefer shorter files (better for preview)
    if prefer_short_files:
        candidates.sort(key=lambda e: e.size_bytes)

    # Deduplicate by family — take at most `limit // num_families` per family
    selected: List[SourceFileRegistryEntry] = []
    per_family: Dict[str, int] = {}
    target_families = len({e.source_family for e in candidates}) or 1
    per_family_limit = max(1, limit // target_families)

    for e in candidates:
        if len(selected) >= limit:
            break
        count = per_family.get(e.source_family, 0)
        if count >= per_family_limit:
            continue
        selected.append(e)
        per_family[e.source_family] = count + 1

    # Hydrate
    results: List[QueryResult] = []
    for entry in selected:
        try:
            pkt, loaded = hydrate_entry(entry)
            results.append(QueryResult(
                family=entry.source_family,
                registry_id=entry.registry_id,
                file_name=entry.file_name,
                internal_path=entry.internal_path,
                context_packet=pkt,
                content_preview=loaded.content_preview,
                content_hash=loaded.content_hash,
                bytes_read=loaded.bytes_read,
                hydration_status="OK",
            ))
        except HydrationError as exc:
            results.append(QueryResult(
                family=entry.source_family,
                registry_id=entry.registry_id,
                file_name=entry.file_name,
                internal_path=entry.internal_path,
                context_packet=None,  # type: ignore[arg-type]
                content_preview="",
                content_hash="",
                bytes_read=0,
                hydration_status=f"SKIPPED:{exc}",
            ))

    return results
