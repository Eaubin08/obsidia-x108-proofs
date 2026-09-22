"""
tests/test_p66_srl_readonly_memory_layer.py

P66 validation suite — 42 tests.
Vérifie : JSON audit, taxonomie SRL, boundary, composants, boundary fixes, régressions P56E→P65.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

P66_JSON = os.path.join(ROOT, "docs", "core_import", "P66_SRL_READONLY_MEMORY_LAYER.json")
SRL_DIR = os.path.join(ROOT, "periphery", "brody_memory_readonly", "srl_session_registry_layer_readonly")
AUTO_TRIAGE_PY = os.path.join(ROOT, "periphery", "brody_memory_readonly", "auto_triage_memory_intake_readonly", "brody_auto_triage_memory_intake_readonly_v1.py")
NEO4J_BRIDGE_PY = os.path.join(ROOT, "periphery", "brody_memory_readonly", "neo4j_brody_guide_bridge_readonly", "brody_neo4j_guide_bridge_readonly_v1.py")
POST_HUMAN_TRIAGE_PY = os.path.join(ROOT, "periphery", "brody_memory_readonly", "post_human_review_memory_triage_readonly", "brody_post_human_review_memory_triage_readonly_v1.py")


@pytest.fixture(scope="module")
def p66_data():
    with open(P66_JSON, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Section 1 — JSON audit (4 tests)
# ---------------------------------------------------------------------------

def test_p66_json_exists():
    assert os.path.isfile(P66_JSON)


def test_p66_json_status(p66_data):
    assert p66_data["status"] == "P66_SRL_READONLY_MEMORY_LAYER_READY"


def test_p66_json_mode(p66_data):
    assert p66_data["mode"] == "AUDIT_AND_READONLY_CANONIZATION"


def test_p66_json_srl_status(p66_data):
    assert p66_data["srl_status"] == "FOUNDATION_PRESENT_PRECANONICAL_READY"


# ---------------------------------------------------------------------------
# Section 2 — Composants (2 tests)
# ---------------------------------------------------------------------------

def test_components_found_nonempty(p66_data):
    assert len(p66_data["components_found"]) > 0


def test_manual_write_modules_quarantined(p66_data):
    quarantined = [q["name"] for q in p66_data["manual_write_modules_quarantined"]]
    assert "graphiti_import_apply_guarded_manual_only" in quarantined
    assert "graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only" in quarantined


# ---------------------------------------------------------------------------
# Section 3 — Taxonomie SRL (6 tests)
# ---------------------------------------------------------------------------

def test_taxonomy_active(p66_data):
    assert "ACTIVE" in p66_data["srl_taxonomy"]


def test_taxonomy_semi_active(p66_data):
    assert "SEMI_ACTIVE" in p66_data["srl_taxonomy"]


def test_taxonomy_cold(p66_data):
    assert "COLD" in p66_data["srl_taxonomy"]


def test_taxonomy_ghost(p66_data):
    assert "GHOST" in p66_data["srl_taxonomy"]


def test_taxonomy_reflex_alert(p66_data):
    assert "REFLEX_ALERT" in p66_data["srl_taxonomy"]


def test_taxonomy_boundary_alert(p66_data):
    assert "BOUNDARY_ALERT" in p66_data["srl_taxonomy"]


# ---------------------------------------------------------------------------
# Section 4 — Métriques SRL (1 test)
# ---------------------------------------------------------------------------

def test_srl_metrics_nonempty(p66_data):
    assert len(p66_data["srl_metrics"]) >= 19


# ---------------------------------------------------------------------------
# Section 5 — Fichiers SRL créés sous srl_session_registry_layer_readonly (1 test)
# ---------------------------------------------------------------------------

def test_srl_files_under_correct_path(p66_data):
    for entry in p66_data["created_files"]:
        assert "srl_session_registry_layer_readonly" in entry["path"]


# ---------------------------------------------------------------------------
# Section 6 — Surfaces non modifiées (4 tests)
# ---------------------------------------------------------------------------

def test_sigma_not_modified(p66_data):
    assert p66_data["sigma_modified"] is False


def test_runtime_wiring_not_modified(p66_data):
    assert p66_data["runtime_wiring_modified"] is False


def test_proofs_v18_3_1_not_modified(p66_data):
    assert p66_data["proofs_v18_3_1_modified"] is False


def test_routes_not_modified(p66_data):
    assert p66_data["routes_modified"] is False


# ---------------------------------------------------------------------------
# Section 7 — Flags sécurité P66 (6 tests)
# ---------------------------------------------------------------------------

def test_no_act_enabled(p66_data):
    assert p66_data["act_enabled"] is False


def test_memory_write_false(p66_data):
    assert p66_data["memory_write_enabled"] is False


def test_graphiti_write_false(p66_data):
    assert p66_data["graphiti_write_enabled"] is False


def test_neo4j_write_false(p66_data):
    assert p66_data["neo4j_write_enabled"] is False


def test_kernel_mutation_false(p66_data):
    assert p66_data["kernel_mutation_enabled"] is False


def test_x108_merge_false(p66_data):
    assert p66_data["x108_merge_enabled"] is False


def test_decision_authority_kx108(p66_data):
    assert p66_data["decision_authority"] == "KX108_ONLY"


# ---------------------------------------------------------------------------
# Section 8 — Boundary fixes vérifiés dans les fichiers source (4 tests)
# ---------------------------------------------------------------------------

def test_auto_triage_emits_verdict_false():
    content = open(AUTO_TRIAGE_PY, encoding="utf-8").read()
    assert '"emits_verdict": False' in content or '"emits_verdict": False,' in content


def test_auto_triage_emits_allow_hold_block_false():
    content = open(AUTO_TRIAGE_PY, encoding="utf-8").read()
    assert '"emits_allow_hold_block": False' in content


def test_auto_triage_no_mandatory_hold_immediate_block():
    content = open(AUTO_TRIAGE_PY, encoding="utf-8").read()
    assert "MANDATORY_HOLD_IMMEDIATE_BLOCK" not in content


def test_auto_triage_uses_boundary_alert_non_decisional():
    content = open(AUTO_TRIAGE_PY, encoding="utf-8").read()
    assert "BOUNDARY_ALERT_NON_DECISIONAL" in content


# ---------------------------------------------------------------------------
# Section 9 — Neo4j password fix (1 test)
# ---------------------------------------------------------------------------

def test_neo4j_no_admin1234_fallback():
    content = open(NEO4J_BRIDGE_PY, encoding="utf-8").read()
    assert "admin1234" not in content


# ---------------------------------------------------------------------------
# Section 10 — Pas de flags interdits dans les fichiers SRL créés (5 tests)
# ---------------------------------------------------------------------------

def _read_srl_python_files():
    texts = []
    for fname in os.listdir(SRL_DIR):
        if fname.endswith(".py"):
            texts.append(open(os.path.join(SRL_DIR, fname), encoding="utf-8").read())
    return "\n".join(texts)


def test_srl_no_emits_verdict_true():
    combined = _read_srl_python_files()
    assert "emits_verdict = True" not in combined
    assert '"emits_verdict": True' not in combined


def test_srl_no_emits_allow_hold_block_true():
    combined = _read_srl_python_files()
    assert "emits_allow_hold_block = True" not in combined
    assert '"emits_allow_hold_block": True' not in combined


def test_srl_no_graphiti_index_write_true():
    combined = _read_srl_python_files()
    assert '"graphiti_index_write": True' not in combined


def test_srl_no_memory_intake_true():
    combined = _read_srl_python_files()
    assert '"memory_intake": True' not in combined


def test_srl_no_neo4j_password_admin1234():
    combined = _read_srl_python_files()
    json_files = []
    for fname in os.listdir(SRL_DIR):
        if fname.endswith(".json"):
            json_files.append(open(os.path.join(SRL_DIR, fname), encoding="utf-8").read())
    all_content = combined + "\n".join(json_files)
    assert "admin1234" not in all_content


# ---------------------------------------------------------------------------
# Section 11 — Régressions P56E→P65 (10 tests)
# ---------------------------------------------------------------------------

def _run_test_file(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header", "-k", "not regression"],
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


# ---------------------------------------------------------------------------
# Section 12 — verify_all et forbidden (2 tests)
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
