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

def test_ga_054_global_manifest_complete():
    """AGENTS_GLOBAL_METADATA_REMEDIATION_V1: wave_file_manifests supersedes the invalid
    ART193-ART200 requirement and constitutes the authoritative AGENTS_FILE_WIRING global
    file manifest."""
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_manifest_complete"] is True
    d2 = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert d2["global_manifest_complete"] is True


def test_ga_055_global_relation_graph_complete():
    """AGENTS_GLOBAL_METADATA_REMEDIATION_V1: relation_graph supersedes the invalid
    ART193-ART200 requirement and constitutes the authoritative AGENTS_FILE_WIRING global
    relation graph."""
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_relation_graph_complete"] is True
    d2 = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert d2["global_relation_graph_complete"] is True


def test_ga_056_art193_to_200_not_found():
    """Historical fact preserved unchanged: prior global artifact IDs ART193-ART200 were
    never found in tree or recent history. This narrative remains true even after the
    accounting error is superseded -- it is not rewritten."""
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    status = d.get("prior_global_artifacts_recovery_status", "")
    assert "ART193" in status
    assert "NOT_FOUND" in status


def test_ga_057_global_registration_superseded():
    """AGENTS_GLOBAL_METADATA_REMEDIATION_V1: global registration blocker superseded."""
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert d["global_registration_blocked"] is False


def test_ga_058_global_file_manifest_entry_present():
    """AGENTS_GLOBAL_METADATA_REMEDIATION_V1: GLOBAL_FILE_MANIFEST/GLOBAL_RELATION_GRAPH
    entries now bind to the real wave_file_manifests/relation_graph sections of this same
    file -- a real filesystem path, never an ART193-ART200 path."""
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    gfm = d["global_artifacts"]["GLOBAL_FILE_MANIFEST"]
    assert gfm["exists"] is True
    assert gfm["path"] == "periphery/agents/agents_file_wiring_artifact_index.json"
    assert gfm["role_section"] == "wave_file_manifests"
    grg = d["global_artifacts"]["GLOBAL_RELATION_GRAPH"]
    assert grg["exists"] is True
    assert grg["path"] == "periphery/agents/agents_file_wiring_artifact_index.json"
    assert grg["role_section"] == "relation_graph"


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


def test_ga_066_wave_slices_global_registration_blocked_now_empty():
    """AGENTS_GLOBAL_METADATA_REMEDIATION_V1: WAVE005_A's global registration blocker was
    a cascading consequence of the superseded ART193-ART200 requirement -- no wave slice
    remains in the active global-registration-blocked list."""
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    wsr = d["wave_status_registry"]
    grb = wsr["wave_slices_global_registration_blocked"]
    assert grb == []


def test_ga_067_gross_wave_index_entries_1924():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["gross_wave_index_entries"] == 1924
    assert d["global_summary"]["gross_documentary_rows_including_secondary"] == 1925


def test_ga_068_unique_primary_paths_1757():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["unique_primary_paths_accounted"] == 1757
    assert d["global_summary"]["primary_overlap_count"] == 167


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


def test_ga_073_campaign_metadata_total_26():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["campaign_metadata_total"] == 26
    assert d["global_summary"]["campaign_metadata_included_in_brody_primary"] == 0


def test_ga_074_campaign_metadata_registry_counts():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    reg = d["campaign_metadata_registry"]
    assert reg["total"] == 26
    assert reg["included_in_brody_primary"] == 0
    assert reg["included_in_primary_partition"] == 0
    assert len(reg["wave005_a_metadata"]) == 11
    assert len(reg["wave005_b_metadata"]) == 3
    assert len(reg["wave005_c_metadata"]) == 3
    assert len(reg["wave005_d_metadata"]) == 3
    assert len(reg["wave005_e_metadata"]) == 3
    assert len(reg["wave005_f_metadata"]) == 3


def test_ga_075_artifact_index_campaign_metadata_registry():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    reg = d["campaign_metadata_registry"]
    assert reg["total"] == 26
    assert reg["included_in_brody_primary"] == 0
    assert len(reg["wave005_a_metadata"]) == 11
    assert len(reg["wave005_b_metadata"]) == 3
    assert len(reg["wave005_c_metadata"]) == 3
    assert len(reg["wave005_d_metadata"]) == 3
    assert len(reg["wave005_e_metadata"]) == 3
    assert len(reg["wave005_f_metadata"]) == 3


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


# ---------------------------------------------------------------------------
# GA-081 — Wave005_E registration
# ---------------------------------------------------------------------------

def test_ga_081_wave005e_registered_in_global_state():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert "WAVE005_E" in d["wave_registry"]
    w5e = d["wave_registry"]["WAVE005_E"]
    assert w5e["status"] == "AGENTS_FILE_WIRING_WAVE005_E_CLOSED"
    assert w5e["functional_files_accounted"] == 124
    assert w5e["files_with_explicit_blocker"] == 0
    assert w5e["remaining_for_wave005f"] == 66
    assert w5e["primary_files_with_proved_relation"] == 124
    assert w5e["primary_files_unresolved"] == 0


def test_ga_082_wave005e_in_artifact_index_manifests():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert "WAVE005_E" in d["wave_file_manifests"]
    w5e = d["wave_file_manifests"]["WAVE005_E"]
    assert w5e["status"] == "AGENTS_FILE_WIRING_WAVE005_E_CLOSED"
    assert w5e["files_indexed"] == 124
    assert w5e["files_with_explicit_blocker"] == 0
    assert w5e["primary_files_with_proved_relation"] == 124
    assert w5e.get("relation_and_provenance_gate") == "WAVE005_E_RELATION_AND_PROVENANCE_GATE_V1_PASSED"


def test_ga_083_wave005e_in_wave_slices_registered():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    wsr = d["wave_status_registry"]
    assert "WAVE005_E" in wsr["wave_slices_registered"]


def test_ga_084_wave005e_zero_blockers():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    w5e = d["wave_registry"]["WAVE005_E"]
    assert w5e["files_with_explicit_blocker"] == 0
    assert w5e["executable_tests"] == 0


def test_ga_085_wave005e_node_in_relation_graph():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    nodes = d["relation_graph"]["nodes"]
    wave_ids = [n["wave"] for n in nodes]
    assert "WAVE005_E" in wave_ids
    w5e_node = next(n for n in nodes if n["wave"] == "WAVE005_E")
    assert w5e_node["files"] == 124


def test_ga_086_gross_note_contains_wave005e_and_f():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    note = d["global_summary"]["gross_wave_index_note"]
    assert "W5E" in note or "124" in note
    assert "W5F" in note or "66" in note


def test_ga_087_wave005e_metadata_in_global_state():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    reg = d["campaign_metadata_registry"]
    w5e_meta = reg["wave005_e_metadata"]
    assert "periphery/agents/brody_documentation_architecture_reports.index.json" in w5e_meta
    assert "periphery/agents/brody_documentation_architecture_reports.py" in w5e_meta
    assert "tests/periphery/test_brody_documentation_architecture_reports.py" in w5e_meta


# ---------------------------------------------------------------------------
# GA-088 — Wave005_F registration
# ---------------------------------------------------------------------------

def test_ga_088_wave005f_registered_in_global_state():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert "WAVE005_F" in d["wave_registry"]
    w5f = d["wave_registry"]["WAVE005_F"]
    assert w5f["status"] == "AGENTS_FILE_WIRING_WAVE005_F_CLOSED"
    assert w5f["functional_files_accounted"] == 66
    assert w5f["files_with_explicit_blocker"] == 0
    assert w5f["primary_files_with_proved_relation"] == 66
    assert w5f["primary_files_unresolved"] == 0
    assert w5f["remaining_after_wave005f"] == 0


def test_ga_089_wave005f_in_artifact_index_manifests():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert "WAVE005_F" in d["wave_file_manifests"]
    w5f = d["wave_file_manifests"]["WAVE005_F"]
    assert w5f["status"] == "AGENTS_FILE_WIRING_WAVE005_F_CLOSED"
    assert w5f["files_indexed"] == 66
    assert w5f["files_with_explicit_blocker"] == 0
    assert w5f["primary_files_with_proved_relation"] == 66
    assert w5f["primary_files_unresolved"] == 0


def test_ga_090_wave005f_in_wave_slices_registered():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    registered = d["wave_status_registry"]["wave_slices_registered"]
    assert "WAVE005_F" in registered


def test_ga_091_gross_updated_to_1924():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["gross_wave_index_entries"] == 1924


def test_ga_092_unique_updated_to_1757():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["global_summary"]["unique_primary_paths_accounted"] == 1757


def test_ga_093_artifact_index_unique_updated_to_1757():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    assert d["unique_primary_paths_accounted"] == 1757


def test_ga_094_wave005f_node_in_relation_graph():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    nodes = d["relation_graph"]["nodes"]
    wave_ids = [n["wave"] for n in nodes]
    assert "WAVE005_F" in wave_ids
    w5f_node = next(n for n in nodes if n["wave"] == "WAVE005_F")
    assert w5f_node["files"] == 66


def test_ga_095_wave005f_metadata_in_global_state():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    reg = d["campaign_metadata_registry"]
    w5f_meta = reg["wave005_f_metadata"]
    assert "periphery/agents/brody_legacy_archive_tooling_review.index.json" in w5f_meta
    assert "periphery/agents/brody_legacy_archive_tooling_review.py" in w5f_meta
    assert "tests/periphery/test_brody_legacy_archive_tooling_review.py" in w5f_meta


def test_ga_096_wave005f_metadata_in_artifact_index():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    reg = d["campaign_metadata_registry"]
    w5f_meta = reg["wave005_f_metadata"]
    assert "periphery/agents/brody_legacy_archive_tooling_review.index.json" in w5f_meta
    assert "periphery/agents/brody_legacy_archive_tooling_review.py" in w5f_meta
    assert "tests/periphery/test_brody_legacy_archive_tooling_review.py" in w5f_meta


def test_ga_097_wave005f_closes_brody_census():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    w5f = d["wave_registry"]["WAVE005_F"]
    assert w5f["remaining_after_wave005f"] == 0
    assert "902" in w5f.get("note", "") or "closes" in w5f.get("note", "").lower()


def test_ga_098_wave005f_zero_blockers_preserved_others():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["wave_registry"]["WAVE005_F"]["files_with_explicit_blocker"] == 0
    assert d["wave_registry"]["WAVE005_B"]["files_with_explicit_blocker"] == 9
    assert d["wave_registry"]["WAVE005_C"]["files_with_explicit_blocker"] == 2
    assert d["wave_registry"]["WAVE005_D"]["files_with_explicit_blocker"] == 5


def test_ga_099_wave005f_file_type_counts():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    w5f = d["wave_registry"]["WAVE005_F"]
    assert w5f["md_artifacts"] == 45
    assert w5f["json_artifacts"] == 8
    assert w5f["txt_artifacts"] == 7
    assert w5f["py_source_modules"] == 4
    assert w5f["tsx_modules"] == 1
    assert w5f["ts_modules"] == 1


def test_ga_100_wave005f_executable_counts():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    w5f = d["wave_registry"]["WAVE005_F"]
    assert w5f["not_executable_artifacts"] == 62
    assert w5f["not_a_test_modules"] == 2
    assert w5f["executable_passes"] == 2


# ---------------------------------------------------------------------------
# GA-101 to GA-115: Wave005 global reconciliation
# ---------------------------------------------------------------------------

def test_ga_101_wave005f_scope_complete_true():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["wave_registry"]["WAVE005_F"]["scope_complete"] is True


def test_ga_102_wave005f_closed_in_global_summary():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    closed = d["global_summary"]["wave_slices_closed"]
    assert "WAVE005_F" in closed
    assert "WAVE005_E" in closed


def test_ga_103_wave005f_closed_in_artifact_index_registry():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    closed = d["wave_status_registry"]["wave_slices_closed"]
    assert "WAVE005_F" in closed
    assert "WAVE005_E" in closed


def test_ga_104_wave005_global_reconciliation_in_global_state():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    rec = d.get("wave005_global_reconciliation", {})
    assert rec, "wave005_global_reconciliation must be present in global_state"


def test_ga_105_wave005_global_status():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    rec = d["wave005_global_reconciliation"]
    assert rec["wave005_global_status"] == "AGENTS_FILE_WIRING_WAVE005_PRIMARY_CENSUS_COMPLETE_GLOBAL_REGISTRATION_SUPERSEDED_FILE_BLOCKERS_REMAIN"


def test_ga_106_wave005_brody_primary_census_complete():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    rec = d["wave005_global_reconciliation"]
    assert rec["brody_primary_census_complete"] is True
    assert rec["brody_primary_total"] == 902


def test_ga_107_wave005_subwave_blockers_total_16():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    rec = d["wave005_global_reconciliation"]
    assert rec["subwave_blockers_total"] == 16


def test_ga_108_wave005_fully_closed_false():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    rec = d["wave005_global_reconciliation"]
    assert rec["wave005_fully_closed"] is False


def test_ga_109_wave005_global_reconciliation_in_artifact_index():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    rec = d.get("wave005_global_reconciliation", {})
    assert rec, "wave005_global_reconciliation must be present in artifact_index"


def test_ga_110_artifact_index_wave005_status():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    rec = d["wave005_global_reconciliation"]
    assert rec["wave005_global_status"] == "AGENTS_FILE_WIRING_WAVE005_PRIMARY_CENSUS_COMPLETE_GLOBAL_REGISTRATION_SUPERSEDED_FILE_BLOCKERS_REMAIN"


def test_ga_111_artifact_index_wave005_blockers_total():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    rec = d["wave005_global_reconciliation"]
    assert rec["subwave_blockers_total"] == 16


def test_ga_112_artifact_index_wave005_not_fully_closed():
    d = _load("periphery/agents/agents_file_wiring_artifact_index.json")
    rec = d["wave005_global_reconciliation"]
    assert rec["wave005_fully_closed"] is False


def test_ga_113_wave005_breakdown_preserved():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    rec = d["wave005_global_reconciliation"]
    bd = rec["breakdown"]
    assert bd["WAVE005_A"] == 11
    assert bd["WAVE005_B"] == 144
    assert bd["WAVE005_C"] == 51
    assert bd["WAVE005_D"] == 506
    assert bd["WAVE005_E"] == 124
    assert bd["WAVE005_F"] == 66
    assert bd["total"] == 902


def test_ga_114_blockers_per_subwave():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    rec = d["wave005_global_reconciliation"]
    detail = rec["subwave_blockers_detail"]
    assert detail["WAVE005_A"] == 0
    assert detail["WAVE005_B"] == 9
    assert detail["WAVE005_C"] == 2
    assert detail["WAVE005_D"] == 5
    assert detail["WAVE005_E"] == 0
    assert detail["WAVE005_F"] == 0


def test_ga_115_wave005f_closed_does_not_affect_blocked_subwaves():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["wave_registry"]["WAVE005_B"]["status"] == "AGENTS_FILE_WIRING_WAVE005_B_PARTIALLY_BLOCKED"
    assert d["wave_registry"]["WAVE005_C"]["status"] == "AGENTS_FILE_WIRING_WAVE005_C_PARTIALLY_BLOCKED"
    assert d["wave_registry"]["WAVE005_D"]["status"] == "AGENTS_FILE_WIRING_WAVE005_D_PARTIALLY_BLOCKED"
