"""
AGENTS_FILE_WIRING_FAMILY_FINAL_RECONCILIATION_GATE_V1 — Test suite.

Coverage: FAMILY-001 to FAMILY-060
NON_SOVEREIGN: can_decide=false, can_act=false, emits_act=false, memory_write=false.
"""
import json
import pytest
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists():
            return p
    raise RuntimeError("Cannot locate repository root")


def _load(rel: str) -> dict:
    with open(_repo_root() / rel, encoding="utf-8") as f:
        return json.load(f)


def _gs():
    return _load("periphery/agents/agents_file_wiring_global_state.json")


def _ai():
    return _load("periphery/agents/agents_file_wiring_artifact_index.json")


# ---------------------------------------------------------------------------
# FAMILY-001 to FAMILY-010: Waves registered (10 waves)
# ---------------------------------------------------------------------------

def test_family001_all_10_waves_registered_in_global_state():
    d = _gs()
    wr = d["wave_registry"]
    for wave in ["WAVE001", "WAVE002", "WAVE003", "WAVE004",
                 "WAVE005_A", "WAVE005_B", "WAVE005_C", "WAVE005_D", "WAVE005_E", "WAVE005_F"]:
        assert wave in wr, f"Missing wave: {wave}"


def test_family002_all_10_waves_in_artifact_index():
    d = _ai()
    registered = d["wave_status_registry"]["wave_slices_registered"]
    for wave in ["WAVE001", "WAVE002", "WAVE003", "WAVE004",
                 "WAVE005_A", "WAVE005_B", "WAVE005_C", "WAVE005_D", "WAVE005_E", "WAVE005_F"]:
        assert wave in registered, f"Missing wave in artifact index: {wave}"


def test_family003_wave_status_w1_w4_closed():
    d = _gs()
    fully_closed = d["global_summary"]["wave_slices_fully_closed"]
    for wave in ["WAVE001", "WAVE002", "WAVE003", "WAVE004"]:
        assert wave in fully_closed


def test_family004_wave005_e_and_f_closed():
    d = _gs()
    closed = d["global_summary"]["wave_slices_closed"]
    assert "WAVE005_E" in closed
    assert "WAVE005_F" in closed


def test_family005_wave005_b_c_d_partially_blocked():
    d = _gs()
    blocked = d["global_summary"]["wave_slices_partially_blocked"]
    assert "WAVE005_B" in blocked
    assert "WAVE005_C" in blocked
    assert "WAVE005_D" in blocked


def test_family006_wave005_a_global_registration_blocked():
    d = _gs()
    grb = d["global_summary"]["wave_slices_global_registration_blocked"]
    assert "WAVE005_A" in grb


def test_family007_wave005_a_status():
    d = _gs()
    assert d["wave_registry"]["WAVE005_A"]["status"] == "CLOSED_LOCALLY_GLOBAL_REGISTRATION_BLOCKED"


def test_family008_wave005_f_status_closed():
    d = _gs()
    assert d["wave_registry"]["WAVE005_F"]["status"] == "AGENTS_FILE_WIRING_WAVE005_F_CLOSED"


def test_family009_wave005_e_status_closed():
    d = _gs()
    assert d["wave_registry"]["WAVE005_E"]["status"] == "AGENTS_FILE_WIRING_WAVE005_E_CLOSED"


def test_family010_family_reconciliation_section_present():
    d = _gs()
    rec = d.get("agents_family_reconciliation", {})
    assert rec, "agents_family_reconciliation must be present"


# ---------------------------------------------------------------------------
# FAMILY-011 to FAMILY-020: Population stability
# ---------------------------------------------------------------------------

def test_family011_wave001_primary_167():
    d = _ai()
    assert d["wave_file_manifests"]["WAVE001"]["files_indexed"] == 167


def test_family012_wave002_primary_167():
    d = _ai()
    assert d["wave_file_manifests"]["WAVE002"]["files_indexed"] == 167


def test_family013_wave003_primary_680():
    d = _ai()
    assert d["wave_file_manifests"]["WAVE003"]["files_indexed"] == 680


def test_family014_wave004_primary_8():
    d = _ai()
    assert d["wave_file_manifests"]["WAVE004"]["files_indexed"] == 8


def test_family015_wave005_a_primary_11():
    d = _gs()
    assert d["wave_registry"]["WAVE005_A"]["functional_files_processed"] == 11


def test_family016_wave005_b_primary_144():
    d = _gs()
    assert d["wave_registry"]["WAVE005_B"]["functional_files_accounted"] == 144


def test_family017_wave005_c_primary_51():
    d = _gs()
    assert d["wave_registry"]["WAVE005_C"]["functional_files_accounted"] == 51


def test_family018_wave005_d_primary_506():
    d = _gs()
    assert d["wave_registry"]["WAVE005_D"]["functional_files_accounted"] == 506


def test_family019_wave005_e_primary_124():
    d = _gs()
    assert d["wave_registry"]["WAVE005_E"]["functional_files_accounted"] == 124


def test_family020_wave005_f_primary_66():
    d = _gs()
    assert d["wave_registry"]["WAVE005_F"]["functional_files_accounted"] == 66


# ---------------------------------------------------------------------------
# FAMILY-021 to FAMILY-030: Brody census complete
# ---------------------------------------------------------------------------

def test_family021_brody_primary_total_902():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["brody_primary_total"] == 902


def test_family022_brody_primary_remaining_0():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["brody_primary_remaining"] == 0


def test_family023_brody_census_complete_true():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["brody_primary_census_complete"] is True


def test_family024_brody_sum_matches_total():
    d = _gs()
    wr = d["wave_registry"]
    w5a = wr["WAVE005_A"]["functional_files_processed"]
    w5b = wr["WAVE005_B"]["functional_files_accounted"]
    w5c = wr["WAVE005_C"]["functional_files_accounted"]
    w5d = wr["WAVE005_D"]["functional_files_accounted"]
    w5e = wr["WAVE005_E"]["functional_files_accounted"]
    w5f = wr["WAVE005_F"]["functional_files_accounted"]
    total = w5a + w5b + w5c + w5d + w5e + w5f
    assert total == 902


def test_family025_wave005_global_reconciliation_brody_902():
    d = _gs()
    rec = d["wave005_global_reconciliation"]
    assert rec["brody_primary_total"] == 902
    assert rec["brody_primary_census_complete"] is True


def test_family026_agents_primary_accounting_complete():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["agents_primary_accounting_complete"] is True


def test_family027_wave005_f_remaining_0():
    d = _gs()
    assert d["wave_registry"]["WAVE005_F"]["remaining_after_wave005f"] == 0


def test_family028_wave005_a_brody_primary_census_in_global():
    d = _gs()
    w5a = d["wave_registry"]["WAVE005_A"]
    assert w5a.get("brody_primary_census") == 902


def test_family029_wave005_d_primary_506_not_507():
    d = _gs()
    w5d = d["wave_registry"]["WAVE005_D"]
    assert w5d["functional_files_accounted"] == 506
    assert w5d.get("all_matrix_rows") == 507
    assert w5d.get("secondary_relation_rows") == 1


def test_family030_family_reconciliation_in_artifact_index():
    d = _ai()
    rec = d.get("agents_family_reconciliation", {})
    assert rec, "agents_family_reconciliation must be present in artifact_index"
    assert rec["agents_primary_accounting_complete"] is True


# ---------------------------------------------------------------------------
# FAMILY-031 to FAMILY-040: Blockers — no double counting
# ---------------------------------------------------------------------------

def test_family031_file_blockers_total_16():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["agents_family_file_blockers"] == 16


def test_family032_global_blockers_total_3():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["agents_family_global_blockers"] == 3


def test_family033_wave005_file_blockers_16():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["wave005_file_blockers"] == 16


def test_family034_wave005_a_global_registration_blockers_1():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["wave005_global_registration_blockers"] == 1


def test_family035_blocker_matrix_present():
    d = _gs()
    bm = d.get("blocker_matrix_v1", {})
    assert bm, "blocker_matrix_v1 must be present"
    assert "blockers" in bm


def test_family036_blocker_matrix_19_entries():
    d = _gs()
    bm = d["blocker_matrix_v1"]
    assert bm["total_blockers"] == 19
    assert len(bm["blockers"]) == 19


def test_family037_blocker_ids_unique():
    d = _gs()
    ids = [b["blocker_id"] for b in d["blocker_matrix_v1"]["blockers"]]
    assert len(ids) == len(set(ids)), "Duplicate blocker_ids detected"


def test_family038_blocker_matrix_file_count_16():
    d = _gs()
    file_b = [b for b in d["blocker_matrix_v1"]["blockers"] if b["is_file_blocker"]]
    assert len(file_b) == 16


def test_family039_blocker_matrix_global_count_3():
    d = _gs()
    global_b = [b for b in d["blocker_matrix_v1"]["blockers"] if b["is_global_blocker"]]
    assert len(global_b) == 3


def test_family040_no_blocker_both_file_and_global():
    d = _gs()
    for b in d["blocker_matrix_v1"]["blockers"]:
        assert not (b["is_file_blocker"] and b["is_global_blocker"]), \
            f"Blocker {b['blocker_id']} cannot be both file and global"


# ---------------------------------------------------------------------------
# FAMILY-041 to FAMILY-050: Blocker separation and categories
# ---------------------------------------------------------------------------

def test_family041_w5b_has_9_blockers():
    d = _gs()
    w5b_b = [b for b in d["blocker_matrix_v1"]["blockers"] if b["wave"] == "WAVE005_B"]
    assert len(w5b_b) == 9


def test_family042_w5c_has_2_blockers():
    d = _gs()
    w5c_b = [b for b in d["blocker_matrix_v1"]["blockers"] if b["wave"] == "WAVE005_C"]
    assert len(w5c_b) == 2


def test_family043_w5d_has_5_blockers():
    d = _gs()
    w5d_b = [b for b in d["blocker_matrix_v1"]["blockers"] if b["wave"] == "WAVE005_D"]
    assert len(w5d_b) == 5


def test_family044_w1_w4_w5a_w5e_w5f_have_0_file_blockers():
    d = _gs()
    for wave in ["WAVE001", "WAVE002", "WAVE003", "WAVE004", "WAVE005_A", "WAVE005_E", "WAVE005_F"]:
        wave_fb = [b for b in d["blocker_matrix_v1"]["blockers"]
                   if b["wave"] == wave and b["is_file_blocker"]]
        assert len(wave_fb) == 0, f"{wave} should have 0 file blockers, got {len(wave_fb)}"


def test_family045_global_registration_blocker_w5a():
    d = _gs()
    grb = [b for b in d["blocker_matrix_v1"]["blockers"]
           if b["blocker_category"] == "GLOBAL_REGISTRATION_BLOCKER"]
    assert len(grb) == 1
    assert grb[0]["wave"] == "WAVE005_A"
    assert grb[0]["blocker_id"] == "BLK-GLOBAL-001"


def test_family046_category_execution_blocker_count_9():
    d = _gs()
    eb = [b for b in d["blocker_matrix_v1"]["blockers"]
          if b["blocker_category"] == "EXECUTION_BLOCKER"]
    assert len(eb) == 9


def test_family047_category_missing_consumer_count_5():
    d = _gs()
    mc = [b for b in d["blocker_matrix_v1"]["blockers"]
          if b["blocker_category"] == "MISSING_CONSUMER_BLOCKER"]
    assert len(mc) == 5


def test_family048_category_relation_blocker_count_2():
    d = _gs()
    rb = [b for b in d["blocker_matrix_v1"]["blockers"]
          if b["blocker_category"] == "RELATION_BLOCKER"]
    assert len(rb) == 2


def test_family049_blocker_by_wave_sums_to_16_file_blockers():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    bw = rec["blocker_count_by_wave"]
    file_total = sum(v for k, v in bw.items())
    assert file_total == 16


def test_family050_w5a_not_counted_as_file_blocker():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    bw = rec["blocker_count_by_wave"]
    assert bw["WAVE005_A"] == 0, "W5A global registration blocker must not be counted as file blocker"


# ---------------------------------------------------------------------------
# FAMILY-051 to FAMILY-060: Populations, family status, MODULES decision
# ---------------------------------------------------------------------------

def test_family051_gross_primary_1924():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["gross_primary_wave_index_entries"] == 1924


def test_family052_unique_primary_1757():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["unique_primary_paths_accounted"] == 1757


def test_family053_overlap_167():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["primary_overlap_count"] == 167


def test_family054_silent_double_count_0():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["silent_double_count"] == 0


def test_family055_campaign_metadata_26_excluded():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["campaign_metadata_total"] == 26
    assert rec["campaign_metadata_included_in_primary"] == 0


def test_family056_family_not_fully_closed():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["agents_family_fully_closed"] is False


def test_family057_global_registration_blocked():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["global_registration_blocked"] is True


def test_family058_global_manifest_not_complete():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["global_manifest_complete"] is False
    assert d["global_manifest_complete"] is False


def test_family059_global_relation_graph_not_complete():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["global_relation_graph_complete"] is False
    assert d["global_relation_graph_complete"] is False


def test_family060_modules_decision_authorized():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["modules_start_decision"] == "AUTHORIZED_WITH_PERSISTED_AGENTS_BLOCKERS"
    assert rec["can_declare_agents_closed"] is False
    assert rec["can_delete_or_ignore_agents_blockers"] is False
    assert rec["can_start_modules_accounting"] is True


# ---------------------------------------------------------------------------
# FAMILY-061 to FAMILY-070: Family status, governance compliance
# ---------------------------------------------------------------------------

def test_family061_family_status_correct():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["family_status"] == "AGENTS_FILE_WIRING_FAMILY_PRIMARY_ACCOUNTING_COMPLETE_GLOBAL_ARTIFACTS_BLOCKED"


def test_family062_family_is_non_sovereign():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["authority"] == "NON_SOVEREIGN"
    assert rec["can_decide"] is False
    assert rec["can_act"] is False
    assert rec["emits_act"] is False
    assert rec["memory_write"] is False


def test_family063_global_state_still_provisional():
    d = _gs()
    assert d.get("global_manifest_complete") is False
    assert d.get("global_relation_graph_complete") is False


def test_family064_artifact_index_still_provisional():
    d = _ai()
    assert d.get("global_manifest_complete") is False
    assert d.get("global_relation_graph_complete") is False
    assert d.get("global_registration_blocked") is True
    assert d.get("artifact_role") == "PROVISIONAL_CAMPAIGN_ARTIFACT_REGISTRY_V1"


def test_family065_artifact_index_family_status():
    d = _ai()
    rec = d.get("agents_family_reconciliation", {})
    assert rec.get("family_status") == "AGENTS_FILE_WIRING_FAMILY_PRIMARY_ACCOUNTING_COMPLETE_GLOBAL_ARTIFACTS_BLOCKED"


def test_family066_wave005_global_status_preserved():
    d = _gs()
    rec = d["wave005_global_reconciliation"]
    assert rec["wave005_global_status"] == "AGENTS_FILE_WIRING_WAVE005_PRIMARY_CENSUS_COMPLETE_GLOBAL_REGISTRATION_BLOCKED"
    assert rec["wave005_fully_closed"] is False


def test_family067_all_blockers_preexisting():
    d = _gs()
    for b in d["blocker_matrix_v1"]["blockers"]:
        assert b["is_preexisting"] is True, f"{b['blocker_id']} should be preexisting"


def test_family068_resolution_not_required_before_modules():
    d = _gs()
    for b in d["blocker_matrix_v1"]["blockers"]:
        assert b["resolution_required_before_modules"] is False, \
            f"{b['blocker_id']} must not block MODULES start"


def test_family069_w5d_python_no_consumer_paths_correct():
    d = _gs()
    w5d = d["wave_registry"]["WAVE005_D"]
    expected = {
        "periphery/brody_memory_readonly/srl_session_registry_layer_readonly/srl_boundary_readonly_v0.py",
        "periphery/brody_memory_readonly/srl_session_registry_layer_readonly/srl_component_matrix_readonly_v0.py",
        "periphery/brody_memory_readonly/srl_session_registry_layer_readonly/srl_taxonomy_readonly_v0.py",
    }
    actual = set(w5d.get("python_no_consumer_paths", []))
    assert actual == expected


def test_family070_w5d_bak_blockers_2():
    d = _gs()
    w5d = d["wave_registry"]["WAVE005_D"]
    assert w5d.get("bak_blockers") == 2
    assert w5d.get("python_no_consumer_blockers") == 3


# ---------------------------------------------------------------------------
# FAMILY-071 to FAMILY-090: Consistency gate — secondary relations + blocker causality
# ---------------------------------------------------------------------------

_PS1 = (
    "periphery/brody_memory_readonly/"
    "brody_agent_readonly_session_test_packet/"
    "run_brody_agent_readonly_session_test_packet_v1.ps1"
)

_EXPECTED_SECONDARY_PATHS = {
    "periphery/agents/brody_memory_agent.py",
    _PS1,
    "periphery/workflow_governance_readonly/integration/brody_workflow_governance_snapshot_adapter.py",
    "periphery/workflow_governance_readonly/operators/brody_workflow_operator_readonly.py",
}


def test_family071_secondary_paths_unique_4():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["secondary_paths_unique"] == 4


def test_family072_secondary_relation_total_final_4():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["secondary_relation_total_final"] == 4


def test_family073_secondary_paths_unique_list_correct():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    actual = set(rec.get("secondary_paths_unique_list", []))
    assert actual == _EXPECTED_SECONDARY_PATHS


def test_family074_secondary_duplicate_ps1_identified():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    dups = rec.get("secondary_duplicate_paths", [])
    assert _PS1 in dups, f"PS1 path must be in secondary_duplicate_paths: {dups}"


def test_family075_frozen_census_contradiction_false():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["frozen_census_contradiction"] is False


def test_family076_secondary_rows_raw_5():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["secondary_rows_raw"] == 5


def test_family077_secondary_rows_raw_breakdown():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    bd = rec.get("secondary_rows_raw_breakdown", {})
    assert bd["W5A_scope_reconciliation"] == 4
    assert bd["W5D_matrix"] == 1


def test_family078_secondary_relations_not_in_primary():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["secondary_relations_included_in_primary"] == 0


def test_family079_w5d_secondary_ps1_not_primary():
    """The PS1 path in W5D matrix is explicitly NOT counted in W5D primary."""
    from pathlib import Path
    import json
    with open(Path(__file__).parents[2] /
              "periphery/agents/brody_memory_interface_and_specs.index.json",
              encoding="utf-8") as f:
        w5d = json.load(f)
    ps1_entries = [e for e in w5d.get("entries", []) if e.get("path") == _PS1]
    assert len(ps1_entries) == 1
    e = ps1_entries[0]
    assert e["counted_in_wave005_d_primary"] is False
    assert e["primary_files_accounted_contribution"] == 0


def test_family080_global_blocker_root_cause_present():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    roots = rec.get("global_blocker_root_causes", [])
    assert "ART193_ART200_ABSENT" in roots


def test_family081_global_blockers_share_root_cause():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec.get("global_blockers_share_root_cause") is True


def test_family082_global_blocker_consequence_chain_present():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    chain = rec.get("global_blocker_consequence_chain", "")
    assert "ART193_ART200" in chain
    assert "BLK-GLOBAL-002" in chain
    assert "BLK-GLOBAL-003" in chain
    assert "BLK-GLOBAL-001" in chain


def test_family083_blk_global_001_is_cascading():
    d = _gs()
    blockers = d["blocker_matrix_v1"]["blockers"]
    g1 = next(b for b in blockers if b["blocker_id"] == "BLK-GLOBAL-001")
    assert g1.get("global_blocker_root_cause") == "ART193_ART200_ABSENT"
    assert g1.get("is_direct_consequence_of_root_cause") is False
    assert "BLK-GLOBAL-002" in (g1.get("is_cascading_consequence_of") or [])


def test_family084_blk_global_002_003_are_direct():
    d = _gs()
    blockers = d["blocker_matrix_v1"]["blockers"]
    for bid in ["BLK-GLOBAL-002", "BLK-GLOBAL-003"]:
        b = next(x for x in blockers if x["blocker_id"] == bid)
        assert b.get("global_blocker_root_cause") == "ART193_ART200_ABSENT"
        assert b.get("is_direct_consequence_of_root_cause") is True


def test_family085_silent_double_count_0():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    assert rec["silent_double_count"] == 0


def test_family086_silent_double_count_proof():
    d = _gs()
    rec = d["agents_family_reconciliation"]
    proof = rec.get("silent_double_count_proof", {})
    assert proof["gross"] == 1924
    assert proof["documented_overlap"] == 167
    assert proof["unique"] == 1757
    assert proof["gross"] - proof["documented_overlap"] == proof["unique"]
    assert proof["equation_holds"] is True
    assert proof["secondary_included_in_primary"] == 0
    assert proof["metadata_included_in_primary"] == 0


def test_family087_missing_consumer_blocker_count_5():
    d = _gs()
    bm = d["blocker_matrix_v1"]
    mc = [b for b in bm["blockers"] if b["blocker_category"] == "MISSING_CONSUMER_BLOCKER"]
    assert len(mc) == 5


def test_family088_missing_consumer_blocker_paths():
    d = _gs()
    bm = d["blocker_matrix_v1"]
    mc_paths = {b["path"] for b in bm["blockers"] if b["blocker_category"] == "MISSING_CONSUMER_BLOCKER"}
    assert "apps/obsidia_api/brody_backend_response_composer.py" in mc_paths
    assert "connectors/brody_memory_readonly_flow.py" in mc_paths
    assert "periphery/brody_memory_readonly/srl_session_registry_layer_readonly/srl_boundary_readonly_v0.py" in mc_paths
    assert "periphery/brody_memory_readonly/srl_session_registry_layer_readonly/srl_component_matrix_readonly_v0.py" in mc_paths
    assert "periphery/brody_memory_readonly/srl_session_registry_layer_readonly/srl_taxonomy_readonly_v0.py" in mc_paths


def test_family089_duplicate_blockers_counted_0():
    d = _gs()
    ids = [b["blocker_id"] for b in d["blocker_matrix_v1"]["blockers"]]
    assert len(ids) == len(set(ids))


def test_family090_artifact_index_consistency_fields():
    d = _ai()
    rec = d.get("agents_family_reconciliation", {})
    assert rec["secondary_paths_unique"] == 4
    assert rec["secondary_relation_total_final"] == 4
    assert rec["frozen_census_contradiction"] is False
    assert rec["global_blocker_root_causes"] == ["ART193_ART200_ABSENT"]
    assert rec["global_blockers_share_root_cause"] is True
    assert rec["silent_double_count"] == 0
