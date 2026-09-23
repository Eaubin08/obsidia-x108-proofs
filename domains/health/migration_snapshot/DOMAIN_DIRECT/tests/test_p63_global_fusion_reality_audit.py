"""Tests P63 — Global Fusion Reality Audit verification."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
P63_JSON = REPO_ROOT / "docs" / "core_import" / "P63_GLOBAL_FUSION_REALITY_AUDIT.json"

REQUIRED_SURFACES = {
    "agents",
    "engine_runtime",
    "sigma",
    "api_routes",
    "canon_wording",
    "presentation_support",
    "gps_defense_aviation",
    "graphiti_brody_memory",
}


def load_p63():
    with open(P63_JSON) as f:
        return json.load(f)


# ── Test 1 ─────────────────────────────────────────────────────────────────────
def test_p63_json_exists():
    assert P63_JSON.exists(), f"P63 JSON absent : {P63_JSON}"


# ── Test 2 ─────────────────────────────────────────────────────────────────────
def test_status():
    data = load_p63()
    assert data["status"] == "P63_GLOBAL_FUSION_REALITY_AUDIT_READY"


# ── Test 3 ─────────────────────────────────────────────────────────────────────
def test_mode():
    data = load_p63()
    assert data["mode"] == "AUDIT_ONLY"


# ── Test 4 ─────────────────────────────────────────────────────────────────────
def test_source_patch_applied_false():
    data = load_p63()
    assert data["source_patch_applied"] is False


# ── Test 5 ─────────────────────────────────────────────────────────────────────
def test_files_imported_count_zero():
    data = load_p63()
    assert data["files_imported_count"] == 0


# ── Test 6 ─────────────────────────────────────────────────────────────────────
def test_surfaces_exist():
    data = load_p63()
    assert "surfaces" in data, "champ 'surfaces' absent du JSON"
    assert isinstance(data["surfaces"], dict)


# ── Test 7 ─────────────────────────────────────────────────────────────────────
def test_surface_agents():
    data = load_p63()
    assert "agents" in data["surfaces"], "surface 'agents' absente"
    s = data["surfaces"]["agents"]
    assert "already_in_place" in s
    assert "blocked" in s
    assert len(s["already_in_place"]) > 0, "agents.already_in_place vide"


# ── Test 8 ─────────────────────────────────────────────────────────────────────
def test_surface_engine_runtime():
    data = load_p63()
    assert "engine_runtime" in data["surfaces"], "surface 'engine_runtime' absente"
    s = data["surfaces"]["engine_runtime"]
    assert "already_in_place" in s
    assert "dry_run_existing" in s
    assert len(s["dry_run_existing"]) > 0, "engine_runtime.dry_run_existing vide"


# ── Test 9 ─────────────────────────────────────────────────────────────────────
def test_surface_sigma():
    data = load_p63()
    assert "sigma" in data["surfaces"], "surface 'sigma' absente"
    s = data["surfaces"]["sigma"]
    assert "already_in_place" in s
    assert "protected_files" in s
    assert len(s["already_in_place"]) >= 10, "sigma.already_in_place insuffisant"


# ── Test 10 ────────────────────────────────────────────────────────────────────
def test_surface_api_routes():
    data = load_p63()
    assert "api_routes" in data["surfaces"], "surface 'api_routes' absente"
    s = data["surfaces"]["api_routes"]
    assert "already_in_place" in s
    assert "readonly_routes" in s
    assert len(s["already_in_place"]) >= 10, "api_routes.already_in_place insuffisant"


# ── Test 11 ────────────────────────────────────────────────────────────────────
def test_surface_canon_wording():
    data = load_p63()
    assert "canon_wording" in data["surfaces"], "surface 'canon_wording' absente"
    s = data["surfaces"]["canon_wording"]
    assert "justified_strong_terms" in s
    assert len(s["justified_strong_terms"]) > 0


# ── Test 12 ────────────────────────────────────────────────────────────────────
def test_surface_presentation_support():
    data = load_p63()
    assert "presentation_support" in data["surfaces"], "surface 'presentation_support' absente"
    s = data["surfaces"]["presentation_support"]
    assert "technical_docs" in s
    assert "public_narrative_docs" in s


# ── Test 13 ────────────────────────────────────────────────────────────────────
def test_surface_gps_defense_aviation():
    data = load_p63()
    assert "gps_defense_aviation" in data["surfaces"], "surface 'gps_defense_aviation' absente"
    s = data["surfaces"]["gps_defense_aviation"]
    assert "already_in_place" in s
    assert "pipeline_connected" in s
    assert "tests_existing" in s
    assert len(s["already_in_place"]) > 0


# ── Test 14 ────────────────────────────────────────────────────────────────────
def test_surface_graphiti_brody_memory():
    data = load_p63()
    assert "graphiti_brody_memory" in data["surfaces"], "surface 'graphiti_brody_memory' absente"
    s = data["surfaces"]["graphiti_brody_memory"]
    assert "isolated" in s
    assert "must_exclude" in s
    assert len(s["isolated"]) > 0


# ── Test 15 ────────────────────────────────────────────────────────────────────
def test_fusion_plan_non_empty():
    data = load_p63()
    assert "fusion_plan" in data
    assert isinstance(data["fusion_plan"], list)
    assert len(data["fusion_plan"]) >= 8, "fusion_plan doit contenir P64-P72"
    paliers = [p["palier"] for p in data["fusion_plan"]]
    for expected in ["P64", "P65", "P66", "P67", "P68", "P69", "P70", "P71", "P72"]:
        assert expected in paliers, f"palier {expected} absent du fusion_plan"


# ── Test 16 ────────────────────────────────────────────────────────────────────
def test_recommended_next_paliers_non_empty():
    data = load_p63()
    assert "recommended_next_paliers" in data
    assert len(data["recommended_next_paliers"]) > 0


# ── Test 17 ────────────────────────────────────────────────────────────────────
def test_risk_matrix_non_empty():
    data = load_p63()
    assert "risk_matrix" in data
    assert isinstance(data["risk_matrix"], list)
    assert len(data["risk_matrix"]) >= 4, "risk_matrix insuffisante"
    for entry in data["risk_matrix"]:
        assert "surface" in entry
        assert "risque" in entry
        assert "decision" in entry


# ── Test 18 ────────────────────────────────────────────────────────────────────
def test_runtime_modified_false():
    data = load_p63()
    assert data.get("runtime_modified") is False


# ── Test 19 ────────────────────────────────────────────────────────────────────
def test_sigma_modified_false():
    data = load_p63()
    assert data.get("sigma_modified") is False


# ── Test 20 ────────────────────────────────────────────────────────────────────
def test_routes_modified_false():
    data = load_p63()
    assert data.get("routes_modified") is False


# ── Test 21 ────────────────────────────────────────────────────────────────────
def test_act_enabled_false():
    data = load_p63()
    assert data.get("act_enabled") is False


# ── Test 22 ────────────────────────────────────────────────────────────────────
def test_memory_write_enabled_false():
    data = load_p63()
    assert data.get("memory_write_enabled") is False


# ── Test 23 ────────────────────────────────────────────────────────────────────
def test_graphiti_write_enabled_false():
    data = load_p63()
    assert data.get("graphiti_write_enabled") is False


# ── Test 24 ────────────────────────────────────────────────────────────────────
def test_kernel_mutation_enabled_false():
    data = load_p63()
    assert data.get("kernel_mutation_enabled") is False


# ── Test 25 ────────────────────────────────────────────────────────────────────
def test_p56e_still_passes():
    p56e = REPO_ROOT / "docs" / "core_import" / "P56E_POST_PATCH_METRIC_REAUDIT.json"
    assert p56e.exists(), "P56E JSON absent"
    data = json.load(open(p56e))
    verdict = data.get("final_verdict", data.get("status", ""))
    assert "PASS" in verdict or "READY" in verdict, f"P56E non PASS : {verdict}"


# ── Test 26 ────────────────────────────────────────────────────────────────────
def test_p57_still_passes():
    p57 = REPO_ROOT / "docs" / "core_import" / "P57_CORE_MACHINERY_INVENTORY.json"
    assert p57.exists(), "P57 JSON absent"
    data = json.load(open(p57))
    assert isinstance(data, list) and len(data) > 0, "P57 inventory vide"


# ── Test 27 ────────────────────────────────────────────────────────────────────
def test_p58_still_passes():
    p58 = REPO_ROOT / "docs" / "core_import" / "P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.json"
    assert p58.exists(), "P58 JSON absent"
    data = json.load(open(p58))
    status = data.get("status", "")
    assert "READY" in status or "PASS" in status or "TRIAGE" in status


# ── Test 28 ────────────────────────────────────────────────────────────────────
def test_p59_still_passes():
    p59 = REPO_ROOT / "docs" / "core_import" / "P59_SAFE_BATCH_1_IMPORT.json"
    assert p59.exists(), "P59 JSON absent"
    assert "READY" in json.load(open(p59)).get("status", "")


# ── Test 29 ────────────────────────────────────────────────────────────────────
def test_p60_still_passes():
    p60 = REPO_ROOT / "docs" / "core_import" / "P60_TEST_BATCH_2_IMPORT.json"
    assert p60.exists(), "P60 JSON absent"
    assert "READY" in json.load(open(p60)).get("status", "")


# ── Test 30 ────────────────────────────────────────────────────────────────────
def test_p61_still_passes():
    p61 = REPO_ROOT / "docs" / "core_import" / "P61_BUS_ADAPTER_BATCH.json"
    assert p61.exists(), "P61 JSON absent"
    assert "READY" in json.load(open(p61)).get("status", "")


# ── Test 31 ────────────────────────────────────────────────────────────────────
def test_p62_still_passes():
    p62 = REPO_ROOT / "docs" / "core_import" / "P62_MANUAL_REVIEW_DEFERRED.json"
    assert p62.exists(), "P62 JSON absent"
    assert "CLASSIFIED" in json.load(open(p62)).get("status", "")


# ── Test 32 ────────────────────────────────────────────────────────────────────
def test_verify_all_still_passes():
    verify_all = REPO_ROOT / "proofs" / "verify_all.py"
    if not verify_all.exists():
        pytest.skip("proofs/verify_all.py absent")
    result = subprocess.run(
        [sys.executable, str(verify_all)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"proofs/verify_all.py FAIL :\n{result.stdout}\n{result.stderr}"
    )


# ── Test 33 ────────────────────────────────────────────────────────────────────
def test_forbidden_content_still_passes():
    check = REPO_ROOT / "scripts" / "check_forbidden_content.py"
    if not check.exists():
        pytest.skip("check_forbidden_content.py absent")
    result = subprocess.run(
        [sys.executable, str(check)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"check_forbidden_content FAIL :\n{result.stdout}\n{result.stderr}"
    )
