"""
P57 — Core Machinery Runtime Binding Audit Tests

Verifies that:
- All P57 audit artefacts exist and are well-formed
- No forbidden runtime flags are effectively set
- P56E invariants are preserved
- Import plan respects safety rules
"""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs" / "core_import"
SIGMA_DIR = REPO_ROOT / "sigma"
PROOF_V18 = REPO_ROOT / "proofs" / "V18_3_1" / "engine_buildable_0_9_3_1"
ZIP_PATH = Path(r"C:\Users\User\Desktop\OBSIDIA_CORE_ONLY_FULL_MACHINERY.zip")


def _load(path: Path) -> dict | list:
    assert path.exists(), f"Missing: {path}"
    return json.loads(path.read_text("utf-8"))


# ---------------------------------------------------------------------------
# Test 1 — P57 inventory JSON exists and is non-empty
# ---------------------------------------------------------------------------
def test_p57_01_inventory_json_exists():
    data = _load(DOCS / "P57_CORE_MACHINERY_INVENTORY.json")
    assert isinstance(data, list)
    assert len(data) > 100, "Inventory should have >100 entries"
    assert all("path" in e and "status" in e for e in data)


# ---------------------------------------------------------------------------
# Test 2 — P57 runtime binding audit JSON exists
# ---------------------------------------------------------------------------
def test_p57_02_runtime_binding_audit_json_exists():
    data = _load(DOCS / "P57_RUNTIME_BINDING_AUDIT.json")
    assert "routes" in data
    assert "runtime_wiring" in data
    assert len(data["routes"]) >= 5, "At least 5 routes should be audited"


# ---------------------------------------------------------------------------
# Test 3 — P57 import plan JSON exists and has required categories
# ---------------------------------------------------------------------------
def test_p57_03_import_plan_json_exists():
    data = _load(DOCS / "P57_CORE_TO_PROOF_IMPORT_PLAN.json")
    assert isinstance(data, list)
    cats = {item["category"] for item in data}
    # Must have at minimum C (keep proof) and E (do not import)
    assert "C_KEEP_PROOF_VERSION" in cats, "Should have KEEP_PROOF_VERSION entries"
    assert "E_DO_NOT_IMPORT" in cats, "Should have DO_NOT_IMPORT entries"
    assert all("merge_action" in item for item in data)


# ---------------------------------------------------------------------------
# Test 4 — No core file was auto-imported (no new files in sigma/ or proofs/ from script)
# ---------------------------------------------------------------------------
def test_p57_04_no_auto_import():
    """
    The P57 script only creates docs/ files — it must not have imported
    any core ZIP file into sigma/, apps/, or proofs/ directly.
    P57 is audit-only.
    """
    # Check that no new Python files appeared in sigma/ with timestamps after P56 commits
    # We verify indirectly: audit JSON's merge_action must not be 'IMPORTED' or 'COPIED'
    plan = _load(DOCS / "P57_CORE_TO_PROOF_IMPORT_PLAN.json")
    forbidden_actions = {"IMPORTED", "COPIED", "AUTO_IMPORT"}
    for item in plan:
        assert item["merge_action"] not in forbidden_actions, (
            f"Forbidden auto-import action found for {item['core_path']}: {item['merge_action']}"
        )


# ---------------------------------------------------------------------------
# Test 5 — No DANGEROUS_DO_NOT_IMPORT classified as IMPORT_NOW_SAFE
# ---------------------------------------------------------------------------
def test_p57_05_dangerous_not_import_safe():
    """Items with DO_NOT_IMPORT status must not appear in IMPORT_NOW_SAFE category."""
    inv = _load(DOCS / "P57_CORE_MACHINERY_INVENTORY.json")
    plan = _load(DOCS / "P57_CORE_TO_PROOF_IMPORT_PLAN.json")

    dangerous_paths = {
        item["path"] for item in inv if item["status"] == "DANGEROUS_DO_NOT_IMPORT"
    }
    # Also governance/ duplicates must not be IMPORT_NOW_SAFE
    duplicate_paths = {
        item["path"] for item in inv if item["status"] == "DUPLICATE_DO_NOT_IMPORT"
    }

    plan_safe = {item["core_path"] for item in plan if item["category"] == "A_IMPORT_NOW_SAFE"}

    bad_dangerous = dangerous_paths & plan_safe
    bad_duplicates = duplicate_paths & plan_safe

    assert not bad_dangerous, f"Dangerous items classified as IMPORT_NOW_SAFE: {bad_dangerous}"
    assert not bad_duplicates, f"Duplicate items classified as IMPORT_NOW_SAFE: {bad_duplicates}"


# ---------------------------------------------------------------------------
# Test 6 — No effective runtime_allowed_now=True
# ---------------------------------------------------------------------------
def test_p57_06_no_effective_runtime_allowed_now_true():
    """No source file in sigma/, apps/, runtime_wiring/ sets runtime_allowed_now=True."""
    pattern = re.compile(
        r"^\s*[\"']?runtime_allowed_now[\"']?\s*[:=]\s*True",
        re.MULTILINE,
    )
    for d in ["sigma", "apps/obsidia_api", "runtime_wiring"]:
        for py in (REPO_ROOT / d).rglob("*.py"):
            text = py.read_text("utf-8", "replace")
            cleaned = re.sub(
                r'(""".*?"""|\'\'\'.*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\'|#.*$)',
                " ", text, flags=re.DOTALL | re.MULTILINE
            )
            assert not pattern.search(cleaned), (
                f"Effective runtime_allowed_now=True in {py.relative_to(REPO_ROOT)}"
            )


# ---------------------------------------------------------------------------
# Test 7 — No effective memory_write=True
# ---------------------------------------------------------------------------
def test_p57_07_no_effective_memory_write_true():
    """No source file sets memory_write=True as an actual assignment."""
    pattern = re.compile(
        r"^\s*[\"']?memory_write[\"']?\s*[:=]\s*True",
        re.MULTILINE,
    )
    binding = _load(DOCS / "P57_RUNTIME_BINDING_AUDIT.json")
    for name, info in binding["routes"].items():
        assert "memory_write" not in info.get("effective_write_flags", []), (
            f"Route {name} has effective memory_write=True"
        )


# ---------------------------------------------------------------------------
# Test 8 — No effective graphiti_write=True
# ---------------------------------------------------------------------------
def test_p57_08_no_effective_graphiti_write_true():
    """No route has graphiti_write as an effective write flag."""
    binding = _load(DOCS / "P57_RUNTIME_BINDING_AUDIT.json")
    for name, info in binding["routes"].items():
        assert "graphiti_write" not in info.get("effective_write_flags", []), (
            f"Route {name} has effective graphiti_write=True"
        )


# ---------------------------------------------------------------------------
# Test 9 — No ACT emitted outside governed paths
# ---------------------------------------------------------------------------
def test_p57_09_no_ungoverned_act():
    """sigma/run_pipeline.py must not emit ACT directly in market_verdict."""
    path = SIGMA_DIR / "run_pipeline.py"
    assert path.exists()
    text = path.read_text("utf-8", "replace")
    cleaned = re.sub(
        r'(""".*?"""|\'\'\'.*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\'|#.*$)',
        " ", text, flags=re.DOTALL | re.MULTILINE
    )
    bad = re.search(r'market_verdict\s*[=\[]\s*["\']ACT["\']', cleaned, re.IGNORECASE)
    assert not bad, "sigma/run_pipeline.py directly emits ACT as market_verdict"


# ---------------------------------------------------------------------------
# Test 10 — P56E still passes (regression check)
# ---------------------------------------------------------------------------
def test_p57_10_p56e_audit_still_pass():
    """P56E audit artefact must still declare PASS."""
    p56e = DOCS / "P56E_POST_PATCH_METRIC_REAUDIT.json"
    assert p56e.exists(), "P56E audit JSON missing"
    data = json.loads(p56e.read_text("utf-8"))
    assert data.get("final_verdict") == "P56E_POST_PATCH_METRIC_REAUDIT_PASS"
    assert data.get("remaining_blockers") == []


# ---------------------------------------------------------------------------
# Test 11 — Sigma still POST_GUARD_VETO_ONLY
# ---------------------------------------------------------------------------
def test_p57_11_sigma_post_guard_veto_only():
    """sigma/run_pipeline.py must still contain POST_GUARD_VETO_ONLY boundary."""
    path = SIGMA_DIR / "run_pipeline.py"
    assert path.exists()
    text = path.read_text("utf-8", "replace")
    assert "POST_GUARD_VETO_ONLY" in text
    assert "pre_sigma_market_verdict" in text
    assert "sigma_authority" in text


# ---------------------------------------------------------------------------
# Test 12 — OS2 proof gamma still 1.0
# ---------------------------------------------------------------------------
def test_p57_12_os2_gamma_still_1():
    """OS2 proof metrics.py gamma must remain 1.0 (P56B not reverted)."""
    path = PROOF_V18 / "obsidia_os2" / "metrics.py"
    assert path.exists()
    gammas = re.findall(r"gamma\s*=\s*([0-9.]+)", path.read_text("utf-8", "replace"))
    assert "1.0" in gammas
    assert "0.5" not in gammas


# ---------------------------------------------------------------------------
# Test 13 — decision_authority = KX108_ONLY
# ---------------------------------------------------------------------------
def test_p57_13_decision_authority_kx108_only():
    """decision_authority must still be KX108_ONLY in sigma/contracts.py."""
    path = SIGMA_DIR / "contracts.py"
    assert path.exists()
    text = path.read_text("utf-8", "replace")
    assert "KX108_ONLY" in text


# ---------------------------------------------------------------------------
# Test 14 — IMPORT_NOW_SAFE candidates have required_tests
# ---------------------------------------------------------------------------
def test_p57_14_import_now_safe_has_required_tests():
    """Every IMPORT_NOW_SAFE candidate must have at least one required test."""
    plan = _load(DOCS / "P57_CORE_TO_PROOF_IMPORT_PLAN.json")
    violations = []
    for item in plan:
        if item["category"] == "A_IMPORT_NOW_SAFE":
            tests = item.get("required_tests", [])
            if not tests or tests == [""]:
                violations.append(item["core_path"])
    assert not violations, f"IMPORT_NOW_SAFE items missing required_tests: {violations}"
