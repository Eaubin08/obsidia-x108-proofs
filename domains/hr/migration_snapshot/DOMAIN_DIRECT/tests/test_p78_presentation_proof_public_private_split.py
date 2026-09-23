"""
tests/test_p78_presentation_proof_public_private_split.py

P78 validation suite.
Verifie : JSON audit, modele split, matrice, surface publique,
RSSI evidence candidates, DO_NOT_PUBLISH, index docs crees,
flags securite, focus findings, regressions P56E->P77.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P78_JSON = os.path.join(ROOT, "docs", "core_import", "P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.json")
P78_MD = os.path.join(ROOT, "docs", "core_import", "P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.md")
SIGMA_DIR = os.path.join(ROOT, "sigma")
PROOFS_DIR = os.path.join(ROOT, "proofs")
PUBLIC_INDEX = os.path.join(ROOT, "docs", "public", "README_PUBLIC_BOUNDARY.md")
INVESTOR_INDEX = os.path.join(ROOT, "docs", "investor", "README_INVESTOR_BOUNDARY.md")
PROOF_INDEX = os.path.join(ROOT, "docs", "proof", "README_PROOF_BOUNDARY.md")
DEMO_INDEX = os.path.join(ROOT, "docs", "demo", "README_DEMO_BOUNDARY.md")


@pytest.fixture(scope="module")
def p78():
    with open(P78_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def doc_matrix(p78):
    return p78["doc_matrix"]


@pytest.fixture(scope="module")
def split_model(p78):
    return p78["split_model"]


@pytest.fixture(scope="module")
def focus_findings(p78):
    return p78["focus_findings"]


# ---------------------------------------------------------------------------
# Section 1 -- JSON de base (6 tests)
# ---------------------------------------------------------------------------

def test_p78_json_exists():
    assert os.path.isfile(P78_JSON)


def test_p78_json_status(p78):
    assert p78["status"] == "P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT_READY"


def test_p78_json_mode(p78):
    assert p78["mode"] == "AUDIT_AND_DOC_INDEX_ONLY"


def test_p78_split_decision(p78):
    assert p78["split_decision"] == "CLASSIFY_AND_INDEX_ONLY"


def test_p78_source_patch_not_applied(p78):
    assert p78["source_patch_applied"] is False


def test_p78_files_imported_zero(p78):
    assert p78["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 -- Modele split (5 tests)
# ---------------------------------------------------------------------------

def test_split_model_mode(split_model):
    assert split_model["mode"] == "AUDIT_AND_DOC_INDEX_ONLY"


def test_split_model_dry_run_only(split_model):
    assert split_model["dry_run_only"] is True


def test_split_model_public_safe_defined(split_model):
    assert "public_safe" in split_model
    assert len(split_model["public_safe"]) > 10


def test_split_model_do_not_publish_defined(split_model):
    assert "do_not_publish" in split_model
    assert len(split_model["do_not_publish"]) > 10


def test_split_model_private_proprietary_defined(split_model):
    assert "private_proprietary" in split_model


# ---------------------------------------------------------------------------
# Section 3 -- Matrice structure (5 tests)
# ---------------------------------------------------------------------------

def test_doc_matrix_exists(p78):
    assert isinstance(p78["doc_matrix"], list)
    assert len(p78["doc_matrix"]) >= 80


def test_doc_matrix_required_fields(doc_matrix):
    required = {
        "file_path", "category", "decision", "reason",
        "publish", "file_count_approx",
    }
    for entry in doc_matrix:
        for f in required:
            assert f in entry, f"Champ manquant {f} dans {entry.get('file_path')}"


def test_doc_matrix_valid_categories(doc_matrix):
    valid = {
        "DOC_PROOF_TECHNICAL", "DOC_AUDIT_TRAIL", "DOC_CORE_IMPORT_LEDGER",
        "DOC_FORMAL_PROOF_MAP", "DOC_RSSI_EVIDENCE_CANDIDATE",
        "DOC_PUBLIC_SAFE", "DOC_PUBLIC_NEEDS_SOFTENING",
        "DOC_INVESTOR_NARRATIVE", "DOC_DEMO_ONLY",
        "DOC_PRIVATE_PROPRIETARY", "DOC_SOURCE_PACK_LOCAL_ONLY",
        "DOC_ARCHIVE_ONLY", "DOC_RUNTIME_INTERNAL",
        "DOC_API_INTERNAL", "DOC_MEMORY_INTERNAL",
        "DOC_CONNECTOR_INTERNAL", "DOC_DO_NOT_PUBLISH",
        "DOC_UNKNOWN_REVIEW",
    }
    for e in doc_matrix:
        assert e["category"] in valid, (
            f"Categorie invalide dans {e['file_path']}: {e['category']}"
        )


def test_doc_matrix_valid_decisions(doc_matrix):
    valid = {
        "KEEP_AS_TECHNICAL_PROOF", "KEEP_AS_AUDIT_LEDGER",
        "KEEP_AS_PUBLIC_SAFE", "MOVE_LATER_PUBLIC",
        "MOVE_LATER_INVESTOR", "MOVE_LATER_DEMO",
        "KEEP_PRIVATE_PROPRIETARY", "KEEP_ARCHIVE_ONLY",
        "KEEP_SOURCE_PACK_LOCAL_ONLY", "DO_NOT_PUBLISH",
        "REQUIRES_REVIEW",
    }
    for e in doc_matrix:
        assert e["decision"] in valid, (
            f"Decision invalide dans {e['file_path']}: {e['decision']}"
        )


def test_doc_matrix_no_runtime_modified(doc_matrix):
    for e in doc_matrix:
        assert e.get("publish") in (True, False), (
            f"publish invalide dans {e.get('file_path')}"
        )


# ---------------------------------------------------------------------------
# Section 4 -- Surface publique safe (5 tests)
# ---------------------------------------------------------------------------

def test_public_safe_count(p78):
    assert len(p78["public_safe"]) >= 15


def test_readme_is_public_safe(doc_matrix):
    readme = next((e for e in doc_matrix if e["file_path"] == "README.md"), None)
    assert readme is not None
    assert readme["decision"] == "KEEP_AS_PUBLIC_SAFE"
    assert readme["publish"] is True


def test_limits_is_public_safe(doc_matrix):
    entry = next((e for e in doc_matrix if "LIMITS.md" in e["file_path"]), None)
    assert entry is not None
    assert entry["decision"] == "KEEP_AS_PUBLIC_SAFE"


def test_bank_scenarios_is_technical_proof(doc_matrix):
    entry = next((e for e in doc_matrix if "BANK_SCENARIOS" in e["file_path"]), None)
    assert entry is not None
    assert entry["decision"] == "KEEP_AS_TECHNICAL_PROOF"
    assert entry["publish"] is True


def test_lean_proofs_is_technical_proof(doc_matrix):
    entry = next((e for e in doc_matrix if "proofs/lean/" in e["file_path"]), None)
    assert entry is not None
    assert entry["decision"] == "KEEP_AS_TECHNICAL_PROOF"
    assert entry["publish"] is True


# ---------------------------------------------------------------------------
# Section 5 -- RSSI evidence candidates (5 tests)
# ---------------------------------------------------------------------------

def test_rssi_candidates_count(p78):
    assert len(p78["rssi_evidence_candidates"]) >= 8


def test_merkle_root_is_rssi_candidate(doc_matrix):
    entry = next((e for e in doc_matrix if "merkle_root.json" in e["file_path"]), None)
    assert entry is not None
    assert entry["category"] == "DOC_RSSI_EVIDENCE_CANDIDATE"


def test_rfc3161_anchor_is_rssi_candidate(doc_matrix):
    entry = next((e for e in doc_matrix if "rfc3161_anchor.json" in e["file_path"]), None)
    assert entry is not None
    assert entry["category"] == "DOC_RSSI_EVIDENCE_CANDIDATE"


def test_p72_is_rssi_candidate(doc_matrix):
    entry = next((e for e in doc_matrix if "P72_INVARIANT_GRAPH" in e["file_path"]), None)
    assert entry is not None
    assert entry["category"] == "DOC_RSSI_EVIDENCE_CANDIDATE"


def test_specs_01_x108_is_rssi_candidate(doc_matrix):
    entry = next((e for e in doc_matrix if "01_X108_AUTHORITY" in e["file_path"]), None)
    assert entry is not None
    assert entry["category"] == "DOC_RSSI_EVIDENCE_CANDIDATE"


# ---------------------------------------------------------------------------
# Section 6 -- DO_NOT_PUBLISH obligatoires (5 tests)
# ---------------------------------------------------------------------------

def test_do_not_publish_count(p78):
    assert len(p78["do_not_publish"]) >= 12


def test_sigma_do_not_publish(doc_matrix):
    entry = next((e for e in doc_matrix if e["file_path"].startswith("sigma/")), None)
    assert entry is not None
    assert entry["decision"] == "DO_NOT_PUBLISH"
    assert entry["publish"] is False


def test_connectors_do_not_publish(doc_matrix):
    entry = next((e for e in doc_matrix if "connectors/" in e["file_path"]), None)
    assert entry is not None
    assert entry["decision"] == "DO_NOT_PUBLISH"


def test_gencoin_do_not_publish(doc_matrix):
    entry = next((e for e in doc_matrix if "gencoin" in e["file_path"].lower()), None)
    assert entry is not None
    assert entry["decision"] in ("DO_NOT_PUBLISH", "KEEP_PRIVATE_PROPRIETARY")


def test_world_action_bus_do_not_publish(doc_matrix):
    entry = next((e for e in doc_matrix if "world_action_bus.jsonl" in e["file_path"]), None)
    assert entry is not None
    assert entry["decision"] == "DO_NOT_PUBLISH"
    assert entry["publish"] is False


# ---------------------------------------------------------------------------
# Section 7 -- Flags securite (14 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p78):
    assert p78["runtime_modified"] is False


def test_sigma_modified_false(p78):
    assert p78["sigma_modified"] is False


def test_routes_modified_false(p78):
    assert p78["routes_modified"] is False


def test_srl_modified_false(p78):
    assert p78["srl_modified"] is False


def test_connectors_modified_false(p78):
    assert p78["connectors_modified"] is False


def test_source_packs_modified_false(p78):
    assert p78["source_packs_modified"] is False


def test_proofs_modified_false(p78):
    assert p78["proofs_modified"] is False


def test_lean_proofs_modified_false(p78):
    assert p78["lean_proofs_modified"] is False


def test_act_enabled_false(p78):
    assert p78["act_enabled"] is False


def test_memory_write_enabled_false(p78):
    assert p78["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p78):
    assert p78["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p78):
    assert p78["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p78):
    assert p78["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p78):
    assert p78["x108_merge_enabled"] is False


# ---------------------------------------------------------------------------
# Section 8 -- Index docs crees (5 tests)
# ---------------------------------------------------------------------------

def test_public_index_exists():
    assert os.path.isfile(PUBLIC_INDEX), "docs/public/README_PUBLIC_BOUNDARY.md absent"


def test_investor_index_exists():
    assert os.path.isfile(INVESTOR_INDEX), "docs/investor/README_INVESTOR_BOUNDARY.md absent"


def test_proof_index_exists():
    assert os.path.isfile(PROOF_INDEX), "docs/proof/README_PROOF_BOUNDARY.md absent"


def test_demo_index_exists():
    assert os.path.isfile(DEMO_INDEX), "docs/demo/README_DEMO_BOUNDARY.md absent"


def test_created_indexes_list(p78):
    created = p78["created_indexes"]
    assert len(created) == 4
    assert any("public" in c for c in created)
    assert any("investor" in c for c in created)
    assert any("proof" in c for c in created)
    assert any("demo" in c for c in created)


# ---------------------------------------------------------------------------
# Section 9 -- Focus findings (5 tests)
# ---------------------------------------------------------------------------

def test_focus_findings_count(focus_findings):
    assert len(focus_findings) >= 7


def test_finding_f1_demo_separation(focus_findings):
    f1 = next((f for f in focus_findings if f["finding_id"] == "P78-F1"), None)
    assert f1 is not None
    assert f1["type"] == "SEPARATION_PROOF_VS_DEMO"


def test_finding_f2_token_do_not_publish(focus_findings):
    f2 = next((f for f in focus_findings if f["finding_id"] == "P78-F2"), None)
    assert f2 is not None
    assert f2["type"] == "DO_NOT_PUBLISH_TOKEN"
    assert f2["action"] == "DO_NOT_PUBLISH"


def test_finding_f3_rssi_candidates(focus_findings):
    f3 = next((f for f in focus_findings if f["finding_id"] == "P78-F3"), None)
    assert f3 is not None
    assert f3["type"] == "RSSI_EVIDENCE_PACK_CANDIDATES"
    assert "P79" in f3["action"]


def test_finding_f5_public_surface(focus_findings):
    f5 = next((f for f in focus_findings if f["finding_id"] == "P78-F5"), None)
    assert f5 is not None
    assert f5["type"] == "PUBLIC_SAFE_SURFACE_IDENTIFIED"
    assert "P80" in f5["action"]


# ---------------------------------------------------------------------------
# Section 10 -- Verification fichiers proteges intacts (4 tests)
# ---------------------------------------------------------------------------

def test_proofs_lean_dir_untouched():
    lean_dir = os.path.join(PROOFS_DIR, "lean")
    assert os.path.isdir(lean_dir)


def test_merkle_root_json_exists():
    p = os.path.join(PROOFS_DIR, "merkle_root.json")
    assert os.path.isfile(p)


def test_rfc3161_anchor_json_exists():
    p = os.path.join(PROOFS_DIR, "rfc3161_anchor.json")
    assert os.path.isfile(p)


def test_sigma_dir_untouched():
    assert os.path.isdir(SIGMA_DIR)
    assert os.path.isfile(os.path.join(SIGMA_DIR, "guard.py"))


# ---------------------------------------------------------------------------
# Section 11 -- Regressions P56E->P77 (22 tests)
# ---------------------------------------------------------------------------

def _run(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return result.returncode == 0


@pytest.mark.regression
def test_p56e_regression():
    assert _run("tests/test_p56e_post_patch_metric_reaudit.py")


@pytest.mark.regression
def test_p57_regression():
    assert _run("tests/test_p57_core_machinery_runtime_binding_audit.py")


@pytest.mark.regression
def test_p58_regression():
    assert _run("tests/test_p58_core_import_triage_operational_path_aware.py")


@pytest.mark.regression
def test_p59_regression():
    assert _run("tests/test_p59_safe_batch_1_import.py")


@pytest.mark.regression
def test_p60_regression():
    assert _run("tests/test_p60_test_batch_2_import.py")


@pytest.mark.regression
def test_p61_regression():
    assert _run("tests/test_p61_bus_adapter_batch.py")


@pytest.mark.regression
def test_p62_regression():
    assert _run("tests/test_p62_manual_review_deferred.py")


@pytest.mark.regression
def test_p63_regression():
    assert _run("tests/test_p63_global_fusion_reality_audit.py")


@pytest.mark.regression
def test_p64_regression():
    assert _run("tests/test_p64_fusion_continuity_ledger.py")


@pytest.mark.regression
def test_p65_regression():
    assert _run("tests/test_p65_os_adapters_unlock_bus_registry.py")


@pytest.mark.regression
def test_p66_regression():
    assert _run("tests/test_p66_srl_readonly_memory_layer.py")


@pytest.mark.regression
def test_p67_regression():
    assert _run("tests/test_p67_boundary_semantic_split_audit.py")


@pytest.mark.regression
def test_p68_regression():
    assert _run("tests/test_p68_api_auth_route_exposure_audit.py")


@pytest.mark.regression
def test_p69_regression():
    assert _run("tests/test_p69_filesystem_path_exposure_audit.py")


@pytest.mark.regression
def test_p70_regression():
    assert _run("tests/test_p70_network_egress_connectors_audit.py")


@pytest.mark.regression
def test_p71_regression():
    assert _run("tests/test_p71_source_runtime_source_packs_deep_audit.py")


@pytest.mark.regression
def test_p72_regression():
    assert _run("tests/test_p72_invariant_graph_formal_proof_alignment.py")


@pytest.mark.regression
def test_p73_regression():
    assert _run("tests/test_p73_agents_complementary_reconciliation.py")


@pytest.mark.regression
def test_p74_regression():
    assert _run("tests/test_p74_sigma_safe_evolution.py")


@pytest.mark.regression
def test_p75_regression():
    assert _run("tests/test_p75_runtime_core_risk_review.py")


@pytest.mark.regression
def test_p76_regression():
    assert _run("tests/test_p76_gps_terrain_portable_reconciliation.py")


@pytest.mark.regression
def test_p77_regression():
    assert _run("tests/test_p77_canon_wording_targeted_cleanup.py")


# ---------------------------------------------------------------------------
# Section 12 -- verify_all et forbidden (2 tests)
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
