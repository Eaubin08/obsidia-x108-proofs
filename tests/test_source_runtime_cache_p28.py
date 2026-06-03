"""P28 — source_runtime_cache unit tests.

Covers: TTL behaviour, cache hit/miss tracking, clear_cache, pack availability cache.
All tests are read-only. No write. No extraction. No ACT.
"""
import pathlib
import sys
import time
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_runtime.source_runtime_cache import (
    load_registry_cached,
    is_pack_available_cached,
    list_available_families_cached,
    clear_cache,
    get_cache_stats,
)


@pytest.fixture(autouse=True)
def reset_cache():
    """Always start each test with a clean cache."""
    clear_cache()
    yield
    clear_cache()


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: First load is a cache miss, second call is a hit
# ─────────────────────────────────────────────────────────────────────────────

def test_cache_miss_then_hit():
    stats_before = get_cache_stats()
    assert stats_before["cache_hits"] == 0
    assert stats_before["cache_misses"] == 0

    # First call — miss
    entries1 = load_registry_cached()
    stats_after_first = get_cache_stats()
    assert stats_after_first["cache_misses"] == 1
    assert stats_after_first["cache_hits"] == 0
    assert len(entries1) > 0

    # Second call — hit (cache still fresh)
    entries2 = load_registry_cached()
    stats_after_second = get_cache_stats()
    assert stats_after_second["cache_hits"] == 1
    assert stats_after_second["cache_misses"] == 1
    assert entries1 is entries2  # same object (no copy)


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: clear_cache forces fresh load
# ─────────────────────────────────────────────────────────────────────────────

def test_clear_cache_forces_reload():
    load_registry_cached()  # warm cache
    clear_cache()

    stats = get_cache_stats()
    assert stats["cache_hits"] == 0
    assert stats["cache_misses"] == 0
    assert stats["registry_cache_loaded"] is False

    load_registry_cached()  # should be a miss again
    stats2 = get_cache_stats()
    assert stats2["cache_misses"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: TTL expiry forces reload
# ─────────────────────────────────────────────────────────────────────────────

def test_ttl_expiry_forces_reload(monkeypatch):
    import runtime_wiring.source_runtime.source_runtime_cache as cache_mod

    # Load once — miss
    load_registry_cached()
    assert get_cache_stats()["cache_misses"] == 1

    # Simulate TTL expiry by rewinding the loaded_at timestamp
    cache_mod._registry_loaded_at = time.monotonic() - 120.0  # 2 minutes ago

    # Load again — should be a miss
    load_registry_cached()
    assert get_cache_stats()["cache_misses"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Pack availability cache works
# ─────────────────────────────────────────────────────────────────────────────

def test_pack_availability_cache():
    # Load registry to know a real zip name
    entries = load_registry_cached()
    zip_names = list({e.source_zip for e in entries})[:3]
    assert len(zip_names) >= 1

    # First call per zip — uncached
    for z in zip_names:
        result = is_pack_available_cached(z)
        assert isinstance(result, bool)

    import runtime_wiring.source_runtime.source_runtime_cache as cache_mod
    assert len(cache_mod._pack_avail_cache) >= 1

    # Second call — same result from cache
    for z in zip_names:
        r1 = is_pack_available_cached(z)
        r2 = is_pack_available_cached(z)
        assert r1 == r2


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: list_available_families_cached returns at least 1 family
# ─────────────────────────────────────────────────────────────────────────────

def test_list_available_families_cached():
    families = list_available_families_cached()
    assert isinstance(families, list)
    assert len(families) >= 1
    for f in families:
        assert isinstance(f, str) and len(f) > 0


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: get_cache_stats returns correct shape
# ─────────────────────────────────────────────────────────────────────────────

def test_cache_stats_shape():
    stats = get_cache_stats()
    required_keys = [
        "registry_cache_loaded", "registry_entry_count", "registry_ttl_seconds",
        "pack_avail_cached_count", "cache_hits", "cache_misses",
        "cache_hit_rate", "source", "readonly", "decision_authority",
    ]
    for key in required_keys:
        assert key in stats, f"Missing key: {key}"

    assert stats["readonly"] is True
    assert stats["decision_authority"] == "KX108_ONLY"
    assert stats["registry_ttl_seconds"] == 60.0


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Cache hit rate computed correctly after hits + misses
# ─────────────────────────────────────────────────────────────────────────────

def test_cache_hit_rate():
    load_registry_cached()  # miss
    load_registry_cached()  # hit
    load_registry_cached()  # hit
    stats = get_cache_stats()
    assert stats["cache_misses"] == 1
    assert stats["cache_hits"] == 2
    assert stats["cache_hit_rate"] == pytest.approx(2 / 3, abs=0.01)
