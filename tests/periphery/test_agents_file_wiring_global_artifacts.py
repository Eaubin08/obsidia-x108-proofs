"""
Wave005_A Artifact Registration Gate — global artifact tests.

Verifies: global artifacts reference Wave005_A, local vs global separation,
campaign state CLOSED_NEXT_SUBWAVE_REQUIRED, census integrity.
"""
from __future__ import annotations

import json
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists():
            return p
    raise RuntimeError("Cannot locate repo root")


def _load(rel: str) -> dict:
    return json.loads((_repo_root() / rel).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# GA-001 — Global state artifact
# ---------------------------------------------------------------------------

def test_ga_001_global_state_exists():
    root = _repo_root()
    assert (root / "periphery/agents/agents_file_wiring_global_state.json").is_file()


def test_ga_002_global_state_artifact_role():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["artifact_role"] == "PROVISIONAL_CAMPAIGN_STATE_SUCCESSOR_V1"


def test_ga_003_global_state_non_sovereign():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["can_decide"] is False
    assert d["can_act"] is False
    assert d["emits_act"] is False
    assert d["memory_write"] is False


def test_ga_004_global_state_registers_wave005a():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    w5a = d["wave_registry"]["WAVE005_A"]
    assert w5a["status"] == "CLOSED_LOCALLY_GLOBAL_REGISTRATION_BLOCKED"
    assert w5a["functional_files_processed"] == 11
    assert w5a["brody_primary_census"] == 902
    assert w5a["files_pending_later_brody_subwaves"] == 891


def test_ga_005_global_state_pending_sum_891():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    p = d["wave_registry"]["WAVE005_A"]["pending_subwaves"]
    total = sum(p.values())
    assert total == 891, f"Pending sum {total} != 891"


def test_ga_006_global_state_primary_unresolved_zero():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["wave_registry"]["WAVE005_A"]["primary_unresolved"] == 0


def test_ga_007_global_state_secondary_review_two():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["wave_registry"]["WAVE005_A"]["secondary_relations_requiring_future_review"] == 2
    paths = d["wave_registry"]["WAVE005_A"]["secondary_review_paths"]
    assert len(paths) == 2
    assert any("workflow_governance_readonly" in p for p in paths)


def test_ga_008_global_state_blocker_queue_empty():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["blocker_queue"] == []


def test_ga_009_global_state_orphan_queue_empty():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["orphan_confirmed_queue"] == []


def test_ga_010_global_state_scope_complete_false():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["wave_registry"]["WAVE005_A"]["scope_complete"] is False


# ---------------------------------------------------------------------------
# GA-020 — Artifact index
# ---------------------------------------------------------------------------

def test_ga_020_artifact_index_exists():
    root = _repo_root()
    assert (root / "periphery/agents/agents_file_wiring_artifact_index.json").is_file()


def test_ga_021_artifact_index_role():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert d["artifact_role"] == "PROVISIONAL_CAMPAIGN_ARTIFACT_REGISTRY_V1"
    # OPTION B: false secondary_roles removed — no claim of GLOBAL_FILE_MANIFEST or GLOBAL_RELATION_GRAPH
    secondary = d.get("secondary_roles", [])
    assert "GLOBAL_FILE_MANIFEST" not in secondary
    assert "GLOBAL_RELATION_GRAPH" not in secondary


def test_ga_022_artifact_index_all_global_artifacts_declared():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    ga = d["global_artifacts"]
    required = [
        "GLOBAL_CAMPAIGN_STATE",
        "GLOBAL_ARTIFACT_INDEX",
        "GLOBAL_FILE_MANIFEST",
        "GLOBAL_RELATION_GRAPH",
        "GLOBAL_UNRESOLVED_QUEUE",
        "GLOBAL_BLOCKER_QUEUE",
        "GLOBAL_ORPHAN_CONFIRMED_QUEUE",
    ]
    for key in required:
        assert key in ga, f"Missing global artifact: {key}"


def test_ga_023_artifact_index_local_matrix_not_global_manifest():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    w5a = d["wave_file_manifests"]["WAVE005_A"]
    lrm = w5a["local_reconciliation_matrix"]
    assert lrm["is_global_file_manifest"] is False
    assert lrm["is_global_relation_graph"] is False
    assert lrm["artifact_role"] == "WAVE005_A_LOCAL_SCOPE_RECONCILIATION_MATRIX"


def test_ga_024_artifact_index_wave005a_in_manifests():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert "WAVE005_A" in d["wave_file_manifests"]
    w5a = d["wave_file_manifests"]["WAVE005_A"]
    assert w5a["files_indexed"] == 11
    assert w5a["status"] == "CLOSED_LOCALLY_GLOBAL_REGISTRATION_BLOCKED"


def test_ga_025_relation_graph_silent_double_count_zero():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    rg = d["relation_graph"]
    assert rg["silent_double_count"] == 0
    assert rg["cross_wave_primary_overlaps"] == 0


def test_ga_026_artifact_index_non_sovereign():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert d["can_decide"] is False
    assert d["can_act"] is False
    assert d["emits_act"] is False


# ---------------------------------------------------------------------------
# GA-030 — Global unresolved queue
# ---------------------------------------------------------------------------

def test_ga_030_global_unresolved_queue_role():
    d = _load("periphery/agents/wave005_unresolved_queue.json")
    assert d.get("artifact_role") == "GLOBAL_UNRESOLVED_QUEUE"
    assert d.get("queue_scope") == "AGENTS_FILE_WIRING_CAMPAIGN_ALL_WAVES"


def test_ga_031_global_unresolved_primary_zero():
    d = _load("periphery/agents/wave005_unresolved_queue.json")
    assert d["primary_unresolved"] == 0


def test_ga_032_global_unresolved_secondary_two():
    d = _load("periphery/agents/wave005_unresolved_queue.json")
    assert d["secondary_relations_requiring_review"] == 2


# ---------------------------------------------------------------------------
# GA-040 — Local campaign state correctly flagged
# ---------------------------------------------------------------------------

def test_ga_040_local_state_role():
    d = _load("periphery/agents/wave005_campaign_state.json")
    assert d.get("artifact_role") == "WAVE005_A_LOCAL_CAMPAIGN_STATE"
    assert d.get("is_global_campaign_state") is False


def test_ga_041_local_state_points_to_global():
    d = _load("periphery/agents/wave005_campaign_state.json")
    assert d.get("global_campaign_state_path") == "periphery/agents/agents_file_wiring_global_state.json"
    assert d.get("global_artifact_index_path") == "periphery/agents/agents_file_wiring_artifact_index.json"


def test_ga_042_local_state_wave005a_registration_blocked():
    d = _load("periphery/agents/wave005_campaign_state.json")
    # OPTION B: global registration is blocked — prior global artifacts not found
    assert d.get("WAVE005_A_GLOBAL_REGISTRATION_COMPLETE") is False
    assert d.get("WAVE005_A_GLOBAL_REGISTRATION_STATUS") == "BLOCKED_PRIOR_ARTIFACTS_NOT_FOUND"


# ---------------------------------------------------------------------------
# GA-050 — Census invariants not changed by registration
# ---------------------------------------------------------------------------

def test_ga_050_brody_primary_still_902():
    """Registration of global artifacts must NOT change primary census."""
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["wave_registry"]["WAVE005_A"]["brody_primary_census"] == 902


def test_ga_051_campaign_metadata_total_eight():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["wave_registry"]["WAVE005_A"]["brody_campaign_metadata"] == 8


def test_ga_052_wave005a_functional_eleven():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["wave_registry"]["WAVE005_A"]["functional_files_processed"] == 11


def test_ga_053_global_artifacts_not_in_brody_primary():
    """Global artefact files do not contain 'brody' in name — not picked up by brody census scan."""
    root = _repo_root()
    global_files = [
        "periphery/agents/agents_file_wiring_global_state.json",
        "periphery/agents/agents_file_wiring_artifact_index.json",
    ]
    for rel in global_files:
        assert (root / rel).is_file(), f"Global artifact missing: {rel}"
        assert "brody" not in rel.lower(), (
            f"Global artifact {rel} contains 'brody' in name — "
            "would be incorrectly picked up by brody census scan"
        )


# ---------------------------------------------------------------------------
# GA-054 to GA-058 — OPTION B: provisional state, blocking metadata
# ---------------------------------------------------------------------------

def test_ga_054_global_manifest_not_complete():
    """OPTION B: no authoritative AGENTS_FILE_WIRING global file manifest exists."""
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_manifest_complete"] is False
    d2 = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert d2["global_manifest_complete"] is False


def test_ga_055_global_relation_graph_not_complete():
    """OPTION B: no authoritative AGENTS_FILE_WIRING global relation graph exists."""
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_relation_graph_complete"] is False
    d2 = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert d2["global_relation_graph_complete"] is False


def test_ga_056_art193_to_200_not_found():
    """OPTION B: prior global artifact IDs ART193-ART200 absent from tree and recent history."""
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    status = d.get("prior_global_artifacts_recovery_status", "")
    assert "ART193" in status
    assert "NOT_FOUND" in status


def test_ga_057_global_registration_blocked():
    """OPTION B: artifact index declares global registration as blocked."""
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert d["global_registration_blocked"] is True


def test_ga_058_global_file_manifest_entry_absent():
    """OPTION B: GLOBAL_FILE_MANIFEST entry in artifact index has exists=false and path=null."""
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    gfm = d["global_artifacts"]["GLOBAL_FILE_MANIFEST"]
    assert gfm["exists"] is False
    assert gfm["path"] is None
    grg = d["global_artifacts"]["GLOBAL_RELATION_GRAPH"]
    assert grg["exists"] is False
    assert grg["path"] is None


# ---------------------------------------------------------------------------
# GA-059 to GA-080 — Wave005_C accounting repair: campaign consistency gate
# ---------------------------------------------------------------------------

def test_ga_059_wave005b_registered_in_global_state():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert "WAVE005_B" in d["wave_registry"]
    w5b = d["wave_registry"]["WAVE005_B"]
    assert w5b["status"] == "AGENTS_FILE_WIRING_WAVE005_B_PARTIALLY_BLOCKED"
    assert w5b["functional_files_accounted"] == 144


def test_ga_060_wave005c_registered_in_global_state():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert "WAVE005_C" in d["wave_registry"]
    w5c = d["wave_registry"]["WAVE005_C"]
    assert w5c["status"] == "AGENTS_FILE_WIRING_WAVE005_C_PARTIALLY_BLOCKED"
    assert w5c["functional_files_accounted"] == 51
    assert w5c["files_with_explicit_blocker"] == 2


def test_ga_061_wave005b_in_artifact_index_manifests():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert "WAVE005_B" in d["wave_file_manifests"]
    w5b = d["wave_file_manifests"]["WAVE005_B"]
    assert w5b["status"] == "AGENTS_FILE_WIRING_WAVE005_B_PARTIALLY_BLOCKED"
    assert w5b["files_indexed"] == 144


def test_ga_062_wave005c_in_artifact_index_manifests():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert "WAVE005_C" in d["wave_file_manifests"]
    w5c = d["wave_file_manifests"]["WAVE005_C"]
    assert w5c["status"] == "AGENTS_FILE_WIRING_WAVE005_C_PARTIALLY_BLOCKED"
    assert w5c["files_indexed"] == 51
    assert w5c["files_with_explicit_blocker"] == 2


def test_ga_063_wave_slices_registered():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    wsr = d["wave_status_registry"]
    registered = wsr["wave_slices_registered"]
    for w in ["WAVE001", "WAVE002", "WAVE003", "WAVE004", "WAVE005_A", "WAVE005_B", "WAVE005_C"]:
        assert w in registered, f"{w} missing from wave_slices_registered"


def test_ga_064_wave_slices_fully_closed():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    wsr = d["wave_status_registry"]
    closed = wsr["wave_slices_fully_closed"]
    for w in ["WAVE001", "WAVE002", "WAVE003", "WAVE004"]:
        assert w in closed
    assert "WAVE005_A" not in closed
    assert "WAVE005_B" not in closed
    assert "WAVE005_C" not in closed


def test_ga_065_wave_slices_partially_blocked():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    wsr = d["wave_status_registry"]
    blocked = wsr["wave_slices_partially_blocked"]
    assert "WAVE005_B" in blocked
    assert "WAVE005_C" in blocked
    assert "WAVE005_A" not in blocked


def test_ga_066_wave_slices_global_registration_blocked():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    wsr = d["wave_status_registry"]
    grb = wsr["wave_slices_global_registration_blocked"]
    assert "WAVE005_A" in grb
    assert "WAVE005_B" not in grb
    assert "WAVE005_C" not in grb


def test_ga_067_gross_wave_index_entries_1228():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["gross_wave_index_entries"] == 1228


def test_ga_068_unique_primary_paths_1061():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["unique_primary_paths_accounted"] == 1061


def test_ga_069_known_cross_wave_overlap_167():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["known_cross_wave_overlap_paths"] == 167


def test_ga_070_silent_double_count_zero():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["silent_double_count"] == 0


def test_ga_071_gross_total_reconciled():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["gross_total_reconciled"] is True
    assert d["global_summary"]["unique_total_computed_from_paths"] is True


def test_ga_072_census_902_preserved_after_wave005c():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["current_active_brody_primary"] == 902


def test_ga_073_campaign_metadata_total_17():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["campaign_metadata_total"] == 17
    assert d["global_summary"]["campaign_metadata_included_in_brody_primary"] == 0


def test_ga_074_campaign_metadata_registry_counts():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    reg = d["campaign_metadata_registry"]
    assert reg["total"] == 17
    assert reg["included_in_brody_primary"] == 0
    assert reg["included_in_primary_partition"] == 0
    assert len(reg["wave005_a_metadata"]) == 11
    assert len(reg["wave005_b_metadata"]) == 3
    assert len(reg["wave005_c_metadata"]) == 3


def test_ga_075_artifact_index_campaign_metadata_registry():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    reg = d["campaign_metadata_registry"]
    assert reg["total"] == 17
    assert reg["included_in_brody_primary"] == 0
    assert len(reg["wave005_a_metadata"]) == 11
    assert len(reg["wave005_b_metadata"]) == 3
    assert len(reg["wave005_c_metadata"]) == 3


def test_ga_076_wave005b_metadata_excluded_from_primary():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    reg = d["campaign_metadata_registry"]
    wb = reg["wave005_b_metadata"]
    assert "periphery/agents/brody_integration_runtime_api_system.index.json" in wb
    assert "periphery/agents/brody_integration_runtime_api_system.py" in wb
    assert "tests/periphery/test_brody_integration_runtime_api_system.py" in wb


def test_ga_077_wave005c_metadata_excluded_from_primary():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    reg = d["campaign_metadata_registry"]
    wc = reg["wave005_c_metadata"]
    assert "periphery/agents/brody_protocols_connectors_scripts.index.json" in wc
    assert "periphery/agents/brody_protocols_connectors_scripts.py" in wc
    assert "tests/periphery/test_brody_protocols_connectors_scripts.py" in wc


def test_ga_078_relation_graph_has_wave005b_node():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    nodes = d["relation_graph"]["nodes"]
    wave_ids = [n["wave"] for n in nodes]
    assert "WAVE005_B" in wave_ids
    w5b_node = next(n for n in nodes if n["wave"] == "WAVE005_B")
    assert w5b_node["files"] == 144


def test_ga_079_documented_catalog_overlap_wave001_wave002():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    dco = d["relation_graph"]["documented_catalog_overlaps"]
    assert "WAVE001_WAVE002" in dco
    assert dco["WAVE001_WAVE002"]["overlap_paths_count"] == 167
    assert dco["WAVE001_WAVE002"]["type"] == "INTENTIONAL_DUAL_PERSPECTIVE"


def test_ga_080_wave005c_blockers_preserved():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    w5c = d["wave_registry"]["WAVE005_C"]
    assert w5c["files_with_explicit_blocker"] == 2
    assert w5c["consistent_failing_test_files"] == 1
    assert w5c["blocked_source_without_consumer"] == 1
    assert w5c["status"] == "AGENTS_FILE_WIRING_WAVE005_C_PARTIALLY_BLOCKED"
