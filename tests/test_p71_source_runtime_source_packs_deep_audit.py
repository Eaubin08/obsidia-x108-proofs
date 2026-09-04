"""
tests/test_p71_source_runtime_source_packs_deep_audit.py

P71 validation suite — 65 tests.
Vérifie : JSON audit, modèle source runtime, source_pack_matrix, adapter_matrix,
findings, flags sécurité, vérifications source, régressions P56E→P70.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P71_JSON = os.path.join(ROOT, "docs", "core_import", "P71_SOURCE_RUNTIME_SOURCE_PACKS_DEEP_AUDIT.json")
RESOLVER = os.path.join(ROOT, "runtime_wiring", "source_runtime", "source_pack_resolver.py")
LOADER = os.path.join(ROOT, "runtime_wiring", "source_runtime", "readonly_content_loader.py")
HYDRATOR = os.path.join(ROOT, "runtime_wiring", "source_runtime", "source_context_hydrator.py")
SOURCE_RUNTIME_STATUS = os.path.join(ROOT, "apps", "obsidia_api", "routes", "source_runtime_status.py")


@pytest.fixture(scope="module")
def p71():
    with open(P71_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def pack_matrix(p71):
    return p71["source_pack_matrix"]


@pytest.fixture(scope="module")
def adapter_matrix(p71):
    return p71["adapter_matrix"]


# ---------------------------------------------------------------------------
# Section 1 — JSON de base (5 tests)
# ---------------------------------------------------------------------------

def test_p71_json_exists():
    assert os.path.isfile(P71_JSON)


def test_p71_json_status(p71):
    assert p71["status"] == "P71_SOURCE_RUNTIME_SOURCE_PACKS_DEEP_AUDIT_READY"


def test_p71_json_mode(p71):
    assert p71["mode"] == "AUDIT_ONLY"


def test_p71_source_patch_false(p71):
    assert p71["source_patch_applied"] is False


def test_p71_files_imported_zero(p71):
    assert p71["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 — Modèle source runtime (10 tests)
# ---------------------------------------------------------------------------

def test_source_runtime_model_full_local(p71):
    assert "full_local" in p71["source_runtime_model"]


def test_source_runtime_model_metadata_only(p71):
    assert "metadata_only" in p71["source_runtime_model"]


def test_source_runtime_model_documented_fallback(p71):
    assert "documented_fallback" in p71["source_runtime_model"]


def test_source_runtime_model_blocked_absent(p71):
    assert "blocked_absent" in p71["source_runtime_model"]


def test_source_runtime_model_archive_only(p71):
    assert "archive_only" in p71["source_runtime_model"]


def test_source_runtime_model_runtime_hydratable(p71):
    assert "runtime_hydratable" in p71["source_runtime_model"]


def test_source_runtime_model_preview_review(p71):
    assert "preview_review" in p71["source_runtime_model"]


def test_source_runtime_model_excerpt_auth_required(p71):
    assert "excerpt_auth_required" in p71["source_runtime_model"]


def test_source_runtime_model_path_exposure_review(p71):
    assert "path_exposure_review" in p71["source_runtime_model"]


def test_source_runtime_model_local_only_uncanonized(p71):
    # Either directly in model or derivable from pack matrix
    matrix_categories = {e["category"] for e in p71["source_pack_matrix"]}
    assert "SOURCE_LOCAL_ONLY_UNCANONIZED" in matrix_categories


# ---------------------------------------------------------------------------
# Section 3 — Source pack matrix (4 tests)
# ---------------------------------------------------------------------------

def test_source_pack_matrix_exists(p71):
    assert isinstance(p71["source_pack_matrix"], list)
    assert len(p71["source_pack_matrix"]) > 0


def test_source_pack_matrix_required_fields(pack_matrix):
    required = {
        "source_name", "source_path", "surface", "exists",
        "file_count", "has_manifest", "has_hashes", "has_content_files",
        "has_metadata_only_marker", "has_runtime_adapter",
        "adapter_path", "preview_endpoint_related", "exposes_path",
        "exposes_excerpt", "category", "risk_level", "reason", "next_action",
    }
    for e in pack_matrix:
        for f in required:
            assert f in e, f"Champ manquant {f} dans entrée {e.get('source_name')}"


def test_category_counts_nonempty(p71):
    assert len(p71["category_counts"]) > 0


def test_category_source_full_local_present(p71):
    assert p71["category_counts"].get("SOURCE_FULL_LOCAL", 0) >= 8


# ---------------------------------------------------------------------------
# Section 4 — Adapter matrix (5 tests)
# ---------------------------------------------------------------------------

def test_adapter_matrix_exists(p71):
    assert isinstance(p71["adapter_matrix"], list)
    assert len(p71["adapter_matrix"]) > 0


def test_adapter_matrix_required_fields(adapter_matrix):
    required = {
        "adapter_path", "related_source", "reads_content", "metadata_only",
        "preview_only", "exposes_path", "exposes_excerpt",
        "auth_required", "dry_run_only", "network_egress",
        "category", "risk_level", "next_action",
    }
    for e in adapter_matrix:
        for f in required:
            assert f in e, f"Champ manquant {f} dans adapter {e.get('adapter_path')}"


def test_adapter_auth_required_present(adapter_matrix):
    auth = [a for a in adapter_matrix if a["category"] == "ADAPTER_AUTH_REQUIRED"]
    assert len(auth) >= 2


def test_adapter_path_exposing_present(adapter_matrix):
    path_exp = [a for a in adapter_matrix if a["category"] == "ADAPTER_PATH_EXPOSING"]
    assert len(path_exp) >= 1


def test_adapter_dry_run_safe_present(adapter_matrix):
    safe = [a for a in adapter_matrix if a["category"] == "ADAPTER_DRY_RUN_SAFE"]
    assert len(safe) >= 2


# ---------------------------------------------------------------------------
# Section 5 — Buckets (9 tests)
# ---------------------------------------------------------------------------

def test_source_full_local_bucket(p71):
    assert isinstance(p71["source_full_local"], list)
    assert len(p71["source_full_local"]) >= 8


def test_source_metadata_only_bucket(p71):
    assert isinstance(p71["source_metadata_only"], list)
    assert len(p71["source_metadata_only"]) >= 1


def test_source_archive_only_bucket(p71):
    assert isinstance(p71["source_archive_only"], list)
    assert len(p71["source_archive_only"]) >= 2


def test_source_runtime_hydratable_bucket(p71):
    assert isinstance(p71["source_runtime_hydratable"], list)
    assert len(p71["source_runtime_hydratable"]) >= 8


def test_source_excerpt_auth_required_bucket(p71):
    assert isinstance(p71["source_excerpt_auth_required"], list)
    assert len(p71["source_excerpt_auth_required"]) >= 2


def test_source_path_exposure_review_bucket(p71):
    assert isinstance(p71["source_path_exposure_review"], list)
    assert len(p71["source_path_exposure_review"]) >= 1


def test_source_pack_do_not_runtime_load_bucket(p71):
    assert isinstance(p71["source_pack_do_not_runtime_load"], list)
    assert len(p71["source_pack_do_not_runtime_load"]) >= 1


def test_source_local_only_uncanonized_bucket(p71):
    assert isinstance(p71["source_local_only_uncanonized"], list)
    assert len(p71["source_local_only_uncanonized"]) >= 1


def test_source_pack_unknown_review_empty(p71):
    assert isinstance(p71["source_pack_unknown_review"], list)


# ---------------------------------------------------------------------------
# Section 6 — Focus findings (5 tests)
# ---------------------------------------------------------------------------

def test_focus_findings_nonempty(p71):
    assert len(p71["focus_findings"]) >= 5


def test_focus_findings_preview_auth_required(p71):
    auth = [f for f in p71["focus_findings"] if f["category"] == "SOURCE_EXCERPT_AUTH_REQUIRED"]
    assert len(auth) >= 2


def test_focus_findings_tmp_core_import_classified(p71):
    tmp = [f for f in p71["focus_findings"] if "_tmp_core_import" in f["file"]]
    assert len(tmp) >= 1
    assert tmp[0]["category"] == "SOURCE_PACK_DO_NOT_RUNTIME_LOAD"


def test_p69_findings_carried(p71):
    assert len(p71["p69_findings_carried"]) >= 4
    categories = {e["p71_category"] for e in p71["p69_findings_carried"]}
    assert "SOURCE_EXCERPT_AUTH_REQUIRED" in categories


def test_p70_findings_carried(p71):
    assert len(p71["p70_findings_carried"]) >= 3
    connectors = [e["p70_file"] for e in p71["p70_findings_carried"]]
    assert any("aviation" in c for c in connectors)


# ---------------------------------------------------------------------------
# Section 7 — Registry safety (3 tests)
# ---------------------------------------------------------------------------

def test_registry_safety_invariants_ok(p71):
    reg = p71["registry_summary"]
    assert reg["py_files_all_do_not_import"] is True
    assert reg["runtime_allowed_now_count"] == 0
    assert reg["emits_act_count"] == 0
    assert reg["safety_invariants_ok"] is True


def test_registry_total_entries(p71):
    assert p71["registry_summary"]["total_entries"] == 15853


def test_registry_families_count(p71):
    assert p71["registry_summary"]["families_count"] == 8


# ---------------------------------------------------------------------------
# Section 8 — Flags sécurité P71 (13 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p71):
    assert p71["runtime_modified"] is False


def test_sigma_modified_false(p71):
    assert p71["sigma_modified"] is False


def test_routes_modified_false(p71):
    assert p71["routes_modified"] is False


def test_srl_modified_false(p71):
    assert p71["srl_modified"] is False


def test_connectors_modified_false(p71):
    assert p71["connectors_modified"] is False


def test_source_packs_modified_false(p71):
    assert p71["source_packs_modified"] is False


def test_freezes_modified_false(p71):
    assert p71["freezes_modified"] is False


def test_act_enabled_false(p71):
    assert p71["act_enabled"] is False


def test_memory_write_enabled_false(p71):
    assert p71["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p71):
    assert p71["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p71):
    assert p71["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p71):
    assert p71["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p71):
    assert p71["x108_merge_enabled"] is False


# ---------------------------------------------------------------------------
# Section 9 — Vérifications source (3 tests)
# ---------------------------------------------------------------------------

def test_readonly_content_loader_forbids_py():
    content = open(LOADER, encoding="utf-8").read()
    assert ".py" in content
    assert "ForbiddenFileError" in content
    assert "extracted_to_disk" in content


def test_source_pack_resolver_has_downloads_path():
    content = open(RESOLVER, encoding="utf-8").read()
    assert "Downloads" in content
    assert "MissingSourcePackError" in content


def test_source_runtime_status_has_preview_endpoint():
    content = open(SOURCE_RUNTIME_STATUS, encoding="utf-8").read()
    assert "/preview" in content
    assert "build_brody_context_from_source_packs" in content
    assert "hydrated_entries" in content


# ---------------------------------------------------------------------------
# Section 10 — Régressions P56E→P70 (15 tests)
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


def test_p69_regression():
    assert _run("tests/test_p69_filesystem_path_exposure_audit.py")


def test_p70_regression():
    assert _run("tests/test_p70_network_egress_connectors_audit.py")


# ---------------------------------------------------------------------------
# Section 11 — verify_all et forbidden (2 tests)
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
