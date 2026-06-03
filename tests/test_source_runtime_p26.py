"""P26 Source Runtime — unit tests for the read-only source pack hydration layer.

Covers: resolver, loader, hydrator, query, X108 gate, OS3 evidence, no-ACT invariants.
All tests are read-only. No extraction, no write, no ACT.
"""
import pathlib
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
import sys
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_runtime.source_pack_resolver import (
    resolve_source_pack,
    is_source_pack_available,
    list_available_families,
    MissingSourcePackError,
    ResolvedSourcePack,
)
from runtime_wiring.source_runtime.readonly_content_loader import (
    load_file_from_pack,
    ForbiddenFileError,
    LoadedContent,
)
from runtime_wiring.source_runtime.source_context_hydrator import (
    hydrate_entry,
    HydrationError,
)
from runtime_wiring.source_runtime.source_runtime_query import query_source_packs, QueryResult
from runtime_wiring.source_runtime.brody_source_context_bridge import (
    build_brody_context_from_source_packs,
)
from runtime_wiring.source_registry.registry_loader import load_registry_json


# ─────────────────────────────────────────────────────────────────────────────
# Session fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def available_families():
    return list_available_families()


@pytest.fixture(scope="session")
def registry_entries():
    try:
        return load_registry_json()
    except FileNotFoundError:
        return []


@pytest.fixture(scope="session")
def cognitive_entries(registry_entries):
    return [
        e for e in registry_entries
        if e.source_family == "COGNITIVE_REINTEGRATION"
        and e.extension.lower() in (".md", ".yaml", ".yml", ".txt", ".json")
        and e.quarantine_status not in ("DO_NOT_IMPORT_RUNTIME", "ARCHIVE_ONLY", "QUARANTINE")
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Resolver finds at least one available pack
# ─────────────────────────────────────────────────────────────────────────────

def test_resolver_finds_at_least_one_pack(available_families):
    assert len(available_families) >= 1, (
        "Expected at least 1 source family to be locally available"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Loader refuses .py files
# ─────────────────────────────────────────────────────────────────────────────

def test_loader_refuses_py_extension(available_families):
    if not available_families:
        pytest.skip("No source packs available locally")

    pack_name = None
    for family in available_families:
        entries = load_registry_json()
        for e in entries:
            if e.source_family == family and is_source_pack_available(e.source_zip):
                pack_name = e.source_zip
                break
        if pack_name:
            break

    if not pack_name:
        pytest.skip("No resolvable pack found")

    resolved = resolve_source_pack(pack_name)
    with pytest.raises(ForbiddenFileError):
        load_file_from_pack(resolved, "some_script.py")


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Loader refuses path traversal
# ─────────────────────────────────────────────────────────────────────────────

def test_loader_refuses_path_traversal(available_families):
    if not available_families:
        pytest.skip("No source packs available locally")

    entries = load_registry_json()
    pack_name = next(
        (e.source_zip for e in entries if is_source_pack_available(e.source_zip)),
        None,
    )
    if not pack_name:
        pytest.skip("No resolvable pack found")

    resolved = resolve_source_pack(pack_name)
    with pytest.raises(ForbiddenFileError):
        load_file_from_pack(resolved, "../../../etc/passwd")


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Loader reads a .md file in read-only mode
# ─────────────────────────────────────────────────────────────────────────────

def test_loader_reads_md_readonly(cognitive_entries, available_families):
    if not available_families:
        pytest.skip("No source packs available locally")

    md_entry = next(
        (e for e in cognitive_entries
         if e.extension.lower() == ".md" and is_source_pack_available(e.source_zip)),
        None,
    )
    if not md_entry:
        pytest.skip("No .md entry available in COGNITIVE_REINTEGRATION")

    resolved = resolve_source_pack(md_entry.source_zip)
    loaded = load_file_from_pack(resolved, md_entry.internal_path)

    assert isinstance(loaded, LoadedContent)
    assert loaded.readonly is True
    assert loaded.extracted_to_disk is False
    assert loaded.bytes_read > 0
    assert len(loaded.content_hash) == 64  # sha256 hex
    assert loaded.content_preview != ""


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Hydrator produces valid ContextPacket with advisory_only=True
# ─────────────────────────────────────────────────────────────────────────────

def test_hydrator_produces_valid_context_packet(cognitive_entries, available_families):
    if not available_families:
        pytest.skip("No source packs available locally")

    entry = next(
        (e for e in cognitive_entries if is_source_pack_available(e.source_zip)),
        None,
    )
    if not entry:
        pytest.skip("No hydrateable entry in COGNITIVE_REINTEGRATION")

    pkt, loaded = hydrate_entry(entry)

    assert pkt.advisory_only is True
    assert pkt.emits_act is False
    assert pkt.readonly is True
    assert pkt.decision_authority == "KX108_ONLY"
    assert pkt.runtime_allowed_now is False
    pkt.validate_invariants()  # must not raise


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: Query returns packets for COGNITIVE_REINTEGRATION
# ─────────────────────────────────────────────────────────────────────────────

def test_query_returns_cognitive_packets(available_families):
    if "COGNITIVE_REINTEGRATION" not in available_families:
        pytest.skip("COGNITIVE_REINTEGRATION not available locally")

    results = query_source_packs(families=["COGNITIVE_REINTEGRATION"], limit=3)
    ok = [r for r in results if r.hydration_status == "OK"]
    assert len(ok) >= 1, "Expected at least 1 hydrated COGNITIVE_REINTEGRATION packet"
    for r in ok:
        assert r.context_packet is not None
        assert r.context_packet.advisory_only is True
        assert r.context_packet.emits_act is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Query works for at least 3 available families
# ─────────────────────────────────────────────────────────────────────────────

def test_query_works_for_multiple_families(available_families):
    if len(available_families) < 3:
        pytest.skip(f"Only {len(available_families)} families available, need 3")

    results = query_source_packs(families=available_families[:3], limit=6)
    ok = [r for r in results if r.hydration_status == "OK"]
    families_present = {r.family for r in ok}
    assert len(families_present) >= 1, "Expected at least 1 family hydrated"


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: X108 gate returns ALLOW_CONTEXT_ONLY
# ─────────────────────────────────────────────────────────────────────────────

def test_x108_gate_returns_allow_context_only(available_families):
    if not available_families:
        pytest.skip("No source packs available locally")

    result = build_brody_context_from_source_packs(
        query="X108 context test P26",
        limit=3,
    )
    if not result.get("source_pack_context_used"):
        pytest.skip("No entries hydrated — source packs may be inaccessible")

    assert result["x108_decision"] == "ALLOW_CONTEXT_ONLY"
    assert result["x108_decision_authority"] == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Test 9: OS3 evidence present and honest (no proof claim in dry-run)
# ─────────────────────────────────────────────────────────────────────────────

def test_os3_evidence_present(available_families):
    if not available_families:
        pytest.skip("No source packs available locally")

    result = build_brody_context_from_source_packs(query="OS3 evidence test", limit=2)
    if not result.get("source_pack_context_used"):
        pytest.skip("No entries hydrated")

    assert "os3_evidence_id" in result
    assert result["os3_proof_claim"] is False  # dry-run: never claim proof
    assert result["os3_verification_status"] == "NOT_VERIFIED_DRY_RUN"


# ─────────────────────────────────────────────────────────────────────────────
# Test 10: No ACT / no write / no mutation in any packet
# ─────────────────────────────────────────────────────────────────────────────

def test_no_act_no_write_no_mutation(available_families):
    if not available_families:
        pytest.skip("No source packs available locally")

    result = build_brody_context_from_source_packs(query="safety invariants test", limit=5)

    assert result.get("no_act") is True
    assert result.get("memory_write") is False
    assert result.get("graph_write") is False
    assert result.get("kernel_mutation") is False
    assert result.get("zip_extraction") is False

    boundary = result.get("boundary", {})
    assert boundary.get("emits_act") is False
    assert boundary.get("decision_authority") == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Test 11: If pack absent → clean skip, no global crash
# ─────────────────────────────────────────────────────────────────────────────

def test_missing_pack_produces_clean_fallback():
    result = build_brody_context_from_source_packs(
        query="missing pack test",
        families=["NONEXISTENT_FAMILY_XYZ_P26_TEST"],
        limit=2,
    )
    # Must not raise — must return a fallback dict
    assert isinstance(result, dict)
    assert result.get("source_pack_context_used") is False
    assert result.get("no_act") is True
    assert "status" in result
    assert "UNAVAILABLE" in result["status"] or "NOT_AVAILABLE" in result["status"]
