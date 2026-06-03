# tests/test_source_registry_p9b.py
# P9B Registry-to-Adapter Dry-Run Tests
# Phase: P9B / Boundary: P9B_REGISTRY_TO_ADAPTER_TESTS_ONLY
# No zip extraction. No source pack import. No runtime activation.
# Run: python -m pytest tests/test_source_registry_p9b.py -v

from __future__ import annotations

import ast
import json
import pathlib
import sys

import pytest

# ── Repo root resolution ──────────────────────────────────────────────────────
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_registry.registry_loader import (
    count_by_field,
    count_by_family,
    filter_runtime_forbidden,
    load_registry_csv,
    load_registry_json,
    validate_registry,
)
from runtime_wiring.source_registry.registry_types import (
    DO_NOT_IMPORT_DECISIONS,
    SourceFileRegistryEntry,
)
from runtime_wiring.source_registry.adapter_target_map import ADAPTER_TARGET_MAP
from runtime_wiring.source_registry.registry_to_adapter_dry_run import (
    _ADAPTER_DISPATCH,
    _FORBIDDEN_DECISIONS,
    entry_to_metadata,
    reject_forbidden_entries,
    route_entry_to_context_packet,
    route_registry_packets_to_x108,
    route_sample_by_family,
    select_routable_entries,
)
from runtime_wiring.source_adapters import (
    atlas_to_context_packet,
    cognitive_to_context_packet,
    compliance_to_context_packet,
    rssi_rgpd_to_context_packet,
)

# ── Registry file paths ───────────────────────────────────────────────────────
_REGISTRY_DIR = _REPO_ROOT / "runtime_wiring" / "source_registry"
_REGISTRY_JSON = _REGISTRY_DIR / "source_file_registry.json"
_REGISTRY_CSV = _REGISTRY_DIR / "source_file_registry.csv"
_REGISTRY_SUMMARY = _REGISTRY_DIR / "source_registry_summary.json"

_EXPECTED_FAMILIES = {
    "COGNITIVE_REINTEGRATION",
    "RSSI_RGPD",
    "ATLAS",
    "COMPLIANCE_DATA_GOVERNANCE",
    # P24 — new families added in coverage repair
    "RSSI_SECURITY_PRESENTATION",
    "EXTERNAL_SIGNALS",
    "NARRATIVE_PROVENANCE_LAYER",
    # P32 — 8th family
    "OS_TRAD_REVERSE_OS",
}

_EXPECTED_TOTAL = 15853  # P32: +546 OS_TRAD_REVERSE_OS entries


# ── Session-scoped fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="session")
def registry_json():
    return load_registry_json(_REGISTRY_JSON)


@pytest.fixture(scope="session")
def registry_summary():
    return json.loads(_REGISTRY_SUMMARY.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def routable_entries(registry_json):
    routable, _ = reject_forbidden_entries(registry_json)
    return routable


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Registry files exist
# ─────────────────────────────────────────────────────────────────────────────

def test_registry_files_exist():
    """All 3 registry output files must exist."""
    assert _REGISTRY_JSON.is_file(), f"Missing: {_REGISTRY_JSON}"
    assert _REGISTRY_CSV.is_file(), f"Missing: {_REGISTRY_CSV}"
    assert _REGISTRY_SUMMARY.is_file(), f"Missing: {_REGISTRY_SUMMARY}"
    assert _REGISTRY_JSON.stat().st_size > 0, "registry JSON is empty"
    assert _REGISTRY_CSV.stat().st_size > 0, "registry CSV is empty"


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Registry loads (JSON and CSV)
# ─────────────────────────────────────────────────────────────────────────────

def test_registry_loads_json_and_csv():
    """Both JSON and CSV loaders must return non-empty lists of SourceFileRegistryEntry."""
    json_entries = load_registry_json(_REGISTRY_JSON)
    assert len(json_entries) > 0, "JSON loader returned empty list"
    assert isinstance(json_entries[0], SourceFileRegistryEntry)

    csv_entries = load_registry_csv(_REGISTRY_CSV)
    assert len(csv_entries) > 0, "CSV loader returned empty list"
    assert isinstance(csv_entries[0], SourceFileRegistryEntry)

    # Both loaders should return the same count
    assert len(json_entries) == len(csv_entries), (
        f"JSON ({len(json_entries)}) vs CSV ({len(csv_entries)}) count mismatch"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Summary counts match expected
# ─────────────────────────────────────────────────────────────────────────────

def test_registry_summary_counts_match_expected(registry_summary):
    """Summary JSON must report correct totals and safety invariants."""
    assert registry_summary["total_entries"] == _EXPECTED_TOTAL, (
        f"Expected {_EXPECTED_TOTAL} entries, got {registry_summary['total_entries']}"
    )
    assert registry_summary["runtime_allowed_now_true_count"] == 0
    assert registry_summary["emits_act_true_count"] == 0
    assert registry_summary["emits_decision_true_count"] == 0
    assert registry_summary["safety_invariants_ok"] is True
    assert registry_summary["zip_extraction"] is False
    assert registry_summary["source_pack_import"] is False
    assert registry_summary["decision_authority"] == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: All 4 families present
# ─────────────────────────────────────────────────────────────────────────────

def test_all_families_present(registry_json):
    """All 4 source families must be present in the registry."""
    families = {e.source_family for e in registry_json}
    assert _EXPECTED_FAMILIES.issubset(families), (
        f"Missing families: {_EXPECTED_FAMILIES - families}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: runtime_allowed_now always False
# ─────────────────────────────────────────────────────────────────────────────

def test_all_runtime_allowed_false(registry_json):
    """Every entry must have runtime_allowed_now=False."""
    violations = [e.registry_id for e in registry_json if e.runtime_allowed_now]
    assert violations == [], (
        f"runtime_allowed_now=True on {len(violations)} entries: {violations[:3]}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: emits_act always False
# ─────────────────────────────────────────────────────────────────────────────

def test_all_emits_act_false(registry_json):
    """Every entry must have emits_act=False."""
    violations = [e.registry_id for e in registry_json if e.emits_act]
    assert violations == [], (
        f"emits_act=True on {len(violations)} entries: {violations[:3]}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: emits_decision always False
# ─────────────────────────────────────────────────────────────────────────────

def test_all_emits_decision_false(registry_json):
    """Every entry must have emits_decision=False."""
    violations = [e.registry_id for e in registry_json if e.emits_decision]
    assert violations == [], (
        f"emits_decision=True on {len(violations)} entries: {violations[:3]}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: .py files are DO_NOT_IMPORT_RUNTIME
# ─────────────────────────────────────────────────────────────────────────────

def test_py_entries_are_do_not_import_runtime(registry_json):
    """All .py files must have recommended_decision=DO_NOT_IMPORT_RUNTIME."""
    py_entries = [e for e in registry_json if e.extension.lower() == ".py"]
    assert len(py_entries) == 272, f"Expected 272 .py files (240 orig + 32 RSSI Security), got {len(py_entries)}"
    bad = [e for e in py_entries if e.recommended_decision != "DO_NOT_IMPORT_RUNTIME"]
    assert bad == [], (
        f"{len(bad)} .py entries without DO_NOT_IMPORT_RUNTIME: "
        + str([e.registry_id for e in bad[:3]])
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 9: Quarantine/archive entries are not routable
# ─────────────────────────────────────────────────────────────────────────────

def test_quarantine_archive_entries_not_routable(registry_json):
    """Entries with QUARANTINE or ARCHIVE_ONLY quarantine_status must be rejected."""
    forbidden_entries = [
        e for e in registry_json
        if e.quarantine_status in {"QUARANTINE", "ARCHIVE_ONLY", "DO_NOT_IMPORT_RUNTIME", "QUARANTINE_CACHE"}
    ]
    routable, rejected = reject_forbidden_entries(forbidden_entries)
    assert routable == [], (
        f"{len(routable)} quarantine/archive entries passed as routable: "
        + str([e.registry_id for e in routable[:3]])
    )
    assert len(rejected) == len(forbidden_entries)

    # Also test via route_entry_to_context_packet raises ValueError
    if forbidden_entries:
        import pytest as _pytest
        with _pytest.raises(ValueError, match="ROUTING_REFUSED"):
            route_entry_to_context_packet(forbidden_entries[0])


# ─────────────────────────────────────────────────────────────────────────────
# Test 10: adapter_targets exist in dispatch table
# ─────────────────────────────────────────────────────────────────────────────

def test_adapter_targets_exist(registry_json):
    """Every routable entry must reference an adapter_target present in _ADAPTER_DISPATCH."""
    routable = select_routable_entries(registry_json)
    unknown_adapters = {
        e.adapter_target for e in routable
        if e.adapter_target not in _ADAPTER_DISPATCH
    }
    assert unknown_adapters == set(), (
        f"Unknown adapter targets in routable entries: {unknown_adapters}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 11: Route 1 entry per family to ContextPacket
# ─────────────────────────────────────────────────────────────────────────────

def test_route_one_entry_per_family_to_context_packet(registry_json):
    """One routable entry per family must be convertible to a ContextPacket."""
    by_family = route_sample_by_family(registry_json, sample_size=1)

    assert set(by_family.keys()) == _EXPECTED_FAMILIES, (
        f"Missing families in routing: {_EXPECTED_FAMILIES - set(by_family.keys())}"
    )
    for family, packets in by_family.items():
        assert len(packets) == 1, f"No packet produced for family {family}"
        pkt = packets[0]
        assert pkt.source_family if hasattr(pkt, 'source_family') else True
        assert pkt.advisory_only is True
        assert pkt.readonly is True
        assert pkt.emits_act is False
        assert pkt.decision_authority == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Test 12: Routed packets never emit act
# ─────────────────────────────────────────────────────────────────────────────

def test_routed_packets_never_emit_act(registry_json):
    """All packets produced from registry entries must have emits_act=False."""
    by_family = route_sample_by_family(registry_json, sample_size=3)
    for family, packets in by_family.items():
        for pkt in packets:
            assert pkt.emits_act is False, (
                f"emits_act=True on packet from {family}: {pkt.context_id}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 13: Routed packets have KX108 authority
# ─────────────────────────────────────────────────────────────────────────────

def test_routed_packets_have_kx108_authority(registry_json):
    """All packets produced from registry entries must have decision_authority=KX108_ONLY."""
    by_family = route_sample_by_family(registry_json, sample_size=3)
    for family, packets in by_family.items():
        for pkt in packets:
            assert pkt.decision_authority == "KX108_ONLY", (
                f"Bad authority on packet from {family}: {pkt.decision_authority}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 14: Route registry packets context-only → ALLOW_CONTEXT_ONLY
# ─────────────────────────────────────────────────────────────────────────────

def test_route_registry_packets_context_only_allows_context_only(registry_json):
    """routing without critical action must yield ALLOW_CONTEXT_ONLY."""
    result = route_registry_packets_to_x108(
        registry_json,
        critical_action_requested=False,
        sample_size=1,
    )
    assert result["status"] == "ROUTED"
    assert result["decision"] == "ALLOW_CONTEXT_ONLY"
    assert result["emits_act"] is False
    assert result["dry_run"] is True
    assert result["proof_claim"] is False
    assert result["all_packets_no_act"] is True
    assert result["all_packets_kx108_authority"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 15: Route registry packets critical action → HOLD
# ─────────────────────────────────────────────────────────────────────────────

def test_route_registry_packets_critical_action_holds(registry_json):
    """routing with critical_action_requested=True must yield HOLD."""
    result = route_registry_packets_to_x108(
        registry_json,
        critical_action_requested=True,
        sample_size=1,
    )
    assert result["status"] == "ROUTED"
    assert result["decision"] == "HOLD"
    assert result["emits_act"] is False
    assert result["dry_run"] is True
    assert result["proof_claim"] is False
    assert result["envelope_id"] is not None


# ─────────────────────────────────────────────────────────────────────────────
# Test 16: No source pack file read in registry_to_adapter_dry_run.py
# ─────────────────────────────────────────────────────────────────────────────

def test_no_source_pack_file_read():
    """registry_to_adapter_dry_run.py must not contain open() calls on zip/source paths."""
    target = _REPO_ROOT / "runtime_wiring" / "source_registry" / "registry_to_adapter_dry_run.py"
    source = target.read_text(encoding="utf-8")

    violations = []
    for lineno, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Must not open _source_packs or .zip files
        if "_source_packs" in stripped:
            violations.append(f"line {lineno}: references '_source_packs'")
        if ".zip" in stripped and "open(" in stripped:
            violations.append(f"line {lineno}: opens .zip file")

    assert violations == [], "Source pack/zip read found:\n" + "\n".join(violations)


# ─────────────────────────────────────────────────────────────────────────────
# Test 17: No zip extraction anywhere in source_registry/
# ─────────────────────────────────────────────────────────────────────────────

def test_no_zip_extraction():
    """No file in source_registry/ may import zipfile, tarfile, or call ZipFile()."""
    registry_dir = _REPO_ROOT / "runtime_wiring" / "source_registry"
    violations = []
    for py_file in registry_dir.glob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", "") or ""
                names = [alias.name for alias in getattr(node, "names", [])]
                for forbidden in ("zipfile", "tarfile", "shutil"):
                    if forbidden in mod or any(forbidden in n for n in names):
                        violations.append(f"{py_file.name}: imports {forbidden}")
    assert violations == [], "Zip/tar extraction imports found:\n" + "\n".join(violations)


# ─────────────────────────────────────────────────────────────────────────────
# Test 18: No forbidden imports in source_registry/ module
# ─────────────────────────────────────────────────────────────────────────────

def test_no_forbidden_imports():
    """source_registry/ must not import from apps/, periphery/, connectors/, sigma/."""
    forbidden_tops = {"apps", "periphery", "connectors", "sigma"}
    registry_dir = _REPO_ROOT / "runtime_wiring" / "source_registry"
    violations = []
    for py_file in registry_dir.glob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", "") or ""
                top = mod.split(".")[0] if mod else ""
                if top in forbidden_tops:
                    violations.append(f"{py_file.name}: imports '{mod}'")
    assert violations == [], "Forbidden imports found:\n" + "\n".join(violations)


# ─────────────────────────────────────────────────────────────────────────────
# Test 19: OS3 evidence is dry-run only (proof_claim=False)
# ─────────────────────────────────────────────────────────────────────────────

def test_os3_evidence_dry_run_only(registry_json):
    """OS3 evidence produced by routing must have proof_claim=False."""
    result = route_registry_packets_to_x108(
        registry_json,
        critical_action_requested=False,
        sample_size=1,
    )
    assert result["proof_claim"] is False
    assert result["verification_status"] == "NOT_VERIFIED_DRY_RUN"

    result_b = route_registry_packets_to_x108(
        registry_json,
        critical_action_requested=True,
        sample_size=1,
    )
    assert result_b["proof_claim"] is False
    assert result_b["verification_status"] == "NOT_VERIFIED_DRY_RUN"


# ─────────────────────────────────────────────────────────────────────────────
# Test 20: No packages/ directory created
# ─────────────────────────────────────────────────────────────────────────────

def test_no_packages_created():
    """packages/ directory must not exist in the repo root."""
    packages_dir = _REPO_ROOT / "packages"
    assert not packages_dir.exists(), (
        "packages/ directory found — NO_PACKAGE constraint violated"
    )
