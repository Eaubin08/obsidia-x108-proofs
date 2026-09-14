"""
MODULES_FILE_WIRING — Opening gate tests (MWC-001 to MWC-060).

Validates the MODULES_FILE_WIRING campaign opening state artifacts:
  - periphery/agents/modules_file_wiring_global_state.json
  - periphery/agents/modules_file_wiring_artifact_index.json
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).parent.parent.parent
GLOBAL_STATE_PATH = ROOT / "periphery/agents/modules_file_wiring_global_state.json"
ARTIFACT_INDEX_PATH = ROOT / "periphery/agents/modules_file_wiring_artifact_index.json"

EXPECTED_SUBDIRS = [
    "00_INDEX", "00_SOURCES", "01_REGISTRES_JSON",
    "02_BLOCS_17", "03_PEPITES_161", "04_SPECS_40",
    "05_MODULES_A1_A24", "06_GARDIENS_DE_FOND_T1_T12", "06_TESTS_T1_T12",
    "07_AGENTS_ET_ROLES", "08_PREUVES_LEAN_TLA", "09_TESTS_PY_TS_CHAOS_LOAD",
    "10_AUDITS_A_F", "11_CONTRATS_OS3_OS4_ADELE", "12_EXTENSIONS_R_D",
    "13_ENGINE_GATES", "14_REGROUPEMENTS_COHERENCE", "root_init_py",
]

EXPECTED_WAVE_IDS = [
    "MODULES_WAVE_A", "MODULES_WAVE_B", "MODULES_WAVE_C", "MODULES_WAVE_D",
    "MODULES_WAVE_E", "MODULES_WAVE_F", "MODULES_WAVE_G", "MODULES_WAVE_H",
    "MODULES_WAVE_I", "MODULES_WAVE_J",
]

EXPECTED_AGENTS_BLOCKER_IDS = [
    "BLK-W5B-001", "BLK-W5B-002", "BLK-W5B-003", "BLK-W5B-004",
    "BLK-W5B-005", "BLK-W5B-006", "BLK-W5B-007", "BLK-W5B-008",
    "BLK-W5B-009", "BLK-W5C-001", "BLK-W5C-002",
    "BLK-W5D-001", "BLK-W5D-002", "BLK-W5D-003", "BLK-W5D-004", "BLK-W5D-005",
    "BLK-GLOBAL-001", "BLK-GLOBAL-002", "BLK-GLOBAL-003",
]


def _gs():
    with open(GLOBAL_STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _ai():
    with open(ARTIFACT_INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)


# ── File existence ─────────────────────────────────────────────────────────────

def test_mwc001_global_state_file_exists():
    assert GLOBAL_STATE_PATH.exists()


def test_mwc002_artifact_index_file_exists():
    assert ARTIFACT_INDEX_PATH.exists()


# ── Global state — campaign identity ──────────────────────────────────────────

def test_mwc003_campaign_id():
    assert _gs()["campaign_id"] == "MODULES_FILE_WIRING"


def test_mwc004_campaign_version():
    assert _gs()["campaign_version"] == "V1"


def test_mwc005_campaign_status_opening():
    assert _gs()["campaign_status"] == "OPENING"


def test_mwc006_authority_non_sovereign():
    assert _gs()["authority"] == "NON_SOVEREIGN"


def test_mwc007_can_decide_false():
    assert _gs()["can_decide"] is False


def test_mwc008_can_act_false():
    assert _gs()["can_act"] is False


def test_mwc009_emits_act_false():
    assert _gs()["emits_act"] is False


def test_mwc010_memory_write_false():
    assert _gs()["memory_write"] is False


# ── Global state — primary scope ──────────────────────────────────────────────

def test_mwc011_scope_root_directory():
    assert _gs()["primary_scope"]["root_directory"] == "periphery/OBSIDIA_V4_STRUCTURED_FULL"


def test_mwc012_scope_total_tracked_in_root():
    assert _gs()["primary_scope"]["total_tracked_in_root"] == 826


def test_mwc013_scope_already_indexed_in_agents():
    assert _gs()["primary_scope"]["already_indexed_in_agents_campaign"] == 121


def test_mwc014_scope_new_scope_files():
    assert _gs()["primary_scope"]["new_scope_files"] == 705


def test_mwc015_scope_freeze_locked():
    assert _gs()["primary_scope"]["scope_freeze"] == "OPENING_CENSUS_LOCKED"


def test_mwc016_scope_consistency():
    s = _gs()["primary_scope"]
    assert s["total_tracked_in_root"] - s["already_indexed_in_agents_campaign"] == s["new_scope_files"]


# ── Global state — subdir census ──────────────────────────────────────────────

def test_mwc017_subdir_census_total():
    assert _gs()["subdir_census"]["total"] == 705


def test_mwc018_subdir_census_all_keys_present():
    census = _gs()["subdir_census"]
    for d in EXPECTED_SUBDIRS:
        assert d in census, f"Missing subdir key: {d}"


def test_mwc019_subdir_00_index():
    assert _gs()["subdir_census"]["00_INDEX"] == 5


def test_mwc020_subdir_00_sources():
    assert _gs()["subdir_census"]["00_SOURCES"] == 11


def test_mwc021_subdir_01_registres():
    assert _gs()["subdir_census"]["01_REGISTRES_JSON"] == 10


def test_mwc022_subdir_02_blocs():
    assert _gs()["subdir_census"]["02_BLOCS_17"] == 17


def test_mwc023_subdir_03_pepites():
    assert _gs()["subdir_census"]["03_PEPITES_161"] == 159


def test_mwc024_subdir_04_specs():
    assert _gs()["subdir_census"]["04_SPECS_40"] == 41


def test_mwc025_subdir_05_modules():
    assert _gs()["subdir_census"]["05_MODULES_A1_A24"] == 25


def test_mwc026_subdir_06_gardiens():
    assert _gs()["subdir_census"]["06_GARDIENS_DE_FOND_T1_T12"] == 13


def test_mwc027_subdir_06_tests():
    assert _gs()["subdir_census"]["06_TESTS_T1_T12"] == 13


def test_mwc028_subdir_07_agents():
    assert _gs()["subdir_census"]["07_AGENTS_ET_ROLES"] == 4


def test_mwc029_subdir_08_preuves():
    assert _gs()["subdir_census"]["08_PREUVES_LEAN_TLA"] == 13


def test_mwc030_subdir_09_tests_py():
    assert _gs()["subdir_census"]["09_TESTS_PY_TS_CHAOS_LOAD"] == 9


def test_mwc031_subdir_10_audits():
    assert _gs()["subdir_census"]["10_AUDITS_A_F"] == 7


def test_mwc032_subdir_11_contrats():
    assert _gs()["subdir_census"]["11_CONTRATS_OS3_OS4_ADELE"] == 3


def test_mwc033_subdir_12_extensions():
    assert _gs()["subdir_census"]["12_EXTENSIONS_R_D"] == 19


def test_mwc034_subdir_13_gates():
    assert _gs()["subdir_census"]["13_ENGINE_GATES"] == 3


def test_mwc035_subdir_14_regroupements():
    assert _gs()["subdir_census"]["14_REGROUPEMENTS_COHERENCE"] == 352


def test_mwc036_subdir_root_init():
    assert _gs()["subdir_census"]["root_init_py"] == 1


def test_mwc037_subdir_sum_equals_total():
    census = _gs()["subdir_census"]
    total = census["total"]
    s = sum(v for k, v in census.items() if k != "total")
    assert s == total


# ── Global state — extension census ──────────────────────────────────────────

def test_mwc038_extension_md_count():
    assert _gs()["extension_census"][".md"] == 648


def test_mwc039_extension_py_count():
    assert _gs()["extension_census"][".py"] == 39


def test_mwc040_extension_json_count():
    assert _gs()["extension_census"][".json"] == 9


def test_mwc041_extension_lean_count():
    assert _gs()["extension_census"][".lean"] == 6


def test_mwc042_extension_total():
    assert _gs()["extension_census"]["total"] == 705


def test_mwc043_extension_sum_equals_total():
    ext = _gs()["extension_census"]
    total = ext["total"]
    s = sum(v for k, v in ext.items() if k != "total")
    assert s == total


# ── Global state — wave structure ────────────────────────────────────────────

def test_mwc044_wave_total_proposed():
    assert _gs()["wave_total_proposed"] == 10


def test_mwc045_wave_files_proposed_total():
    assert _gs()["wave_files_proposed_total"] == 705


def test_mwc046_proposed_wave_ids():
    waves = _gs()["proposed_wave_structure"]
    ids = [w["wave_id"] for w in waves]
    for wid in EXPECTED_WAVE_IDS:
        assert wid in ids, f"Missing wave_id: {wid}"


def test_mwc047_wave_files_sum():
    waves = _gs()["proposed_wave_structure"]
    total = sum(w["proposed_file_count"] for w in waves)
    assert total == 705


def test_mwc048_all_waves_not_started():
    waves = _gs()["proposed_wave_structure"]
    for w in waves:
        assert w["status"] == "NOT_STARTED"


def test_mwc049_waves_not_started_list():
    gs = _gs()
    assert set(gs["waves_not_started"]) == set(EXPECTED_WAVE_IDS)


def test_mwc050_waves_closed_empty():
    assert _gs()["waves_closed"] == []


def test_mwc051_waves_in_progress_empty():
    assert _gs()["waves_in_progress"] == []


def test_mwc052_files_indexed_total_zero():
    assert _gs()["files_indexed_total"] == 0


# ── Global state — persisted AGENTS context ───────────────────────────────────

def test_mwc053_agents_blockers_total_19():
    ag = _gs()["persisted_agents_context"]
    assert ag["agents_blockers_total"] == 19


def test_mwc054_agents_file_blockers_16():
    ag = _gs()["persisted_agents_context"]
    assert ag["agents_file_blockers"] == 16


def test_mwc055_agents_global_blockers_3():
    ag = _gs()["persisted_agents_context"]
    assert ag["agents_global_blockers"] == 3


def test_mwc056_agents_global_root_causes_1():
    ag = _gs()["persisted_agents_context"]
    assert ag["agents_global_root_causes"] == 1


def test_mwc057_agents_blocker_ids_count():
    ag = _gs()["persisted_agents_context"]
    assert len(ag["agents_blocker_ids"]) == 19


def test_mwc058_agents_blocker_ids_exact():
    ag = _gs()["persisted_agents_context"]
    assert set(ag["agents_blocker_ids"]) == set(EXPECTED_AGENTS_BLOCKER_IDS)


def test_mwc059_agents_start_decision():
    ag = _gs()["persisted_agents_context"]
    assert ag["agents_start_decision"] == "AUTHORIZED_WITH_PERSISTED_AGENTS_BLOCKERS"


def test_mwc060_agents_family_status():
    ag = _gs()["persisted_agents_context"]
    assert ag["agents_family_status"] == (
        "AGENTS_FILE_WIRING_FAMILY_PRIMARY_ACCOUNTING_COMPLETE_GLOBAL_ARTIFACTS_BLOCKED"
    )


# ── Global state — MODULES family status ─────────────────────────────────────

def test_mwc061_modules_family_status():
    assert _gs()["modules_family_status"] == "MODULES_FILE_WIRING_FAMILY_OPENING"


def test_mwc062_modules_start_decision():
    assert _gs()["modules_start_decision"] == "MODULES_WAVE_A_AUTHORIZED_PENDING_WAVE_START"


# ── Artifact index — identity ─────────────────────────────────────────────────

def test_mwc063_artifact_id():
    assert _ai()["artifact_id"] == "MODULES_FILE_WIRING_ARTIFACT_INDEX_V1"


def test_mwc064_artifact_campaign():
    assert _ai()["campaign"] == "MODULES_FILE_WIRING"


def test_mwc065_artifact_authority():
    assert _ai()["authority"] == "NON_SOVEREIGN"


def test_mwc066_artifact_can_decide_false():
    assert _ai()["can_decide"] is False


def test_mwc067_artifact_global_manifest_not_complete():
    assert _ai()["global_manifest_complete"] is False


def test_mwc068_artifact_global_registration_not_blocked():
    assert _ai()["global_registration_blocked"] is False


# ── Artifact index — scope ───────────────────────────────────────────────────

def test_mwc069_artifact_scope_new_files():
    assert _ai()["campaign_scope"]["total_new_scope_files"] == 705


def test_mwc070_artifact_scope_files_indexed_zero():
    assert _ai()["campaign_scope"]["files_indexed"] == 0


def test_mwc071_artifact_scope_files_remaining():
    assert _ai()["campaign_scope"]["files_remaining"] == 705


# ── Artifact index — wave status registry ────────────────────────────────────

def test_mwc072_artifact_wave_registry_all_present():
    reg = _ai()["wave_status_registry"]
    for wid in EXPECTED_WAVE_IDS:
        assert wid in reg, f"Missing wave in registry: {wid}"


def test_mwc073_artifact_wave_registry_all_not_started():
    reg = _ai()["wave_status_registry"]
    for wid, info in reg.items():
        assert info["status"] == "NOT_STARTED", f"Wave {wid} not in NOT_STARTED"


def test_mwc074_artifact_wave_registry_no_indexed_files():
    reg = _ai()["wave_status_registry"]
    for wid, info in reg.items():
        assert info["indexed_file_count"] == 0


def test_mwc075_artifact_wave_registry_no_blockers():
    reg = _ai()["wave_status_registry"]
    for wid, info in reg.items():
        assert info["blockers"] == [], f"Wave {wid} has unexpected blockers"


# ── Artifact index — persisted AGENTS context ────────────────────────────────

def test_mwc076_artifact_agents_blockers_total():
    assert _ai()["persisted_agents_context"]["agents_blockers_total"] == 19


def test_mwc077_artifact_agents_file_blockers():
    assert _ai()["persisted_agents_context"]["agents_file_blockers"] == 16


def test_mwc078_artifact_agents_global_blockers():
    assert _ai()["persisted_agents_context"]["agents_global_blockers"] == 3


def test_mwc079_artifact_modules_family_status():
    assert _ai()["modules_family_status"] == "MODULES_FILE_WIRING_FAMILY_OPENING"


# ── Cross-artifact consistency ────────────────────────────────────────────────

def test_mwc080_cross_modules_family_status_consistent():
    assert _gs()["modules_family_status"] == _ai()["modules_family_status"]


def test_mwc081_cross_agents_blockers_consistent():
    gs_total = _gs()["persisted_agents_context"]["agents_blockers_total"]
    ai_total = _ai()["persisted_agents_context"]["agents_blockers_total"]
    assert gs_total == ai_total == 19


def test_mwc082_cross_scope_new_files_consistent():
    assert _gs()["primary_scope"]["new_scope_files"] == _ai()["campaign_scope"]["total_new_scope_files"]


def test_mwc083_wave_a_proposed_count():
    waves = _gs()["proposed_wave_structure"]
    wa = next(w for w in waves if w["wave_id"] == "MODULES_WAVE_A")
    assert wa["proposed_file_count"] == 26


def test_mwc084_wave_i_proposed_count():
    waves = _gs()["proposed_wave_structure"]
    wi = next(w for w in waves if w["wave_id"] == "MODULES_WAVE_I")
    assert wi["proposed_file_count"] == 352


def test_mwc085_wave_i_is_largest():
    waves = _gs()["proposed_wave_structure"]
    counts = {w["wave_id"]: w["proposed_file_count"] for w in waves}
    assert counts["MODULES_WAVE_I"] == max(counts.values())
