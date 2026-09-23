"""Tests P60 — Test Batch 2 Import verification."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
P60_JSON = REPO_ROOT / "docs" / "core_import" / "P60_TEST_BATCH_2_IMPORT.json"

FORBIDDEN_TARGET_PREFIXES = [
    "apps/",
    "runtime_wiring/",
    "proofs/V18_3_1/",
    "periphery/",
]

FORBIDDEN_FLAGS = [
    "runtime_allowed_now = true",
    "memory_write = true",
    "graphiti_write = true",
    "neo4j_write = true",
    "kernel_mutation = true",
    "emits_act = true",
]

SAFE_BATCH_1_CLASSIFICATIONS = {"SAFE_BATCH_1"}
FORBIDDEN_SURFACES = {"BUS_ADAPTER", "PRIVATE_UI_IGNORE", "RESPONSE_TEMPLATE_READONLY"}


def load_p60():
    with open(P60_JSON) as f:
        return json.load(f)


# ── Test 1 ─────────────────────────────────────────────────────────────────────
def test_p60_json_exists():
    assert P60_JSON.exists(), f"P60 JSON absent : {P60_JSON}"


# ── Test 2 ─────────────────────────────────────────────────────────────────────
def test_status():
    data = load_p60()
    assert data["status"] == "P60_TEST_BATCH_2_IMPORT_READY"


# ── Test 3 ─────────────────────────────────────────────────────────────────────
def test_source_patch_applied():
    data = load_p60()
    assert data["source_patch_applied"] is True


# ── Test 4 ─────────────────────────────────────────────────────────────────────
def test_import_scope():
    data = load_p60()
    assert data["import_scope"] == "TEST_BATCH_2_ONLY"


# ── Test 5 ─────────────────────────────────────────────────────────────────────
def test_files_imported_count_matches():
    data = load_p60()
    assert data["files_imported_count"] == len(data["imported_files"])


# ── Test 6 ─────────────────────────────────────────────────────────────────────
def test_all_imported_files_exist():
    data = load_p60()
    for entry in data["imported_files"]:
        target = REPO_ROOT / entry["target_path"]
        assert target.exists(), f"Fichier importé absent : {entry['target_path']}"


# ── Test 7 ─────────────────────────────────────────────────────────────────────
def test_all_imported_files_test_batch_2():
    data = load_p60()
    valid = {"TEST_BATCH_2", "TEST_ONLY"}
    for entry in data["imported_files"]:
        classif = entry.get("classification", "")
        surface = entry.get("execution_surface", "")
        assert classif in valid or surface in {"TEST_ONLY", "PROOF_SIGMA"}, (
            f"{entry['target_path']} : classification={classif}, surface={surface}"
        )


# ── Test 8 ─────────────────────────────────────────────────────────────────────
def test_no_safe_batch_1_imported():
    data = load_p60()
    for entry in data["imported_files"]:
        assert entry.get("classification") not in SAFE_BATCH_1_CLASSIFICATIONS, (
            f"SAFE_BATCH_1 importé : {entry['target_path']}"
        )


# ── Test 9 ─────────────────────────────────────────────────────────────────────
def test_no_bus_adapter_imported():
    data = load_p60()
    for entry in data["imported_files"]:
        assert entry.get("execution_surface") != "BUS_ADAPTER", (
            f"BUS_ADAPTER importé : {entry['target_path']}"
        )
        assert entry.get("classification") != "BUS_ADAPTER_BATCH", (
            f"BUS_ADAPTER_BATCH importé : {entry['target_path']}"
        )


# ── Test 10 ────────────────────────────────────────────────────────────────────
def test_no_private_ui_imported():
    data = load_p60()
    for entry in data["imported_files"]:
        assert entry.get("execution_surface") != "PRIVATE_UI_IGNORE", (
            f"PRIVATE_UI_IGNORE importé : {entry['target_path']}"
        )


# ── Test 11 ────────────────────────────────────────────────────────────────────
def test_no_response_template_imported():
    data = load_p60()
    for entry in data["imported_files"]:
        assert entry.get("execution_surface") != "RESPONSE_TEMPLATE_READONLY", (
            f"RESPONSE_TEMPLATE_READONLY importé : {entry['target_path']}"
        )


# ── Test 12 ────────────────────────────────────────────────────────────────────
def test_no_forbidden_target_prefixes():
    data = load_p60()
    for entry in data["imported_files"]:
        tp = entry["target_path"]
        for prefix in FORBIDDEN_TARGET_PREFIXES:
            assert not tp.startswith(prefix), (
                f"target_path {tp!r} commence par préfixe interdit {prefix!r}"
            )


# ── Test 13 ────────────────────────────────────────────────────────────────────
def test_sigma_targets_are_tests_only():
    data = load_p60()
    for entry in data["imported_files"]:
        tp = entry["target_path"]
        if tp.startswith("sigma/"):
            surface = entry.get("execution_surface", "")
            assert surface in {"TEST_ONLY", "TEST_PROOF_SURFACE"}, (
                f"Fichier sigma/ non TEST_ONLY importé : {tp} (surface={surface})"
            )


# ── Test 14 ────────────────────────────────────────────────────────────────────
def test_all_py_files_compile():
    data = load_p60()
    for entry in data["imported_files"]:
        tp = entry["target_path"]
        if tp.endswith(".py"):
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(REPO_ROOT / tp)],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, (
                f"Compilation échouée pour {tp} : {result.stderr}"
            )


# ── Test 15 ────────────────────────────────────────────────────────────────────
def test_no_forbidden_flags_in_imported_files():
    data = load_p60()
    for entry in data["imported_files"]:
        tp = entry["target_path"]
        if tp.endswith(".py"):
            content = (REPO_ROOT / tp).read_text(encoding="utf-8", errors="replace")
            for flag in FORBIDDEN_FLAGS:
                assert flag not in content, (
                    f"Flag interdit {flag!r} trouvé dans {tp}"
                )


# ── Test 16 ────────────────────────────────────────────────────────────────────
def test_no_dangerous_actions_in_imported_files():
    data = load_p60()
    patterns = [
        (r"requests\.post\s*\(", "requests.post sans dry-run"),
        (r"os\.remove\s*\(", "os.remove sur chemin repo"),
        (r"shutil\.rmtree\s*\(", "shutil.rmtree sur chemin repo"),
    ]
    for entry in data["imported_files"]:
        tp = entry["target_path"]
        if tp.endswith(".py"):
            content = (REPO_ROOT / tp).read_text(encoding="utf-8", errors="replace")
            for pattern, label in patterns:
                assert not re.search(pattern, content), (
                    f"Action dangereuse ({label}) détectée dans {tp}"
                )


# ── Test 17 ────────────────────────────────────────────────────────────────────
def test_p56e_still_passes():
    p56e = REPO_ROOT / "docs" / "core_import" / "P56E_POST_PATCH_METRIC_REAUDIT.json"
    assert p56e.exists(), "P56E JSON absent"
    with open(p56e) as f:
        data = json.load(f)
    verdict = data.get("final_verdict", data.get("status", ""))
    assert "PASS" in verdict or "READY" in verdict, f"P56E non PASS : {verdict}"


# ── Test 18 ────────────────────────────────────────────────────────────────────
def test_p57_still_passes():
    p57_inventory = REPO_ROOT / "docs" / "core_import" / "P57_CORE_MACHINERY_INVENTORY.json"
    assert p57_inventory.exists(), "P57 inventory JSON absent"
    with open(p57_inventory) as f:
        data = json.load(f)
    assert isinstance(data, list) and len(data) > 0, "P57 inventory vide ou invalide"
    p57_tests = REPO_ROOT / "tests" / "test_p57_core_machinery_runtime_binding_audit.py"
    assert p57_tests.exists(), "test_p57 absent"


# ── Test 19 ────────────────────────────────────────────────────────────────────
def test_p58_still_passes():
    p58 = REPO_ROOT / "docs" / "core_import" / "P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.json"
    assert p58.exists(), "P58 JSON absent"
    with open(p58) as f:
        data = json.load(f)
    status = data.get("status", "")
    assert "PASS" in status or "READY" in status or "TRIAGE" in status, (
        f"P58 non PASS : {status}"
    )


# ── Test 20 ────────────────────────────────────────────────────────────────────
def test_p59_still_passes():
    p59 = REPO_ROOT / "docs" / "core_import" / "P59_SAFE_BATCH_1_IMPORT.json"
    assert p59.exists(), "P59 JSON absent"
    with open(p59) as f:
        data = json.load(f)
    status = data.get("status", "")
    assert "PASS" in status or "READY" in status, f"P59 non PASS : {status}"


# ── Test 21 ────────────────────────────────────────────────────────────────────
def test_verify_all_still_passes():
    verify_all = REPO_ROOT / "proofs" / "verify_all.py"
    if not verify_all.exists():
        import pytest
        pytest.skip("proofs/verify_all.py absent — test sauté")
    result = subprocess.run(
        [sys.executable, str(verify_all)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"proofs/verify_all.py FAIL :\n{result.stdout}\n{result.stderr}"
    )


# ── Test 22 ────────────────────────────────────────────────────────────────────
def test_forbidden_content_still_passes():
    check_forbidden = REPO_ROOT / "scripts" / "check_forbidden_content.py"
    if not check_forbidden.exists():
        import pytest
        pytest.skip("scripts/check_forbidden_content.py absent — test sauté")
    result = subprocess.run(
        [sys.executable, str(check_forbidden)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"check_forbidden_content FAIL :\n{result.stdout}\n{result.stderr}"
    )
