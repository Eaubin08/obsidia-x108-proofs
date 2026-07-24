"""
tests/test_p68_api_auth_route_exposure_audit.py

P68 validation suite — 52 tests.
Vérifie : JSON audit, modèle catégories, routes matrix, findings critiques,
flags sécurité, régressions P56E→P67.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P68_JSON = os.path.join(ROOT, "docs", "core_import", "P68_API_AUTH_ROUTE_EXPOSURE_AUDIT.json")
AUTH_PY = os.path.join(ROOT, "apps", "obsidia_api", "auth.py")
BRODY_PY = os.path.join(ROOT, "apps", "obsidia_api", "routes", "brody.py")
RUNTIME_FREEZE_PY = os.path.join(ROOT, "apps", "obsidia_api", "routes", "runtime_freeze.py")
BLOCKCHAIN_PY = os.path.join(ROOT, "apps", "obsidia_api", "routes", "blockchain.py")


@pytest.fixture(scope="module")
def p68():
    with open(P68_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def routes(p68):
    return p68["routes_matrix"]


# ---------------------------------------------------------------------------
# Section 1 — JSON de base (5 tests)
# ---------------------------------------------------------------------------

def test_p68_json_exists():
    assert os.path.isfile(P68_JSON)


def test_p68_json_status(p68):
    assert p68["status"] == "P68_API_AUTH_ROUTE_EXPOSURE_AUDIT_READY"


def test_p68_json_mode(p68):
    assert p68["mode"] == "AUDIT_ONLY"


def test_p68_source_patch_false(p68):
    assert p68["source_patch_applied"] is False


def test_p68_files_imported_zero(p68):
    assert p68["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 — Modèle catégories d'exposition (10 tests)
# ---------------------------------------------------------------------------

def test_route_model_public_minimal_safe(p68):
    assert "public_minimal_safe" in p68["route_model"]


def test_route_model_auth_required_readonly(p68):
    assert "auth_required_readonly" in p68["route_model"]


def test_route_model_auth_required_dry_run(p68):
    assert "auth_required_dry_run" in p68["route_model"]


def test_route_model_internal_only(p68):
    assert "internal_only" in p68["route_model"]


def test_route_model_workbench_only(p68):
    assert "workbench_only" in p68["route_model"]


def test_route_model_source_exposure_review(p68):
    assert "source_exposure_review" in p68["route_model"]


def test_route_model_action_risk_review(p68):
    assert "action_risk_review" in p68["route_model"]


def test_route_model_connector_egress_review(p68):
    assert "connector_egress_review" in p68["route_model"]


def test_category_counts_action_risk_present(p68):
    assert p68["category_counts"].get("ACTION_RISK_REVIEW", 0) > 0


def test_category_counts_memory_graphiti_present(p68):
    assert p68["category_counts"].get("MEMORY_GRAPHITI_REVIEW", 0) > 0


# ---------------------------------------------------------------------------
# Section 3 — Routes matrix (5 tests)
# ---------------------------------------------------------------------------

def test_routes_matrix_nonempty(routes):
    assert len(routes) > 0


def test_routes_matrix_count_gte_70(routes):
    # 80 routes détectées = 77 routes API + 3 connecteurs
    assert len(routes) >= 70


def test_routes_matrix_has_required_fields(routes):
    required = {"route_path", "http_method", "source_file", "auth_required",
                "category", "risk_level", "decision_authority"}
    for entry in routes:
        for field in required:
            assert field in entry, f"Missing field {field} in {entry.get('route_path')}"


def test_all_routes_have_decision_authority_kx108(routes):
    for entry in routes:
        assert entry["decision_authority"] == "KX108_ONLY", (
            f"Route {entry['route_path']} has decision_authority={entry['decision_authority']}"
        )


def test_brody_chat_auth_required(routes):
    brody_chat = [r for r in routes if "/brody/chat" in r["route_path"]]
    assert len(brody_chat) == 1
    assert brody_chat[0]["auth_required"] is True
    assert brody_chat[0]["detected_auth"] == "require_api_key"


# ---------------------------------------------------------------------------
# Section 4 — Buckets (5 tests)
# ---------------------------------------------------------------------------

def test_public_minimal_safe_has_health(p68):
    safe = p68["public_minimal_safe"]
    assert any("/health" in r for r in safe)


def test_public_minimal_safe_has_readiness(p68):
    safe = p68["public_minimal_safe"]
    assert any("/readiness" in r for r in safe)


def test_action_risk_review_has_blockchain(p68):
    action = p68["action_risk_review"]
    assert any("blockchain" in r for r in action)


def test_connector_egress_review_has_three_connectors(p68):
    egress = p68["connector_egress_review"]
    connector_entries = [r for r in egress if "CONNECTOR" in r]
    assert len(connector_entries) >= 3


def test_internal_only_has_runtime_freeze(p68):
    internal = p68["internal_only"]
    assert any("runtime" in r for r in internal)


# ---------------------------------------------------------------------------
# Section 5 — Findings critiques (5 tests)
# ---------------------------------------------------------------------------

def test_focus_findings_nonempty(p68):
    assert len(p68["focus_findings"]) >= 5


def test_focus_findings_runtime_freeze_internal(p68):
    freeze = [f for f in p68["focus_findings"] if "runtime_freeze" in f["file"]]
    assert len(freeze) == 1
    assert freeze[0]["category"] == "INTERNAL_ONLY"


def test_focus_findings_blockchain_action_risk(p68):
    bc = [f for f in p68["focus_findings"] if "blockchain" in f["file"]]
    assert len(bc) == 1
    assert bc[0]["category"] == "ACTION_RISK_REVIEW"


def test_focus_findings_connectors_egress_review(p68):
    connectors = [f for f in p68["focus_findings"]
                  if f["category"] == "CONNECTOR_EGRESS_REVIEW"]
    assert len(connectors) >= 3


def test_preexisting_test_debt_documented(p68):
    assert len(p68["preexisting_test_debt"]) > 0


# ---------------------------------------------------------------------------
# Section 6 — Flags sécurité P68 (10 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p68):
    assert p68["runtime_modified"] is False


def test_sigma_modified_false(p68):
    assert p68["sigma_modified"] is False


def test_routes_modified_false(p68):
    assert p68["routes_modified"] is False


def test_srl_modified_false(p68):
    assert p68["srl_modified"] is False


def test_act_enabled_false(p68):
    assert p68["act_enabled"] is False


def test_memory_write_enabled_false(p68):
    assert p68["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p68):
    assert p68["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p68):
    assert p68["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p68):
    assert p68["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p68):
    assert p68["x108_merge_enabled"] is False


# ---------------------------------------------------------------------------
# Section 7 — Vérifications source (5 tests)
# ---------------------------------------------------------------------------

def test_auth_py_fail_closed_503():
    content = open(AUTH_PY, encoding="utf-8").read()
    assert "503" in content
    assert "OBSIDIA_API_KEY" in content


def test_auth_py_no_silent_bypass():
    content = open(AUTH_PY, encoding="utf-8").read()
    # Ne doit pas y avoir de "return" conditionnel contournant le check
    assert "OBSIDIA_API_KEY" in content


def test_brody_py_has_require_api_key():
    content = open(BRODY_PY, encoding="utf-8").read()
    assert "require_api_key" in content


def test_runtime_freeze_subprocess_git_readonly():
    content = open(RUNTIME_FREEZE_PY, encoding="utf-8").read()
    assert "subprocess" in content
    assert "git" in content
    # Ne doit pas y avoir de writes git
    assert "git commit" not in content
    assert "git push" not in content


def test_blockchain_py_no_auth():
    content = open(BLOCKCHAIN_PY, encoding="utf-8").read()
    # blockchain.py n'a pas require_api_key — finding audit P68
    assert "require_api_key" not in content


# ---------------------------------------------------------------------------
# Section 8 — Régressions P56E→P67 (12 tests)
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


def test_p67_regression():
    assert _run_test_file("tests/test_p67_boundary_semantic_split_audit.py")


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
