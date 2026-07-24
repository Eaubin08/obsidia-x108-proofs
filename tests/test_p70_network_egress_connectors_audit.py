"""
tests/test_p70_network_egress_connectors_audit.py

P70 validation suite — 63 tests.
Vérifie : JSON audit, modèle réseau, network_matrix, buckets, connector_matrix,
findings, flags sécurité, vérifications source, régressions P56E→P69.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P70_JSON = os.path.join(ROOT, "docs", "core_import", "P70_NETWORK_EGRESS_CONNECTORS_AUDIT.json")
AVIATION = os.path.join(ROOT, "connectors", "aviation_robo.py")
BANK = os.path.join(ROOT, "connectors", "bank_normal_flow.py")
TRADING = os.path.join(ROOT, "connectors", "trading_live.py")
GRAPHITI_CLIENT = os.path.join(ROOT, "apps", "obsidia_api", "graphiti_v20_readonly_client.py")


@pytest.fixture(scope="module")
def p70():
    with open(P70_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def network_matrix(p70):
    return p70["network_matrix"]


@pytest.fixture(scope="module")
def connector_matrix(p70):
    return p70["connector_matrix"]


# ---------------------------------------------------------------------------
# Section 1 — JSON de base (5 tests)
# ---------------------------------------------------------------------------

def test_p70_json_exists():
    assert os.path.isfile(P70_JSON)


def test_p70_json_status(p70):
    assert p70["status"] == "P70_NETWORK_EGRESS_CONNECTORS_AUDIT_READY"


def test_p70_json_mode(p70):
    assert p70["mode"] == "AUDIT_ONLY"


def test_p70_source_patch_false(p70):
    assert p70["source_patch_applied"] is False


def test_p70_files_imported_zero(p70):
    assert p70["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 — Modèle réseau (10 tests)
# ---------------------------------------------------------------------------

def test_network_model_none(p70):
    assert "network_egress_none" in p70["network_model"]


def test_network_model_test_only(p70):
    assert "test_only" in p70["network_model"]


def test_network_model_localhost_review(p70):
    assert "localhost_review" in p70["network_model"]


def test_network_model_connector_dry_run(p70):
    assert "connector_dry_run" in p70["network_model"]


def test_network_model_connector_active_review(p70):
    assert "connector_active_review" in p70["network_model"]


def test_network_model_graphiti_review(p70):
    assert "graphiti_review" in p70["network_model"]


def test_network_model_neo4j_review(p70):
    assert "neo4j_review" in p70["network_model"]


def test_network_model_market_data_review(p70):
    assert "market_data_review" in p70["network_model"]


def test_network_model_trading_review(p70):
    assert "trading_review" in p70["network_model"]


def test_network_model_blocked(p70):
    assert "blocked" in p70["network_model"]


# ---------------------------------------------------------------------------
# Section 3 — Network matrix (4 tests)
# ---------------------------------------------------------------------------

def test_network_matrix_nonempty(network_matrix):
    assert len(network_matrix) > 0


def test_network_matrix_required_fields(network_matrix):
    required = {
        "path", "surface", "category", "risk_level", "reason", "next_action",
        "has_timeout", "has_dry_run_flag", "has_kx108_authority",
        "live_loop", "localhost_target", "external_target",
        "memory_write", "graphiti_write", "neo4j_write",
    }
    for e in network_matrix:
        for f in required:
            assert f in e, f"Champ manquant {f} dans entrée {e.get('path')}"


def test_category_counts_nonempty(p70):
    assert len(p70["category_counts"]) > 0


def test_category_connector_active_review_present(p70):
    assert p70["category_counts"].get("NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW", 0) > 0


# ---------------------------------------------------------------------------
# Section 4 — Buckets (9 tests)
# ---------------------------------------------------------------------------

def test_network_egress_none_bucket(p70):
    assert isinstance(p70["network_egress_none"], list)
    assert len(p70["network_egress_none"]) > 0


def test_network_egress_test_only_bucket(p70):
    assert isinstance(p70["network_egress_test_only"], list)
    assert len(p70["network_egress_test_only"]) > 0


def test_network_egress_localhost_review_bucket(p70):
    assert isinstance(p70["network_egress_localhost_review"], list)
    assert len(p70["network_egress_localhost_review"]) > 0


def test_network_egress_connector_active_review_bucket(p70):
    assert isinstance(p70["network_egress_connector_active_review"], list)
    assert len(p70["network_egress_connector_active_review"]) >= 2


def test_network_egress_graphiti_review_bucket(p70):
    assert isinstance(p70["network_egress_graphiti_review"], list)
    assert len(p70["network_egress_graphiti_review"]) > 0


def test_network_egress_neo4j_review_bucket(p70):
    assert isinstance(p70["network_egress_neo4j_review"], list)
    assert len(p70["network_egress_neo4j_review"]) > 0


def test_network_egress_trading_review_bucket(p70):
    assert isinstance(p70["network_egress_trading_review"], list)
    assert len(p70["network_egress_trading_review"]) >= 1


def test_network_egress_blocked_bucket(p70):
    assert isinstance(p70["network_egress_blocked"], list)
    assert len(p70["network_egress_blocked"]) >= 1


def test_network_egress_connector_dry_run_bucket(p70):
    assert isinstance(p70["network_egress_connector_dry_run"], list)


# ---------------------------------------------------------------------------
# Section 5 — Connector matrix (5 tests)
# ---------------------------------------------------------------------------

def test_connector_matrix_nonempty(connector_matrix):
    assert len(connector_matrix) >= 5


def test_connector_matrix_required_fields(connector_matrix):
    required = {
        "connector_path", "connector_name", "target", "method",
        "timeout_declared", "dry_run_declared", "kx108_authority_declared",
        "loop_type", "irreversible_in_payload", "external_egress",
        "category", "risk_level", "next_action",
    }
    for e in connector_matrix:
        for f in required:
            assert f in e, f"Champ manquant {f} dans connecteur {e.get('connector_name')}"


def test_connector_aviation_category(connector_matrix):
    avi = [c for c in connector_matrix if "aviation_robo" in c["connector_path"]]
    assert len(avi) == 1
    assert avi[0]["category"] == "CONNECTOR_ACTIVE_REVIEW"
    assert avi[0]["risk_level"] == "HIGH"
    assert "while True" in avi[0]["loop_type"]
    assert avi[0]["dry_run_declared"] is False


def test_connector_trading_category(connector_matrix):
    trading = [c for c in connector_matrix if "trading_live" in c["connector_path"]]
    assert len(trading) == 1
    assert trading[0]["category"] == "CONNECTOR_DO_NOT_RUN"
    assert trading[0]["external_egress"] is True


def test_connector_graphiti_v20_safe(connector_matrix):
    g = [c for c in connector_matrix if "graphiti_v20_readonly" in c["connector_path"]]
    assert len(g) == 1
    assert g[0]["category"] == "CONNECTOR_DRY_RUN_SAFE"
    assert g[0]["risk_level"] == "LOW"
    assert g[0]["dry_run_declared"] is True


# ---------------------------------------------------------------------------
# Section 6 — Focus findings (5 tests)
# ---------------------------------------------------------------------------

def test_focus_findings_nonempty(p70):
    assert len(p70["focus_findings"]) >= 5


def test_focus_findings_aviation_present(p70):
    avi = [f for f in p70["focus_findings"] if "aviation" in f["file"]]
    assert len(avi) >= 1
    assert avi[0]["risk"] == "HIGH"


def test_focus_findings_trading_do_not_run(p70):
    trading = [f for f in p70["focus_findings"] if "trading" in f["file"]]
    assert len(trading) >= 1
    assert "DO_NOT_RUN" in trading[0]["action"] or "UNGUARDED" in trading[0]["action"]


def test_focus_findings_graphiti_safe(p70):
    g = [f for f in p70["focus_findings"] if "graphiti_v20" in f["file"]]
    assert len(g) >= 1
    assert g[0]["risk"] == "LOW"


def test_preexisting_manifest_drift_documented(p70):
    paths = [e["file"] for e in p70["preexisting_manifest_drift"]]
    assert any("world_action_bus" in p for p in paths)
    assert any("PROOFKIT_REPORT" in p for p in paths)


# ---------------------------------------------------------------------------
# Section 7 — Flags sécurité P70 (11 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p70):
    assert p70["runtime_modified"] is False


def test_sigma_modified_false(p70):
    assert p70["sigma_modified"] is False


def test_routes_modified_false(p70):
    assert p70["routes_modified"] is False


def test_srl_modified_false(p70):
    assert p70["srl_modified"] is False


def test_connectors_modified_false(p70):
    assert p70["connectors_modified"] is False


def test_act_enabled_false(p70):
    assert p70["act_enabled"] is False


def test_memory_write_enabled_false(p70):
    assert p70["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p70):
    assert p70["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p70):
    assert p70["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p70):
    assert p70["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p70):
    assert p70["x108_merge_enabled"] is False


# ---------------------------------------------------------------------------
# Section 8 — Vérifications source connecteurs (3 tests)
# ---------------------------------------------------------------------------

def test_aviation_has_while_true_and_requests_post():
    content = open(AVIATION, encoding="utf-8").read()
    assert "while True" in content
    assert "requests.post" in content
    assert "irreversible" in content


def test_trading_has_ccxt_binance_external():
    content = open(TRADING, encoding="utf-8").read()
    assert "ccxt" in content
    assert "binance" in content
    assert "while True" in content


def test_graphiti_client_all_get_readonly():
    content = open(GRAPHITI_CLIENT, encoding="utf-8").read()
    assert "GET" in content
    assert "graphiti_write" in content
    assert "neo4j_write" in content


# ---------------------------------------------------------------------------
# Section 9 — Régressions P56E→P69 (14 tests)
# ---------------------------------------------------------------------------

def _run(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header"],
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


# ---------------------------------------------------------------------------
# Section 10 — verify_all et forbidden (2 tests)
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
