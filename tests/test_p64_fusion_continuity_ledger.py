"""Tests P64 — Fusion Continuity Ledger verification."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
P64_JSON = REPO_ROOT / "docs" / "core_import" / "P64_FUSION_CONTINUITY_LEDGER.json"

REQUIRED_SURFACES = {
    "metrics",
    "sigma",
    "agents",
    "engine_runtime",
    "runtime_wiring",
    "api_routes",
    "bus",
    "gps_defense_aviation",
    "graphiti_brody_memory",
    "canon_wording",
    "presentation_support",
}


def load_p64():
    with open(P64_JSON) as f:
        return json.load(f)


# ── Test 1 ─────────────────────────────────────────────────────────────────────
def test_p64_json_exists():
    assert P64_JSON.exists(), f"P64 JSON absent : {P64_JSON}"


# ── Test 2 ─────────────────────────────────────────────────────────────────────
def test_status():
    data = load_p64()
    assert data["status"] == "P64_FUSION_CONTINUITY_LEDGER_READY"


# ── Test 3 ─────────────────────────────────────────────────────────────────────
def test_mode():
    data = load_p64()
    assert data["mode"] == "LEDGER_ONLY"


# ── Test 4 ─────────────────────────────────────────────────────────────────────
def test_source_patch_applied_false():
    data = load_p64()
    assert data["source_patch_applied"] is False


# ── Test 5 ─────────────────────────────────────────────────────────────────────
def test_files_imported_count_zero():
    data = load_p64()
    assert data["files_imported_count"] == 0


# ── Test 6 ─────────────────────────────────────────────────────────────────────
def test_core_role():
    data = load_p64()
    assert data["core_role"] == "RIGOR_METRICS_AND_RAW_MATERIAL"


# ── Test 7 ─────────────────────────────────────────────────────────────────────
def test_proof_role():
    data = load_p64()
    assert data["proof_role"] == "ADVANCED_GOVERNED_RUNTIME_AND_SIGMA"


# ── Test 8 ─────────────────────────────────────────────────────────────────────
def test_validated_decisions_non_empty():
    data = load_p64()
    assert "validated_decisions" in data
    assert isinstance(data["validated_decisions"], list)
    assert len(data["validated_decisions"]) >= 8, (
        "validated_decisions doit couvrir P56 à P63"
    )
    paliers = [d.get("palier", "") for d in data["validated_decisions"]]
    for expected in ["P56", "P57", "P58", "P59", "P60", "P61", "P62", "P63"]:
        assert expected in paliers, f"Palier {expected} absent de validated_decisions"


# ── Test 9 ─────────────────────────────────────────────────────────────────────
def test_surface_ledger_metrics():
    data = load_p64()
    assert "surface_ledger" in data
    assert "metrics" in data["surface_ledger"], "surface_ledger.metrics absent"
    m = data["surface_ledger"]["metrics"]
    assert "decision" in m
    assert "KEEP_PROOF" in m["decision"] or "KEEP" in m["decision"]


# ── Test 10 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_sigma():
    data = load_p64()
    assert "sigma" in data["surface_ledger"], "surface_ledger.sigma absent"
    s = data["surface_ledger"]["sigma"]
    assert "KEEP_PROOF" in s["decision"] or "KEEP" in s["decision"]
    assert "P56B" in s["proof_contient_deja"] or "P56" in s["proof_contient_deja"]


# ── Test 11 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_agents():
    data = load_p64()
    assert "agents" in data["surface_ledger"], "surface_ledger.agents absent"
    a = data["surface_ledger"]["agents"]
    assert "decision" in a
    assert "prochain_geste" in a


# ── Test 12 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_engine_runtime():
    data = load_p64()
    assert "engine_runtime" in data["surface_ledger"], "surface_ledger.engine_runtime absent"
    e = data["surface_ledger"]["engine_runtime"]
    assert "BLOCK" in e["decision"], "engine_runtime doit avoir une décision BLOCK"
    assert "prochain_geste" in e


# ── Test 13 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_runtime_wiring():
    data = load_p64()
    assert "runtime_wiring" in data["surface_ledger"], "surface_ledger.runtime_wiring absent"
    r = data["surface_ledger"]["runtime_wiring"]
    assert "KEEP_PROOF" in r["decision"] or "KEEP" in r["decision"]


# ── Test 14 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_api_routes():
    data = load_p64()
    assert "api_routes" in data["surface_ledger"], "surface_ledger.api_routes absent"
    a = data["surface_ledger"]["api_routes"]
    assert "decision" in a
    assert "prochain_geste" in a


# ── Test 15 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_bus():
    data = load_p64()
    assert "bus" in data["surface_ledger"], "surface_ledger.bus absent"
    b = data["surface_ledger"]["bus"]
    assert "P65" in b["prochain_geste"] or "registry" in b["prochain_geste"].lower()


# ── Test 16 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_gps_defense_aviation():
    data = load_p64()
    assert "gps_defense_aviation" in data["surface_ledger"], "surface_ledger.gps_defense_aviation absent"
    g = data["surface_ledger"]["gps_defense_aviation"]
    assert "decision" in g
    assert "prochain_geste" in g


# ── Test 17 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_graphiti_brody_memory():
    data = load_p64()
    assert "graphiti_brody_memory" in data["surface_ledger"], "surface_ledger.graphiti_brody_memory absent"
    g = data["surface_ledger"]["graphiti_brody_memory"]
    assert "KEEP_PROOF" in g["decision"] or "KEEP" in g["decision"]
    assert "False" in g["proof_contient_deja"] or "false" in g["proof_contient_deja"].lower() or "write=False" in g["proof_contient_deja"]


# ── Test 18 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_canon_wording():
    data = load_p64()
    assert "canon_wording" in data["surface_ledger"], "surface_ledger.canon_wording absent"
    c = data["surface_ledger"]["canon_wording"]
    assert "PATCH_TARGETED" in c["decision"] or "PATCH" in c["decision"]


# ── Test 19 ────────────────────────────────────────────────────────────────────
def test_surface_ledger_presentation_support():
    data = load_p64()
    assert "presentation_support" in data["surface_ledger"], "surface_ledger.presentation_support absent"
    p = data["surface_ledger"]["presentation_support"]
    assert "SEPARATE" in p["decision"] or "P71" in p["prochain_geste"]


# ── Test 20 ────────────────────────────────────────────────────────────────────
def test_do_not_forget_non_empty():
    data = load_p64()
    assert "do_not_forget" in data
    assert isinstance(data["do_not_forget"], list)
    assert len(data["do_not_forget"]) >= 10, "do_not_forget doit contenir au moins 10 règles"
    joined = " ".join(data["do_not_forget"])
    assert "sigma" in joined.lower(), "do_not_forget doit mentionner sigma"
    assert "registry" in joined.lower() or "P61" in joined, "do_not_forget doit mentionner registry/P61"
    assert "gamma" in joined.lower() or "0.5" in joined, "do_not_forget doit mentionner le gamma"


# ── Test 21 ────────────────────────────────────────────────────────────────────
def test_next_paliers_non_empty():
    data = load_p64()
    assert "next_paliers" in data
    assert isinstance(data["next_paliers"], list)
    assert len(data["next_paliers"]) >= 8
    paliers = [p["palier"] for p in data["next_paliers"]]
    for expected in ["P65", "P66", "P67", "P68", "P69", "P70", "P71", "P72"]:
        assert expected in paliers, f"Palier {expected} absent de next_paliers"


# ── Test 22 ────────────────────────────────────────────────────────────────────
def test_runtime_modified_false():
    data = load_p64()
    assert data.get("runtime_modified") is False


# ── Test 23 ────────────────────────────────────────────────────────────────────
def test_sigma_modified_false():
    data = load_p64()
    assert data.get("sigma_modified") is False


# ── Test 24 ────────────────────────────────────────────────────────────────────
def test_routes_modified_false():
    data = load_p64()
    assert data.get("routes_modified") is False


# ── Test 25 ────────────────────────────────────────────────────────────────────
def test_act_enabled_false():
    data = load_p64()
    assert data.get("act_enabled") is False


# ── Test 26 ────────────────────────────────────────────────────────────────────
def test_memory_write_enabled_false():
    data = load_p64()
    assert data.get("memory_write_enabled") is False


# ── Test 27 ────────────────────────────────────────────────────────────────────
def test_graphiti_write_enabled_false():
    data = load_p64()
    assert data.get("graphiti_write_enabled") is False


# ── Test 28 ────────────────────────────────────────────────────────────────────
def test_kernel_mutation_enabled_false():
    data = load_p64()
    assert data.get("kernel_mutation_enabled") is False


# ── Test 29 ────────────────────────────────────────────────────────────────────
def test_p56e_still_passes():
    p56e = REPO_ROOT / "docs" / "core_import" / "P56E_POST_PATCH_METRIC_REAUDIT.json"
    assert p56e.exists(), "P56E JSON absent"
    data = json.load(open(p56e))
    verdict = data.get("final_verdict", data.get("status", ""))
    assert "PASS" in verdict or "READY" in verdict, f"P56E non PASS : {verdict}"


# ── Test 30 ────────────────────────────────────────────────────────────────────
def test_p57_still_passes():
    p57 = REPO_ROOT / "docs" / "core_import" / "P57_CORE_MACHINERY_INVENTORY.json"
    assert p57.exists(), "P57 JSON absent"
    data = json.load(open(p57))
    assert isinstance(data, list) and len(data) > 0, "P57 inventory vide"


# ── Test 31 ────────────────────────────────────────────────────────────────────
def test_p58_still_passes():
    p58 = REPO_ROOT / "docs" / "core_import" / "P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.json"
    assert p58.exists(), "P58 JSON absent"
    data = json.load(open(p58))
    status = data.get("status", "")
    assert "READY" in status or "PASS" in status or "TRIAGE" in status


# ── Test 32 ────────────────────────────────────────────────────────────────────
def test_p59_still_passes():
    p59 = REPO_ROOT / "docs" / "core_import" / "P59_SAFE_BATCH_1_IMPORT.json"
    assert p59.exists(), "P59 JSON absent"
    assert "READY" in json.load(open(p59)).get("status", "")


# ── Test 33 ────────────────────────────────────────────────────────────────────
def test_p60_still_passes():
    p60 = REPO_ROOT / "docs" / "core_import" / "P60_TEST_BATCH_2_IMPORT.json"
    assert p60.exists(), "P60 JSON absent"
    assert "READY" in json.load(open(p60)).get("status", "")


# ── Test 34 ────────────────────────────────────────────────────────────────────
def test_p61_still_passes():
    p61 = REPO_ROOT / "docs" / "core_import" / "P61_BUS_ADAPTER_BATCH.json"
    assert p61.exists(), "P61 JSON absent"
    assert "READY" in json.load(open(p61)).get("status", "")


# ── Test 35 ────────────────────────────────────────────────────────────────────
def test_p62_still_passes():
    p62 = REPO_ROOT / "docs" / "core_import" / "P62_MANUAL_REVIEW_DEFERRED.json"
    assert p62.exists(), "P62 JSON absent"
    assert "CLASSIFIED" in json.load(open(p62)).get("status", "")


# ── Test 36 ────────────────────────────────────────────────────────────────────
def test_p63_still_passes():
    p63 = REPO_ROOT / "docs" / "core_import" / "P63_GLOBAL_FUSION_REALITY_AUDIT.json"
    assert p63.exists(), "P63 JSON absent"
    assert "READY" in json.load(open(p63)).get("status", "")


# ── Test 37 ────────────────────────────────────────────────────────────────────
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


# ── Test 38 ────────────────────────────────────────────────────────────────────
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
