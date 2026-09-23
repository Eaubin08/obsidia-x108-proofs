"""Tests P62 — Manual Review Deferred Classification verification."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
P62_JSON = REPO_ROOT / "docs" / "core_import" / "P62_MANUAL_REVIEW_DEFERRED.json"

ALLOWED_DECISIONS = {
    "KEEP_PROOF_VERSION",
    "IMPORT_TEST_ONLY",
    "IMPORT_DOC_ONLY",
    "IMPORT_AFTER_ADAPTER",
    "DO_NOT_IMPORT",
    "BLOCKED_REQUIRES_ARCHITECTURAL_REVIEW",
    "SAFE_READONLY_ADAPTER_CANDIDATE",
}

FORBIDDEN_MODIFIED_PREFIXES = [
    "apps/obsidia_api/routes/",
    "sigma/",
    "runtime_wiring/",
    "proofs/V18_3_1/",
]


def load_p62():
    with open(P62_JSON) as f:
        return json.load(f)


# ── Test 1 ─────────────────────────────────────────────────────────────────────
def test_p62_json_exists():
    assert P62_JSON.exists(), f"P62 JSON absent : {P62_JSON}"


# ── Test 2 ─────────────────────────────────────────────────────────────────────
def test_status():
    data = load_p62()
    assert data["status"] == "P62_MANUAL_REVIEW_CLASSIFIED"


# ── Test 3 ─────────────────────────────────────────────────────────────────────
def test_source_patch_applied_false():
    data = load_p62()
    assert data["source_patch_applied"] is False


# ── Test 4 ─────────────────────────────────────────────────────────────────────
def test_import_scope():
    data = load_p62()
    assert data["import_scope"] == "MANUAL_REVIEW_DEFERRED_ONLY"


# ── Test 5 ─────────────────────────────────────────────────────────────────────
def test_review_mode():
    data = load_p62()
    assert data["review_mode"] == "CLASSIFICATION_ONLY"


# ── Test 6 ─────────────────────────────────────────────────────────────────────
def test_files_imported_count_zero():
    data = load_p62()
    assert data["files_imported_count"] == 0


# ── Test 7 ─────────────────────────────────────────────────────────────────────
def test_reviewed_files_non_empty():
    data = load_p62()
    assert len(data["reviewed_files"]) > 0, "reviewed_files est vide"


# ── Test 8 ─────────────────────────────────────────────────────────────────────
def test_all_reviewed_files_manual_review_deferred():
    data = load_p62()
    for entry in data["reviewed_files"]:
        assert entry["classification"] == "MANUAL_REVIEW_DEFERRED", (
            f"{entry['core_path']} : classification={entry['classification']}"
        )


# ── Test 9 ─────────────────────────────────────────────────────────────────────
def test_no_safe_batch_1_in_reviewed():
    data = load_p62()
    for entry in data["reviewed_files"]:
        assert entry["classification"] != "SAFE_BATCH_1", (
            f"SAFE_BATCH_1 dans reviewed_files : {entry['core_path']}"
        )


# ── Test 10 ────────────────────────────────────────────────────────────────────
def test_no_test_batch_2_in_reviewed():
    data = load_p62()
    for entry in data["reviewed_files"]:
        assert entry["classification"] != "TEST_BATCH_2", (
            f"TEST_BATCH_2 dans reviewed_files : {entry['core_path']}"
        )


# ── Test 11 ────────────────────────────────────────────────────────────────────
def test_no_bus_adapter_batch_in_reviewed():
    data = load_p62()
    for entry in data["reviewed_files"]:
        assert entry["classification"] != "BUS_ADAPTER_BATCH", (
            f"BUS_ADAPTER_BATCH dans reviewed_files : {entry['core_path']}"
        )


# ── Test 12 ────────────────────────────────────────────────────────────────────
def test_no_private_ui_in_reviewed():
    data = load_p62()
    for entry in data["reviewed_files"]:
        assert entry["classification"] not in {"PRIVATE_UI_EXCLUDED", "PRIVATE_UI_IGNORE"}, (
            f"PRIVATE_UI dans reviewed_files : {entry['core_path']}"
        )


# ── Test 13 ────────────────────────────────────────────────────────────────────
def test_all_entries_have_valid_decision():
    data = load_p62()
    for entry in data["reviewed_files"]:
        assert entry["decision"] in ALLOWED_DECISIONS, (
            f"{entry['core_path']} : decision invalide {entry['decision']!r}"
        )


# ── Test 14 ────────────────────────────────────────────────────────────────────
def test_all_existing_sources_have_sha():
    data = load_p62()
    for entry in data["reviewed_files"]:
        if entry["source_exists"] and not entry["core_path"].endswith("/"):
            assert entry["source_sha256"] is not None, (
                f"{entry['core_path']} source existe mais sha256 absent"
            )


# ── Test 15 ────────────────────────────────────────────────────────────────────
def test_decision_counts_match_reviewed_files():
    data = load_p62()
    from collections import Counter
    actual = Counter(e["decision"] for e in data["reviewed_files"])
    reported = data["decision_counts"]
    for decision, count in actual.items():
        assert reported.get(decision, 0) == count, (
            f"decision_counts[{decision!r}]={reported.get(decision)} != actual={count}"
        )
    assert sum(actual.values()) == len(data["reviewed_files"])


# ── Test 16 ────────────────────────────────────────────────────────────────────
def test_no_routes_modified():
    data = load_p62()
    assert data.get("apps_routes_modified") is False


# ── Test 17 ────────────────────────────────────────────────────────────────────
def test_sigma_not_modified():
    data = load_p62()
    assert data.get("sigma_modified") is False


# ── Test 18 ────────────────────────────────────────────────────────────────────
def test_runtime_wiring_not_modified():
    data = load_p62()
    assert data.get("runtime_wiring_modified") is False


# ── Test 19 ────────────────────────────────────────────────────────────────────
def test_proofs_v18_3_1_not_modified():
    data = load_p62()
    assert data.get("proofs_v18_3_1_modified") is False


# ── Test 20 ────────────────────────────────────────────────────────────────────
def test_act_not_enabled():
    data = load_p62()
    assert data.get("act_enabled") is False


# ── Test 21 ────────────────────────────────────────────────────────────────────
def test_memory_write_not_enabled():
    data = load_p62()
    assert data.get("memory_write_enabled") is False


# ── Test 22 ────────────────────────────────────────────────────────────────────
def test_graphiti_write_not_enabled():
    data = load_p62()
    assert data.get("graphiti_write_enabled") is False


# ── Test 23 ────────────────────────────────────────────────────────────────────
def test_kernel_mutation_not_enabled():
    data = load_p62()
    assert data.get("kernel_mutation_enabled") is False


# ── Test 24 ────────────────────────────────────────────────────────────────────
def test_p56e_still_passes():
    p56e = REPO_ROOT / "docs" / "core_import" / "P56E_POST_PATCH_METRIC_REAUDIT.json"
    assert p56e.exists()
    data = json.load(open(p56e))
    verdict = data.get("final_verdict", data.get("status", ""))
    assert "PASS" in verdict or "READY" in verdict


# ── Test 25 ────────────────────────────────────────────────────────────────────
def test_p57_still_passes():
    p57 = REPO_ROOT / "docs" / "core_import" / "P57_CORE_MACHINERY_INVENTORY.json"
    assert p57.exists()
    data = json.load(open(p57))
    assert isinstance(data, list) and len(data) > 0


# ── Test 26 ────────────────────────────────────────────────────────────────────
def test_p58_still_passes():
    p58 = REPO_ROOT / "docs" / "core_import" / "P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.json"
    assert p58.exists()
    data = json.load(open(p58))
    assert "READY" in data.get("status","") or "TRIAGE" in data.get("status","")


# ── Test 27 ────────────────────────────────────────────────────────────────────
def test_p59_still_passes():
    p59 = REPO_ROOT / "docs" / "core_import" / "P59_SAFE_BATCH_1_IMPORT.json"
    assert p59.exists()
    assert "READY" in json.load(open(p59)).get("status","")


# ── Test 28 ────────────────────────────────────────────────────────────────────
def test_p60_still_passes():
    p60 = REPO_ROOT / "docs" / "core_import" / "P60_TEST_BATCH_2_IMPORT.json"
    assert p60.exists()
    assert "READY" in json.load(open(p60)).get("status","")


# ── Test 29 ────────────────────────────────────────────────────────────────────
def test_p61_still_passes():
    p61 = REPO_ROOT / "docs" / "core_import" / "P61_BUS_ADAPTER_BATCH.json"
    assert p61.exists()
    assert "READY" in json.load(open(p61)).get("status","")


# ── Test 30 ────────────────────────────────────────────────────────────────────
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


# ── Test 31 ────────────────────────────────────────────────────────────────────
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
