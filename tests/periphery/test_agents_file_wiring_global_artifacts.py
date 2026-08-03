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
    assert d["artifact_role"] == "GLOBAL_CAMPAIGN_STATE"


def test_ga_003_global_state_non_sovereign():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    assert d["can_decide"] is False
    assert d["can_act"] is False
    assert d["emits_act"] is False
    assert d["memory_write"] is False


def test_ga_004_global_state_registers_wave005a():
    d = _load("periphery/agents/agents_file_wiring_global_state.json")
    w5a = d["wave_registry"]["WAVE005_A"]
    assert w5a["status"] == "CLOSED_NEXT_SUBWAVE_REQUIRED"
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
    assert d["artifact_role"] == "GLOBAL_ARTIFACT_INDEX"
    assert "GLOBAL_FILE_MANIFEST" in d.get("secondary_roles", [])
    assert "GLOBAL_RELATION_GRAPH" in d.get("secondary_roles", [])


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
    assert w5a["status"] == "CLOSED_NEXT_SUBWAVE_REQUIRED"


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


def test_ga_042_local_state_wave005a_registration_complete():
    d = _load("periphery/agents/wave005_campaign_state.json")
    assert d.get("WAVE005_A_GLOBAL_REGISTRATION_COMPLETE") is True


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
