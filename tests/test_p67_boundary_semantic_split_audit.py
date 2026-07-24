"""
tests/test_p67_boundary_semantic_split_audit.py

P67 validation suite — 48 tests.
Vérifie : JSON audit, modèle boundary, surfaces, flags sécurité, régressions P56E→P66.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P67_JSON = os.path.join(ROOT, "docs", "core_import", "P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT.json")


@pytest.fixture(scope="module")
def p67_data():
    with open(P67_JSON, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Section 1 — JSON audit de base (5 tests)
# ---------------------------------------------------------------------------

def test_p67_json_exists():
    assert os.path.isfile(P67_JSON)


def test_p67_json_status(p67_data):
    assert p67_data["status"] == "P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT_READY"


def test_p67_json_mode(p67_data):
    assert p67_data["mode"] == "AUDIT_ONLY"


def test_p67_source_patch_false(p67_data):
    assert p67_data["source_patch_applied"] is False


def test_p67_files_imported_zero(p67_data):
    assert p67_data["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 — Modèle boundary (10 tests)
# ---------------------------------------------------------------------------

def test_boundary_model_decision_readonly(p67_data):
    assert "decision_readonly" in p67_data["boundary_model"]


def test_boundary_model_act_readonly(p67_data):
    assert "act_readonly" in p67_data["boundary_model"]


def test_boundary_model_dry_run_only(p67_data):
    assert "dry_run_only" in p67_data["boundary_model"]


def test_boundary_model_filesystem_write(p67_data):
    assert "filesystem_write" in p67_data["boundary_model"]


def test_boundary_model_canonical_memory_write(p67_data):
    assert "canonical_memory_write" in p67_data["boundary_model"]


def test_boundary_model_graphiti_write(p67_data):
    assert "graphiti_write" in p67_data["boundary_model"]


def test_boundary_model_neo4j_write(p67_data):
    assert "neo4j_write" in p67_data["boundary_model"]


def test_boundary_model_network_egress(p67_data):
    assert "network_egress" in p67_data["boundary_model"]


def test_boundary_model_subprocess_execute(p67_data):
    assert "subprocess_execute" in p67_data["boundary_model"]


def test_boundary_model_path_exposure(p67_data):
    assert "path_exposure" in p67_data["boundary_model"]


# ---------------------------------------------------------------------------
# Section 3 — Boundary matrix et catégories (3 tests)
# ---------------------------------------------------------------------------

def test_boundary_matrix_nonempty(p67_data):
    assert len(p67_data["boundary_matrix"]) > 0


def test_category_counts_nonempty(p67_data):
    assert len(p67_data["category_counts"]) > 0


def test_category_decision_readonly_present(p67_data):
    assert p67_data["category_counts"].get("DECISION_READONLY", 0) > 0


# ---------------------------------------------------------------------------
# Section 4 — Surfaces scannées (5 tests)
# ---------------------------------------------------------------------------

def test_surface_sigma_scanned(p67_data):
    assert "sigma" in p67_data["scanned_surfaces"]


def test_surface_runtime_wiring_scanned(p67_data):
    assert "runtime_wiring" in p67_data["scanned_surfaces"]


def test_surface_apps_obsidia_api_scanned(p67_data):
    assert "apps/obsidia_api" in p67_data["scanned_surfaces"]


def test_surface_periphery_scanned(p67_data):
    assert "periphery" in p67_data["scanned_surfaces"]


def test_surface_connectors_or_noted(p67_data):
    assert "connectors" in p67_data["scanned_surfaces"]


# ---------------------------------------------------------------------------
# Section 5 — Listes bucketed (5 tests)
# ---------------------------------------------------------------------------

def test_safe_readonly_files_exists(p67_data):
    assert "safe_readonly_files" in p67_data
    assert isinstance(p67_data["safe_readonly_files"], list)


def test_dry_run_only_files_exists(p67_data):
    assert "dry_run_only_files" in p67_data
    assert isinstance(p67_data["dry_run_only_files"], list)


def test_unknown_requires_review_exists(p67_data):
    assert "unknown_requires_review" in p67_data
    assert isinstance(p67_data["unknown_requires_review"], list)


def test_preexisting_manifest_drift_documented(p67_data):
    paths = [e["file"] for e in p67_data["preexisting_manifest_drift"]]
    assert any("world_action_bus" in p for p in paths)
    assert any("PROOFKIT_REPORT" in p for p in paths)


def test_preexisting_test_debt_documented(p67_data):
    assert len(p67_data["preexisting_test_debt"]) > 0


# ---------------------------------------------------------------------------
# Section 6 — Flags sécurité P67 (10 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p67_data):
    assert p67_data["runtime_modified"] is False


def test_sigma_modified_false(p67_data):
    assert p67_data["sigma_modified"] is False


def test_routes_modified_false(p67_data):
    assert p67_data["routes_modified"] is False


def test_srl_modified_false(p67_data):
    assert p67_data["srl_modified"] is False


def test_act_enabled_false(p67_data):
    assert p67_data["act_enabled"] is False


def test_memory_write_enabled_false(p67_data):
    assert p67_data["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p67_data):
    assert p67_data["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p67_data):
    assert p67_data["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p67_data):
    assert p67_data["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p67_data):
    assert p67_data["x108_merge_enabled"] is False


# ---------------------------------------------------------------------------
# Section 7 — Régressions P56E→P66 (11 tests)
# ---------------------------------------------------------------------------

def _run_test_file(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    return result.returncode == 0


def test_p56e_regression():
    assert _run_test_file("tests/test_p56e_post_patch_metric_reaudit.py")


def test_p57_regression():
    assert _run_test_file("tests/test_p57_core_machinery_runtime_binding_audit.py")


def test_p58_regression():
    assert _run_test_file("tests/test_p58_core_import_triage_operational_path_aware.py")


def test_p59_regression():
    assert _run_test_file("tests/test_p59_safe_batch_1_import.py")


def test_p60_regression():
    assert _run_test_file("tests/test_p60_test_batch_2_import.py")


def test_p61_regression():
    assert _run_test_file("tests/test_p61_bus_adapter_batch.py")


def test_p62_regression():
    assert _run_test_file("tests/test_p62_manual_review_deferred.py")


def test_p63_regression():
    assert _run_test_file("tests/test_p63_global_fusion_reality_audit.py")


def test_p64_regression():
    assert _run_test_file("tests/test_p64_fusion_continuity_ledger.py")


def test_p65_regression():
    assert _run_test_file("tests/test_p65_os_adapters_unlock_bus_registry.py")


def test_p66_regression():
    assert _run_test_file("tests/test_p66_srl_readonly_memory_layer.py")


# ---------------------------------------------------------------------------
# Section 8 — verify_all et forbidden (2 tests)
# ---------------------------------------------------------------------------

def test_verify_all_pass():
    result = subprocess.run(
        [sys.executable, "proofs/verify_all.py"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert "PASS" in result.stdout


def test_forbidden_content_pass():
    result = subprocess.run(
        [sys.executable, "scripts/check_forbidden_content.py"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert "FORBIDDEN_CONTENT_PASS" in result.stdout
