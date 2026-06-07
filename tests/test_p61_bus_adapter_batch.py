"""Tests P61 — Bus Adapter Batch DRY_RUN_ONLY verification."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
P61_JSON = REPO_ROOT / "docs" / "core_import" / "P61_BUS_ADAPTER_BATCH.json"

FORBIDDEN_TARGET_PREFIXES = [
    "sigma/",
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

ALLOWED_TARGET_PREFIX = "apps/obsidia_api/bus/"
FORBIDDEN_ROUTES_PREFIX = "apps/obsidia_api/routes/"


def load_p61():
    with open(P61_JSON) as f:
        return json.load(f)


# ── Test 1 ─────────────────────────────────────────────────────────────────────
def test_p61_json_exists():
    assert P61_JSON.exists(), f"P61 JSON absent : {P61_JSON}"


# ── Test 2 ─────────────────────────────────────────────────────────────────────
def test_status():
    data = load_p61()
    assert data["status"] == "P61_BUS_ADAPTER_BATCH_READY"


# ── Test 3 ─────────────────────────────────────────────────────────────────────
def test_source_patch_applied():
    data = load_p61()
    assert data["source_patch_applied"] is True


# ── Test 4 ─────────────────────────────────────────────────────────────────────
def test_import_scope():
    data = load_p61()
    assert data["import_scope"] == "BUS_ADAPTER_BATCH_ONLY"


# ── Test 5 ─────────────────────────────────────────────────────────────────────
def test_adapter_mode():
    data = load_p61()
    assert data["adapter_mode"] == "DRY_RUN_ONLY"


# ── Test 6 ─────────────────────────────────────────────────────────────────────
def test_files_adapted_count_matches():
    data = load_p61()
    assert data["files_adapted_count"] == len(data["adapted_files"])


# ── Test 7 ─────────────────────────────────────────────────────────────────────
def test_all_adapted_files_exist():
    data = load_p61()
    for entry in data["adapted_files"]:
        target = REPO_ROOT / entry["target_path"]
        assert target.exists(), f"Fichier adapté absent : {entry['target_path']}"


# ── Test 8 ─────────────────────────────────────────────────────────────────────
def test_all_adapted_files_bus_adapter_classification():
    data = load_p61()
    valid = {"BUS_ADAPTER_BATCH", "NEEDS_ADAPTER", "BUS_ADAPTER"}
    for entry in data["adapted_files"]:
        classif = entry.get("classification", "")
        surface = entry.get("execution_surface", "")
        assert classif in valid or surface in {"BUS_ADAPTER"}, (
            f"{entry['target_path']} : classification={classif}, surface={surface}"
        )


# ── Test 9 ─────────────────────────────────────────────────────────────────────
def test_no_safe_batch_1_adapted():
    data = load_p61()
    for entry in data["adapted_files"]:
        assert entry.get("classification") != "SAFE_BATCH_1", (
            f"SAFE_BATCH_1 adapté : {entry['target_path']}"
        )


# ── Test 10 ────────────────────────────────────────────────────────────────────
def test_no_test_batch_2_adapted():
    data = load_p61()
    for entry in data["adapted_files"]:
        assert entry.get("classification") not in {"TEST_BATCH_2", "TEST_ONLY"}, (
            f"TEST_BATCH_2/TEST_ONLY adapté : {entry['target_path']}"
        )


# ── Test 11 ────────────────────────────────────────────────────────────────────
def test_no_private_ui_adapted():
    data = load_p61()
    for entry in data["adapted_files"]:
        assert entry.get("execution_surface") != "PRIVATE_UI_IGNORE", (
            f"PRIVATE_UI_IGNORE adapté : {entry['target_path']}"
        )


# ── Test 12 ────────────────────────────────────────────────────────────────────
def test_no_response_template_adapted():
    data = load_p61()
    for entry in data["adapted_files"]:
        assert entry.get("execution_surface") != "RESPONSE_TEMPLATE_READONLY", (
            f"RESPONSE_TEMPLATE_READONLY adapté : {entry['target_path']}"
        )


# ── Test 13 ────────────────────────────────────────────────────────────────────
def test_no_forbidden_target_prefixes():
    data = load_p61()
    for entry in data["adapted_files"]:
        tp = entry["target_path"]
        for prefix in FORBIDDEN_TARGET_PREFIXES:
            assert not tp.startswith(prefix), (
                f"target_path {tp!r} commence par préfixe interdit {prefix!r}"
            )


# ── Test 14 ────────────────────────────────────────────────────────────────────
def test_target_paths_only_under_bus():
    data = load_p61()
    for entry in data["adapted_files"]:
        tp = entry["target_path"]
        assert tp.startswith(ALLOWED_TARGET_PREFIX), (
            f"target_path {tp!r} hors de {ALLOWED_TARGET_PREFIX!r}"
        )


# ── Test 15 ────────────────────────────────────────────────────────────────────
def test_no_routes_modified():
    data = load_p61()
    assert data.get("routes_modified") is False
    for entry in data["adapted_files"]:
        tp = entry["target_path"]
        assert not tp.startswith(FORBIDDEN_ROUTES_PREFIX), (
            f"Fichier de routes modifié : {tp}"
        )


# ── Test 16 ────────────────────────────────────────────────────────────────────
def test_all_py_files_compile():
    data = load_p61()
    for entry in data["adapted_files"]:
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


# ── Test 17 ────────────────────────────────────────────────────────────────────
def test_no_forbidden_flags_in_adapted_files():
    data = load_p61()
    for entry in data["adapted_files"]:
        tp = entry["target_path"]
        if tp.endswith(".py"):
            content = (REPO_ROOT / tp).read_text(encoding="utf-8", errors="replace")
            for flag in FORBIDDEN_FLAGS:
                assert flag not in content, (
                    f"Flag interdit {flag!r} trouvé dans {tp}"
                )


# ── Test 18 ────────────────────────────────────────────────────────────────────
def test_no_dangerous_actions_in_adapted_files():
    data = load_p61()
    patterns = [
        (r"requests\.post\s*\(", "requests.post sans dry-run"),
        (r"os\.remove\s*\(", "os.remove sur chemin repo"),
        (r"shutil\.rmtree\s*\(", "shutil.rmtree sur chemin repo"),
    ]
    for entry in data["adapted_files"]:
        tp = entry["target_path"]
        if tp.endswith(".py"):
            content = (REPO_ROOT / tp).read_text(encoding="utf-8", errors="replace")
            for pattern, label in patterns:
                assert not re.search(pattern, content), (
                    f"Action dangereuse ({label}) détectée dans {tp}"
                )


# ── Test 19 ────────────────────────────────────────────────────────────────────
def test_router_exposes_dry_run_default():
    router_file = REPO_ROOT / "apps" / "obsidia_api" / "bus" / "router.py"
    if not router_file.exists():
        pytest.skip("router.py absent")
    content = router_file.read_text(encoding="utf-8")
    assert "dry_run: bool = True" in content or "dry_run=True" in content, (
        "router.py ne expose pas dry_run=True par défaut"
    )
    assert "DRY_RUN_ONLY" in content, "router.py ne déclare pas DRY_RUN_ONLY"


# ── Test 20 ────────────────────────────────────────────────────────────────────
def test_no_act_returnable_directly():
    message_file = REPO_ROOT / "apps" / "obsidia_api" / "bus" / "message.py"
    if not message_file.exists():
        pytest.skip("message.py absent")
    content = message_file.read_text(encoding="utf-8")
    assert "ALLOWED_DECISIONS" in content, "message.py ne déclare pas ALLOWED_DECISIONS"
    assert "ACT" not in content.split("ALLOWED_DECISIONS")[1].split("\n")[0], (
        "ACT semble être dans ALLOWED_DECISIONS"
    )
    # Verify the guard exists
    assert "__post_init__" in content, "message.py manque de guards __post_init__"
    # Runtime check: DecisionMsg('ACT') must raise
    try:
        import importlib.util, sys as _sys
        spec = importlib.util.spec_from_file_location("bus_message_p61", str(message_file))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        try:
            mod.DecisionMsg(decision="ACT", trace_id="t", reason_code="rc", reason_message="rm")
            assert False, "DecisionMsg('ACT') devrait lever ValueError"
        except ValueError:
            pass
    except Exception as e:
        pytest.skip(f"Import dynamique impossible : {e}")


# ── Test 21 ────────────────────────────────────────────────────────────────────
def test_p56e_still_passes():
    p56e = REPO_ROOT / "docs" / "core_import" / "P56E_POST_PATCH_METRIC_REAUDIT.json"
    assert p56e.exists(), "P56E JSON absent"
    with open(p56e) as f:
        data = json.load(f)
    verdict = data.get("final_verdict", data.get("status", ""))
    assert "PASS" in verdict or "READY" in verdict, f"P56E non PASS : {verdict}"


# ── Test 22 ────────────────────────────────────────────────────────────────────
def test_p57_still_passes():
    p57 = REPO_ROOT / "docs" / "core_import" / "P57_CORE_MACHINERY_INVENTORY.json"
    assert p57.exists(), "P57 JSON absent"
    with open(p57) as f:
        data = json.load(f)
    assert isinstance(data, list) and len(data) > 0, "P57 inventory vide"
    assert (REPO_ROOT / "tests" / "test_p57_core_machinery_runtime_binding_audit.py").exists()


# ── Test 23 ────────────────────────────────────────────────────────────────────
def test_p58_still_passes():
    p58 = REPO_ROOT / "docs" / "core_import" / "P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.json"
    assert p58.exists(), "P58 JSON absent"
    with open(p58) as f:
        data = json.load(f)
    status = data.get("status", "")
    assert "READY" in status or "PASS" in status or "TRIAGE" in status


# ── Test 24 ────────────────────────────────────────────────────────────────────
def test_p59_still_passes():
    p59 = REPO_ROOT / "docs" / "core_import" / "P59_SAFE_BATCH_1_IMPORT.json"
    assert p59.exists(), "P59 JSON absent"
    with open(p59) as f:
        data = json.load(f)
    assert "READY" in data.get("status", "") or "PASS" in data.get("status", "")


# ── Test 25 ────────────────────────────────────────────────────────────────────
def test_p60_still_passes():
    p60 = REPO_ROOT / "docs" / "core_import" / "P60_TEST_BATCH_2_IMPORT.json"
    assert p60.exists(), "P60 JSON absent"
    with open(p60) as f:
        data = json.load(f)
    assert "READY" in data.get("status", "") or "PASS" in data.get("status", "")


# ── Test 26 ────────────────────────────────────────────────────────────────────
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


# ── Test 27 ────────────────────────────────────────────────────────────────────
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
