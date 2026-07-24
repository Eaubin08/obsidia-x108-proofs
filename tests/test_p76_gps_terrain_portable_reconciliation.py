"""
tests/test_p76_gps_terrain_portable_reconciliation.py

P76 validation suite.
Verifie : JSON audit, modele GPS, matrice, proof integre,
adapters safe, connectors bloques, invariants P70/P72, flags securite,
regressions P56E->P75.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P76_JSON = os.path.join(ROOT, "docs", "core_import", "P76_GPS_TERRAIN_PORTABLE_RECONCILIATION.json")
P76_MD = os.path.join(ROOT, "docs", "core_import", "P76_GPS_TERRAIN_PORTABLE_RECONCILIATION.md")
SIGMA_DIR = os.path.join(ROOT, "sigma")
GPS_AGENTS = os.path.join(SIGMA_DIR, "domains", "gps_defense_aviation_agents.py")
GPS_EXAMPLES_DIR = os.path.join(SIGMA_DIR, "examples")
CONNECTORS_DIR = os.path.join(ROOT, "connectors")
PERIPHERY_DIR = os.path.join(ROOT, "periphery")
SERVER_SEALED = os.path.join(ROOT, "server.kernel.sealed.cjs")


@pytest.fixture(scope="module")
def p76():
    with open(P76_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def gps_matrix(p76):
    return p76["gps_matrix"]


@pytest.fixture(scope="module")
def connector_matrix(p76):
    return p76["connector_matrix"]


@pytest.fixture(scope="module")
def replay_matrix(p76):
    return p76["replay_candidate_matrix"]


@pytest.fixture(scope="module")
def focus_findings(p76):
    return p76["focus_findings"]


# ---------------------------------------------------------------------------
# Section 1 — JSON de base (6 tests)
# ---------------------------------------------------------------------------

def test_p76_json_exists():
    assert os.path.isfile(P76_JSON)


def test_p76_json_status(p76):
    assert p76["status"] == "P76_GPS_TERRAIN_PORTABLE_RECONCILIATION_READY"


def test_p76_json_mode(p76):
    assert p76["mode"] == "AUDIT_AND_RECONCILIATION_DOCS_ONLY"


def test_p76_gps_decision(p76):
    assert p76["gps_decision"] == "KEEP_PROOF_AND_TERRAIN_EVIDENCE_SEPARATED"


def test_p76_source_patch_not_applied(p76):
    assert p76["source_patch_applied"] is False


def test_p76_files_imported_zero(p76):
    assert p76["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 — Modele GPS (5 tests)
# ---------------------------------------------------------------------------

def test_gps_model_proof_integrated(p76):
    assert "proof_integrated" in p76["gps_model"]


def test_gps_model_connector_do_not_run(p76):
    assert "connector_do_not_run" in p76["gps_model"]


def test_gps_model_localhost_archive_only(p76):
    assert "localhost_archive_only" in p76["gps_model"]


def test_gps_model_tested_proof_surface(p76):
    assert "tested_proof_surface" in p76["gps_model"]


def test_gps_model_replay_candidate(p76):
    assert "replay_candidate" in p76["gps_model"]


# ---------------------------------------------------------------------------
# Section 3 — Matrice GPS — structure (5 tests)
# ---------------------------------------------------------------------------

def test_gps_matrix_exists(p76):
    assert isinstance(p76["gps_matrix"], list)
    assert len(p76["gps_matrix"]) > 0


def test_gps_matrix_count(p76):
    assert p76["gps_files_scanned_count"] >= 20
    assert len(p76["gps_matrix"]) >= 20


def test_gps_matrix_required_fields(gps_matrix):
    required = {
        "file_path", "component_name", "category", "decision",
        "risk_level", "description", "proof_wins", "sigma_bridge_safe",
        "p72_invariants",
    }
    for entry in gps_matrix:
        for f in required:
            assert f in entry, f"Champ manquant {f} dans {entry.get('file_path')}"


def test_gps_matrix_all_decisions_valid(gps_matrix):
    valid = {
        "KEEP_PROOF_VERSION", "KEEP_AS_TERRAIN_EVIDENCE",
        "REPLAY_ONLY_LATER", "BLOCK_CONNECTOR_RUN",
        "ADAPT_READONLY_LATER", "ADAPT_DRY_RUN_LATER",
        "BLOCK_UNTIL_AUTH_EGRESS_HARDENING",
    }
    for e in gps_matrix:
        assert e["decision"] in valid, (
            f"Decision invalide dans {e['file_path']}: {e['decision']}"
        )


def test_gps_matrix_category_counts(p76):
    counts = p76["category_counts"]
    assert counts.get("GPS_PROOF_INTEGRATED", 0) >= 4
    assert counts.get("GPS_TESTED_PROOF_SURFACE", 0) >= 3
    assert counts.get("GPS_EXAMPLE_ONLY", 0) >= 6
    assert counts.get("GPS_CONNECTOR_DO_NOT_RUN", 0) >= 3


# ---------------------------------------------------------------------------
# Section 4 — GPS Proof integre (7 tests)
# ---------------------------------------------------------------------------

def _get_gps_entry(matrix, path_fragment):
    return next((e for e in matrix if path_fragment in e["file_path"]), None)


def test_gps_agents_proof_integrated(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "gps_defense_aviation_agents.py")
    assert entry is not None
    assert entry["category"] == "GPS_PROOF_INTEGRATED"
    assert entry["decision"] == "KEEP_PROOF_VERSION"
    assert entry["proof_wins"] is True


def test_gps_contracts_proof_integrated(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "GpsDefenseAviationState")
    assert entry is not None
    assert entry["category"] == "GPS_PROOF_INTEGRATED"


def test_gps_run_pipeline_proof_integrated(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "run_pipeline.py")
    assert entry is not None
    assert entry["category"] == "GPS_PROOF_INTEGRATED"
    assert entry["sigma_bridge_safe"] is True


def test_gps_guard_proof_integrated(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "guard.py")
    assert entry is not None
    assert entry["category"] == "GPS_PROOF_INTEGRATED"
    assert entry["proof_wins"] is True


def test_gps_agents_file_exists():
    assert os.path.isfile(GPS_AGENTS)


def test_gps_agents_6_agents():
    content = open(GPS_AGENTS, encoding="utf-8").read()
    for agent in [
        "SourceAvailabilityAgent",
        "TrajectoryIntegrityAgent",
        "SourceConflictAgent",
        "TimeSkewAgent",
        "BrownoutAgent",
        "AttestationReadinessAgent",
    ]:
        assert agent in content, f"Agent {agent} manquant dans gps_defense_aviation_agents.py"


def test_gps_proof_integrated_list_nonempty(p76):
    assert len(p76["proof_integrated"]) >= 4


# ---------------------------------------------------------------------------
# Section 5 — Tests GPS proof surface (4 tests)
# ---------------------------------------------------------------------------

def test_gps_smoke_in_matrix(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "test_gps_smoke.py")
    assert entry is not None
    assert entry["category"] == "GPS_TESTED_PROOF_SURFACE"


def test_gps_semantics_in_matrix(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "test_gps_semantics.py")
    assert entry is not None
    assert entry["category"] == "GPS_TESTED_PROOF_SURFACE"


def test_gps_fail_closed_in_matrix(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "test_gps_fail_closed.py")
    assert entry is not None
    assert entry["category"] == "GPS_TESTED_PROOF_SURFACE"


def test_gps_tests_files_exist():
    for f in ["test_gps_smoke.py", "test_gps_semantics.py", "test_gps_fail_closed.py"]:
        path = os.path.join(SIGMA_DIR, "tests", f)
        assert os.path.isfile(path), f"Fichier manquant : {path}"


# ---------------------------------------------------------------------------
# Section 6 — Exemples GPS (5 tests)
# ---------------------------------------------------------------------------

def test_gps_examples_count(gps_matrix):
    examples = [e for e in gps_matrix if e["category"] == "GPS_EXAMPLE_ONLY"]
    assert len(examples) >= 6


def test_gps_nominal_example_exists():
    assert os.path.isfile(os.path.join(GPS_EXAMPLES_DIR, "gps_nominal.json"))


def test_gps_omega_chaos_example_exists():
    path = os.path.join(GPS_EXAMPLES_DIR, "gps_omega_chaos.json")
    assert os.path.isfile(path)
    data = json.loads(open(path, encoding="utf-8").read())
    assert data["trajectory_drift_score"] >= 0.90
    assert data["source_conflict_score"] >= 0.90


def test_gps_no_source_example_no_sources():
    path = os.path.join(GPS_EXAMPLES_DIR, "gps_no_source.json")
    assert os.path.isfile(path)
    data = json.loads(open(path, encoding="utf-8").read())
    assert data["gps_available"] is False
    assert data["inertial_available"] is False
    assert data["radio_available"] is False


def test_gps_source_conflict_high_score():
    path = os.path.join(GPS_EXAMPLES_DIR, "gps_source_conflict.json")
    assert os.path.isfile(path)
    data = json.loads(open(path, encoding="utf-8").read())
    assert data["source_conflict_score"] >= 0.80


# ---------------------------------------------------------------------------
# Section 7 — Adapters GPS safe (4 tests)
# ---------------------------------------------------------------------------

def test_gps_adapter_safe_readonly(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "gps_adapter.py")
    assert entry is not None
    assert entry["category"] == "GPS_ADAPTER_SAFE_READONLY"
    assert entry["sigma_bridge_safe"] is True


def test_sigma_bridge_safe_readonly(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "sigma_bridge.py")
    assert entry is not None
    assert entry["category"] == "GPS_ADAPTER_SAFE_READONLY"
    assert entry["sigma_bridge_safe"] is True
    assert entry["proof_wins"] is True


def test_gps_adapter_file_exists():
    path = os.path.join(PERIPHERY_DIR, "adapters", "gps_adapter.py")
    assert os.path.isfile(path)


def test_sigma_bridge_no_direct_act():
    path = os.path.join(PERIPHERY_DIR, "sigma_bridge.py")
    assert os.path.isfile(path)
    content = open(path, encoding="utf-8").read()
    assert "GuardX108" in content
    assert "assert_non_sovereign" in content


# ---------------------------------------------------------------------------
# Section 8 — Connectors DO_NOT_RUN (6 tests)
# ---------------------------------------------------------------------------

def test_aviation_robo_blocked(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "aviation_robo.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_CONNECTOR_RUN"
    assert entry["category"] == "GPS_CONNECTOR_DO_NOT_RUN"


def test_bank_connector_blocked(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "bank_normal_flow.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_CONNECTOR_RUN"


def test_trading_connector_blocked(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "trading_live.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_CONNECTOR_RUN"


def test_connector_do_not_run_list(p76):
    blocked = p76["connector_do_not_run"]
    assert len(blocked) >= 3
    assert any("aviation_robo" in s for s in blocked)


def test_aviation_robo_has_while_true():
    path = os.path.join(CONNECTORS_DIR, "aviation_robo.py")
    assert os.path.isfile(path)
    content = open(path, encoding="utf-8").read()
    assert "while True" in content
    assert "requests.post" in content


def test_trading_live_has_external_network():
    path = os.path.join(CONNECTORS_DIR, "trading_live.py")
    assert os.path.isfile(path)
    content = open(path, encoding="utf-8").read()
    assert "ccxt" in content


# ---------------------------------------------------------------------------
# Section 9 — Localhost / ragnarok archive (3 tests)
# ---------------------------------------------------------------------------

def test_server_sealed_exists():
    assert os.path.isfile(SERVER_SEALED)


def test_server_sealed_localhost_archive(gps_matrix):
    entry = _get_gps_entry(gps_matrix, "server.kernel.sealed.cjs")
    assert entry is not None
    assert entry["category"] == "GPS_LOCALHOST_ARCHIVE_ONLY"
    assert entry["decision"] == "KEEP_AS_TERRAIN_EVIDENCE"


def test_server_sealed_ragnarok_route():
    content = open(SERVER_SEALED, encoding="utf-8").read()
    assert "/kernel/ragnarok" in content
    assert "sigma/run_pipeline.py" in content


# ---------------------------------------------------------------------------
# Section 10 — Terrain evidence (3 tests)
# ---------------------------------------------------------------------------

def test_alldata_absent():
    alldata_path = os.path.join(ROOT, "allData")
    assert not os.path.isdir(alldata_path), "allData/ ne doit pas etre present dans le repo"


def test_sessions_absent():
    sessions_path = os.path.join(ROOT, "_sessions")
    assert not os.path.isdir(sessions_path), "_sessions/ ne doit pas etre present dans le repo"


def test_terrain_evidence_matrix_nonempty(p76):
    assert len(p76["terrain_evidence_matrix"]) >= 2


# ---------------------------------------------------------------------------
# Section 11 — Replay candidates (3 tests)
# ---------------------------------------------------------------------------

def test_replay_candidates_count(p76):
    assert len(p76["replay_candidates"]) >= 4


def test_replay_matrix_all_safe(replay_matrix):
    for r in replay_matrix:
        assert r["safe_to_replay"] is True
        assert r["risk_level"] in ("NONE", "LOW")


def test_replay_omega_chaos_present(replay_matrix):
    rc = next((r for r in replay_matrix if "omega_chaos" in r["file_path"]), None)
    assert rc is not None
    assert rc["expected_x108_gate"] == "BLOCK"


# ---------------------------------------------------------------------------
# Section 12 — Focus findings (5 tests)
# ---------------------------------------------------------------------------

def test_focus_findings_count(focus_findings):
    assert len(focus_findings) >= 7


def test_finding_f1_gps_proof_complete(focus_findings):
    f1 = next((f for f in focus_findings if f["finding_id"] == "P76-F1"), None)
    assert f1 is not None
    assert f1["type"] == "GPS_PROOF_COMPLETE"
    assert "KEEP_PROOF_VERSION" in f1["action"]


def test_finding_f3_connector_do_not_run(focus_findings):
    f3 = next((f for f in focus_findings if f["finding_id"] == "P76-F3"), None)
    assert f3 is not None
    assert f3["type"] == "CONNECTOR_DO_NOT_RUN"
    assert "BLOCK_CONNECTOR_RUN" in f3["action"]


def test_finding_f4_ragnarok_archive(focus_findings):
    f4 = next((f for f in focus_findings if f["finding_id"] == "P76-F4"), None)
    assert f4 is not None
    assert f4["type"] == "LOCALHOST_RAGNAROK_ARCHIVE"
    assert "ragnarok" in f4["description"].lower() or "localhost" in f4["description"].lower()


def test_finding_f7_hardening_roadmap(focus_findings):
    f7 = next((f for f in focus_findings if f["finding_id"] == "P76-F7"), None)
    assert f7 is not None
    assert "HARDENING" in f7["type"]


# ---------------------------------------------------------------------------
# Section 13 — Flags securite (15 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p76):
    assert p76["runtime_modified"] is False


def test_sigma_modified_false(p76):
    assert p76["sigma_modified"] is False


def test_routes_modified_false(p76):
    assert p76["routes_modified"] is False


def test_lean_proofs_modified_false(p76):
    assert p76["lean_proofs_modified"] is False


def test_proofs_modified_false(p76):
    assert p76["proofs_modified"] is False


def test_srl_modified_false(p76):
    assert p76["srl_modified"] is False


def test_connectors_modified_false(p76):
    assert p76["connectors_modified"] is False


def test_source_packs_modified_false(p76):
    assert p76["source_packs_modified"] is False


def test_act_enabled_false(p76):
    assert p76["act_enabled"] is False


def test_memory_write_enabled_false(p76):
    assert p76["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p76):
    assert p76["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p76):
    assert p76["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p76):
    assert p76["kernel_mutation_enabled"] is False


def test_network_called_false(p76):
    assert p76["network_called"] is False


def test_localhost_called_false(p76):
    assert p76["localhost_called"] is False


# ---------------------------------------------------------------------------
# Section 14 — GPS tests sigma executes (5 tests live)
# ---------------------------------------------------------------------------

def _run_sigma_gps(example_name: str) -> dict:
    cmd = [
        sys.executable,
        str(os.path.join(SIGMA_DIR, "run_pipeline.py")),
        "gps_defense_aviation",
        str(os.path.join(GPS_EXAMPLES_DIR, example_name)),
    ]
    out = subprocess.check_output(cmd, text=True, cwd=ROOT)
    return json.loads(out)


def test_gps_nominal_allow():
    result = _run_sigma_gps("gps_nominal.json")
    assert result["x108_gate"] == "ALLOW"
    assert result["market_verdict"] == "TRAJECTORY_VALID"


def test_gps_no_source_hold():
    result = _run_sigma_gps("gps_no_source.json")
    assert result["x108_gate"] in ("HOLD", "BLOCK")
    assert result["market_verdict"] != "TRAJECTORY_VALID"


def test_gps_source_conflict_block():
    result = _run_sigma_gps("gps_source_conflict.json")
    assert result["x108_gate"] == "BLOCK"
    assert result["market_verdict"] == "ABORT_TRAJECTORY"


def test_gps_brownout_not_allow():
    result = _run_sigma_gps("gps_brownout.json")
    assert result["x108_gate"] in ("HOLD", "BLOCK")


def test_gps_omega_chaos_block():
    result = _run_sigma_gps("gps_omega_chaos.json")
    assert result["x108_gate"] in ("HOLD", "BLOCK")


# ---------------------------------------------------------------------------
# Section 15 — Regressions P56E->P75 (20 tests)
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


# ---------------------------------------------------------------------------
# Section 16 — verify_all et forbidden (2 tests)
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
