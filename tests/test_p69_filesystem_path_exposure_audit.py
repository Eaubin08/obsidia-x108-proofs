"""
tests/test_p69_filesystem_path_exposure_audit.py

P69 validation suite — 51 tests.
Vérifie : JSON audit, modèle filesystem, matrix, buckets, findings, flags sécurité, régressions P56E→P68.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P69_JSON = os.path.join(ROOT, "docs", "core_import", "P69_FILESYSTEM_PATH_EXPOSURE_AUDIT.json")
AUDIT_MW = os.path.join(ROOT, "apps", "obsidia_api", "audit_middleware.py")
WORLD_BUS = os.path.join(ROOT, "periphery", "world_calls", "world_action_bus.py")
GEN_MANIFEST = os.path.join(ROOT, "scripts", "generate_recursive_manifest.py")
SOURCE_RUNTIME_PY = os.path.join(ROOT, "apps", "obsidia_api", "routes", "source_runtime_status.py")


@pytest.fixture(scope="module")
def p69():
    with open(P69_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def matrix(p69):
    return p69["filesystem_matrix"]


# ---------------------------------------------------------------------------
# Section 1 — JSON de base (5 tests)
# ---------------------------------------------------------------------------

def test_p69_json_exists():
    assert os.path.isfile(P69_JSON)


def test_p69_json_status(p69):
    assert p69["status"] == "P69_FILESYSTEM_PATH_EXPOSURE_AUDIT_READY"


def test_p69_json_mode(p69):
    assert p69["mode"] == "AUDIT_ONLY"


def test_p69_source_patch_false(p69):
    assert p69["source_patch_applied"] is False


def test_p69_files_imported_zero(p69):
    assert p69["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 — Modèle filesystem (10 tests)
# ---------------------------------------------------------------------------

def test_filesystem_model_canonical_memory_write(p69):
    assert "canonical_memory_write" in p69["filesystem_model"]


def test_filesystem_model_local_audit_write(p69):
    assert "local_audit_write" in p69["filesystem_model"]


def test_filesystem_model_artifact_write(p69):
    assert "artifact_write" in p69["filesystem_model"]


def test_filesystem_model_report_write(p69):
    assert "report_write" in p69["filesystem_model"]


def test_filesystem_model_manifest_write(p69):
    assert "manifest_write" in p69["filesystem_model"]


def test_filesystem_model_dangerous_path_write(p69):
    assert "dangerous_path_write" in p69["filesystem_model"]


def test_filesystem_model_local_file_read(p69):
    assert "local_file_read" in p69["filesystem_model"]


def test_filesystem_model_source_pack_read(p69):
    assert "source_pack_read" in p69["filesystem_model"]


def test_filesystem_model_path_exposure(p69):
    assert "path_exposure" in p69["filesystem_model"]


def test_filesystem_model_source_excerpt_exposure(p69):
    assert "source_excerpt_exposure" in p69["filesystem_model"]


# ---------------------------------------------------------------------------
# Section 3 — Filesystem matrix (4 tests)
# ---------------------------------------------------------------------------

def test_filesystem_matrix_nonempty(matrix):
    assert len(matrix) > 0


def test_filesystem_matrix_required_fields(matrix):
    required = {"path", "surface", "category", "risk_level", "reason", "next_action",
                "writes_local_audit", "writes_canonical_memory", "reads_source_pack"}
    for e in matrix:
        for f in required:
            assert f in e, f"Missing field {f} in entry {e.get('path')}"


def test_category_counts_nonempty(p69):
    assert len(p69["category_counts"]) > 0


def test_category_local_audit_write_present(p69):
    assert p69["category_counts"].get("LOCAL_AUDIT_WRITE", 0) > 0


# ---------------------------------------------------------------------------
# Section 4 — Buckets (7 tests)
# ---------------------------------------------------------------------------

def test_local_audit_write_bucket_exists(p69):
    assert isinstance(p69["local_audit_write"], list)
    assert len(p69["local_audit_write"]) > 0


def test_artifact_write_bucket_exists(p69):
    assert isinstance(p69["artifact_write"], list)
    assert len(p69["artifact_write"]) > 0


def test_report_write_bucket_exists(p69):
    assert isinstance(p69["report_write"], list)
    assert len(p69["report_write"]) > 0


def test_manifest_write_bucket_exists(p69):
    assert isinstance(p69["manifest_write"], list)
    assert len(p69["manifest_write"]) > 0


def test_path_exposure_review_bucket_exists(p69):
    assert isinstance(p69["path_exposure_review"], list)


def test_source_excerpt_review_bucket_exists(p69):
    assert isinstance(p69["source_excerpt_review"], list)
    assert len(p69["source_excerpt_review"]) > 0


def test_absolute_path_exposure_bucket_exists(p69):
    assert isinstance(p69["absolute_path_exposure"], list)
    assert len(p69["absolute_path_exposure"]) > 0


# ---------------------------------------------------------------------------
# Section 5 — Focus findings (4 tests)
# ---------------------------------------------------------------------------

def test_focus_findings_nonempty(p69):
    assert len(p69["focus_findings"]) >= 5


def test_focus_findings_world_action_bus(p69):
    bus = [f for f in p69["focus_findings"] if "world_action_bus" in f["file"]]
    assert len(bus) >= 1


def test_focus_findings_absolute_path_exposure(p69):
    abs_path = [f for f in p69["focus_findings"] if f["category"] == "ABSOLUTE_PATH_EXPOSURE"]
    assert len(abs_path) >= 2


def test_preexisting_manifest_drift_documented(p69):
    paths = [e["file"] for e in p69["preexisting_manifest_drift"]]
    assert any("world_action_bus" in p for p in paths)
    assert any("PROOFKIT_REPORT" in p for p in paths)


# ---------------------------------------------------------------------------
# Section 6 — Flags sécurité P69 (10 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p69):
    assert p69["runtime_modified"] is False


def test_sigma_modified_false(p69):
    assert p69["sigma_modified"] is False


def test_routes_modified_false(p69):
    assert p69["routes_modified"] is False


def test_srl_modified_false(p69):
    assert p69["srl_modified"] is False


def test_act_enabled_false(p69):
    assert p69["act_enabled"] is False


def test_memory_write_enabled_false(p69):
    assert p69["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p69):
    assert p69["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p69):
    assert p69["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p69):
    assert p69["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p69):
    assert p69["x108_merge_enabled"] is False


# ---------------------------------------------------------------------------
# Section 7 — Vérifications source (3 tests)
# ---------------------------------------------------------------------------

def test_audit_middleware_writes_audit_logs():
    content = open(AUDIT_MW, encoding="utf-8").read()
    assert "audit_logs" in content
    assert "memory_write" in content


def test_world_action_bus_dry_run():
    content = open(WORLD_BUS, encoding="utf-8").read()
    assert "world_action_bus.jsonl" in content
    assert "dry_run" in content.lower() or "dry_run_only" in content


def test_generate_manifest_writes_to_root():
    content = open(GEN_MANIFEST, encoding="utf-8").read()
    assert "MANIFEST_SHA256_RECURSIVE.json" in content
    assert "json.dump" in content


# ---------------------------------------------------------------------------
# Section 8 — Régressions P56E→P68 (13 tests)
# ---------------------------------------------------------------------------

def _run(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header", "-k", "not regression"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return result.returncode == 0


def test_p56e_regression():
    assert _run("tests/test_p56e_post_patch_metric_reaudit.py")


def test_p57_regression():
    assert _run("tests/test_p57_core_machinery_runtime_binding_audit.py")


def test_p58_regression():
    assert _run("tests/test_p58_core_import_triage_operational_path_aware.py")


def test_p59_regression():
    assert _run("tests/test_p59_safe_batch_1_import.py")


def test_p60_regression():
    assert _run("tests/test_p60_test_batch_2_import.py")


def test_p61_regression():
    assert _run("tests/test_p61_bus_adapter_batch.py")


def test_p62_regression():
    assert _run("tests/test_p62_manual_review_deferred.py")


def test_p63_regression():
    assert _run("tests/test_p63_global_fusion_reality_audit.py")


def test_p64_regression():
    assert _run("tests/test_p64_fusion_continuity_ledger.py")


def test_p65_regression():
    assert _run("tests/test_p65_os_adapters_unlock_bus_registry.py")


def test_p66_regression():
    assert _run("tests/test_p66_srl_readonly_memory_layer.py")


def test_p67_regression():
    assert _run("tests/test_p67_boundary_semantic_split_audit.py")


def test_p68_regression():
    assert _run("tests/test_p68_api_auth_route_exposure_audit.py")


# ---------------------------------------------------------------------------
# Section 9 — verify_all et forbidden (2 tests)
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
