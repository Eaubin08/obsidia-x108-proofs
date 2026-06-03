# runtime_wiring/source_runtime/source_runtime_cache.py
# TTL-based in-memory cache for registry entries and pack availability.
# Never caches file content — only metadata and entry lists.
# KX108_ONLY. No ACT. No write. No extraction.

from __future__ import annotations
import time
from typing import Dict, List, Optional, Tuple

from runtime_wiring.source_registry.registry_types import SourceFileRegistryEntry

_REGISTRY_TTL: float = 60.0   # seconds — registry entries
_PACK_AVAIL_TTL: float = 60.0  # seconds — pack availability probes

# Registry cache
_registry_cache: Optional[List[SourceFileRegistryEntry]] = None
_registry_loaded_at: float = 0.0

# Pack availability cache: source_zip → (available, loaded_at)
_pack_avail_cache: Dict[str, Tuple[bool, float]] = {}

# Hit/miss counters
_stats_hits: int = 0
_stats_misses: int = 0


def load_registry_cached() -> List[SourceFileRegistryEntry]:
    """Load registry with TTL-based cache. Falls back to fresh load on miss/expiry."""
    global _registry_cache, _registry_loaded_at, _stats_hits, _stats_misses
    now = time.monotonic()
    if _registry_cache is not None and (now - _registry_loaded_at) < _REGISTRY_TTL:
        _stats_hits += 1
        return _registry_cache
    from runtime_wiring.source_registry.registry_loader import load_registry_json
    _registry_cache = load_registry_json()
    _registry_loaded_at = now
    _stats_misses += 1
    return _registry_cache


def is_pack_available_cached(source_zip: str) -> bool:
    """Check pack availability with TTL-based cache. Never extracts."""
    now = time.monotonic()
    if source_zip in _pack_avail_cache:
        result, loaded_at = _pack_avail_cache[source_zip]
        if (now - loaded_at) < _PACK_AVAIL_TTL:
            return result
    from runtime_wiring.source_runtime.source_pack_resolver import is_source_pack_available
    result = is_source_pack_available(source_zip)
    _pack_avail_cache[source_zip] = (result, now)
    return result


def list_available_families_cached() -> List[str]:
    """Return families with locally available packs, using cached registry + availability."""
    try:
        entries = load_registry_cached()
    except FileNotFoundError:
        return []

    zips_per_family: Dict[str, set] = {}
    for e in entries:
        zips_per_family.setdefault(e.source_family, set()).add(e.source_zip)

    available = []
    for family, zips in zips_per_family.items():
        for z in zips:
            if is_pack_available_cached(z):
                available.append(family)
                break
    return sorted(set(available))


def clear_cache() -> None:
    """Clear all caches and reset counters. For tests and forced refresh."""
    global _registry_cache, _registry_loaded_at, _stats_hits, _stats_misses
    _registry_cache = None
    _registry_loaded_at = 0.0
    _pack_avail_cache.clear()
    _stats_hits = 0
    _stats_misses = 0


def get_cache_stats() -> dict:
    """Return current cache statistics. No side effects."""
    total = _stats_hits + _stats_misses
    return {
        "registry_cache_loaded": _registry_cache is not None,
        "registry_entry_count": len(_registry_cache) if _registry_cache else 0,
        "registry_ttl_seconds": _REGISTRY_TTL,
        "pack_avail_cached_count": len(_pack_avail_cache),
        "cache_hits": _stats_hits,
        "cache_misses": _stats_misses,
        "cache_hit_rate": round(_stats_hits / total, 3) if total > 0 else None,
        "source": "SOURCE_RUNTIME_CACHE_P28",
        "readonly": True,
        "decision_authority": "KX108_ONLY",
    }
