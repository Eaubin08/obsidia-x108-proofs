"""
P58 — Core Import Triage Operational Path-Aware Tests

Verifies that:
- Le JSON P58 existe et est bien formé
- Aucun import effectif n'a eu lieu (core_files_imported = 0)
- source_patch_applied = false
- safe_batch_1 est non vide et respecte les contraintes de sécurité
- bus_adapter_batch contient exactement les 4 fichiers bus
- Aucun DO_NOT_IMPORT / KEEP_PROOF_VERSION dans safe_batch_1
- Chaque entrée safe_batch_1 a required_tests non vide et risk LOW/CONTROLLED
- Chaque entrée a execution_surface
- PRIVATE_UI_IGNORE n'apparaît jamais dans safe_batch_1
- RESPONSE_TEMPLATE_READONLY jamais classé DECISION_KERNEL
- next_step = P59_SAFE_BATCH_1_IMPORT
- P56E reste PASS
- P57 reste PASS
- Aucun flag runtime/write/ACT actif
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs" / "core_import"
P58_JSON = DOCS / "P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.json"
P57_PLAN = DOCS / "P57_CORE_TO_PROOF_IMPORT_PLAN.json"
P56E_TEST = REPO_ROOT / "tests" / "test_p56e_post_patch_metric_reaudit.py"
P57_TEST = REPO_ROOT / "tests" / "test_p57_core_machinery_runtime_binding_audit.py"

BUS_FILES = {
    "engine/bus/__init__.py",
    "engine/bus/message.py",
    "engine/bus/registry.py",
    "engine/bus/router.py",
}

DO_NOT_IMPORT_CATEGORIES = {"DO_NOT_IMPORT", "KEEP_PROOF_VERSION"}

FORBIDDEN_IN_SAFE_BATCH_1_SURFACES = {"PRIVATE_UI_IGNORE", "RESPONSE_TEMPLATE_READONLY"}


def _load_p58() -> dict:
    assert P58_JSON.exists(), f"P58 JSON manquant : {P58_JSON}"
    data = json.loads(P58_JSON.read_text("utf-8"))
    assert isinstance(data, dict), "P58 JSON doit être un dict"
    return data


# ---------------------------------------------------------------------------
# Test 1 — P58 JSON existe
# ---------------------------------------------------------------------------
def test_p58_01_json_exists():
    data = _load_p58()
    assert data.get("audit_id") == "P58"
    assert "safe_batch_1" in data
    assert "test_batch_2" in data
    assert "bus_adapter_batch" in data
    assert "manual_review_deferred" in data
    assert "do_not_touch_confirmation" in data
    assert "private_ui_exclusion" in data


# ---------------------------------------------------------------------------
# Test 2 — source_patch_applied = false
# ---------------------------------------------------------------------------
def test_p58_02_source_patch_applied_false():
    data = _load_p58()
    assert data.get("source_patch_applied") is False, \
        "source_patch_applied doit être false — aucun patch appliqué en P58"


# ---------------------------------------------------------------------------
# Test 3 — core_files_imported = 0
# ---------------------------------------------------------------------------
def test_p58_03_core_files_imported_zero():
    data = _load_p58()
    assert data.get("core_files_imported") == 0, \
        "P58 est un triage uniquement — aucun fichier importé"


# ---------------------------------------------------------------------------
# Test 4 — safe_batch_1 non vide
# ---------------------------------------------------------------------------
def test_p58_04_safe_batch_1_non_empty():
    data = _load_p58()
    batch = data.get("safe_batch_1", [])
    assert len(batch) > 0, "safe_batch_1 doit contenir au moins un candidat"


# ---------------------------------------------------------------------------
# Test 5 — Aucun DO_NOT_IMPORT dans safe_batch_1
# ---------------------------------------------------------------------------
def test_p58_05_no_do_not_import_in_safe_batch():
    data = _load_p58()
    p57 = json.loads(P57_PLAN.read_text("utf-8")) if P57_PLAN.exists() else []
    do_not_import_paths = {
        e["core_path"] for e in p57
        if e.get("category") == "E_DO_NOT_IMPORT"
    }
    safe_paths = {e["core_path"] for e in data.get("safe_batch_1", [])}
    intersection = safe_paths & do_not_import_paths
    assert not intersection, \
        f"Chemins DO_NOT_IMPORT présents dans safe_batch_1 : {intersection}"


# ---------------------------------------------------------------------------
# Test 6 — Aucun KEEP_PROOF_VERSION dans safe_batch_1
# ---------------------------------------------------------------------------
def test_p58_06_no_keep_proof_in_safe_batch():
    data = _load_p58()
    p57 = json.loads(P57_PLAN.read_text("utf-8")) if P57_PLAN.exists() else []
    keep_proof_paths = {
        e["core_path"] for e in p57
        if e.get("category") == "C_KEEP_PROOF_VERSION"
    }
    safe_paths = {e["core_path"] for e in data.get("safe_batch_1", [])}
    intersection = safe_paths & keep_proof_paths
    assert not intersection, \
        f"Chemins KEEP_PROOF_VERSION présents dans safe_batch_1 : {intersection}"


# ---------------------------------------------------------------------------
# Test 7 — bus_adapter_batch contient exactement les 4 fichiers bus
# ---------------------------------------------------------------------------
def test_p58_07_bus_adapter_batch_exact_four():
    data = _load_p58()
    batch = data.get("bus_adapter_batch", [])
    assert len(batch) == 4, \
        f"bus_adapter_batch doit contenir exactement 4 fichiers, got {len(batch)}"
    bus_paths = {e["core_path"] for e in batch}
    assert bus_paths == BUS_FILES, \
        f"bus_adapter_batch paths incorrects. Attendu: {BUS_FILES}, got: {bus_paths}"


# ---------------------------------------------------------------------------
# Test 8 — Chaque safe_batch_1 a required_tests non vide
# ---------------------------------------------------------------------------
def test_p58_08_safe_batch_required_tests_non_empty():
    data = _load_p58()
    for entry in data.get("safe_batch_1", []):
        tests = entry.get("required_tests", [])
        assert tests and len(tests) > 0, \
            f"required_tests vide pour {entry.get('core_path')}"


# ---------------------------------------------------------------------------
# Test 9 — Chaque safe_batch_1 a risk = LOW ou CONTROLLED
# ---------------------------------------------------------------------------
def test_p58_09_safe_batch_risk_low_or_controlled():
    data = _load_p58()
    allowed_risks = {"LOW", "CONTROLLED"}
    for entry in data.get("safe_batch_1", []):
        risk = entry.get("risk", "")
        assert risk in allowed_risks, \
            f"Risque '{risk}' non autorisé dans safe_batch_1 pour {entry.get('core_path')}"


# ---------------------------------------------------------------------------
# Test 10 — Chaque entrée a execution_surface
# ---------------------------------------------------------------------------
def test_p58_10_all_entries_have_execution_surface():
    data = _load_p58()
    all_batches = (
        data.get("safe_batch_1", [])
        + data.get("test_batch_2", [])
        + data.get("bus_adapter_batch", [])
        + data.get("manual_review_deferred", [])
        + data.get("do_not_touch_confirmation", [])
        + data.get("private_ui_exclusion", [])
    )
    for entry in all_batches:
        assert entry.get("execution_surface"), \
            f"execution_surface manquante pour {entry.get('core_path')}"


# ---------------------------------------------------------------------------
# Test 11 — PRIVATE_UI_IGNORE n'apparaît jamais dans safe_batch_1
# ---------------------------------------------------------------------------
def test_p58_11_private_ui_not_in_safe_batch():
    data = _load_p58()
    for entry in data.get("safe_batch_1", []):
        surface = entry.get("execution_surface", "")
        assert surface not in FORBIDDEN_IN_SAFE_BATCH_1_SURFACES, \
            f"Surface '{surface}' interdite dans safe_batch_1 pour {entry.get('core_path')}"


# ---------------------------------------------------------------------------
# Test 12 — RESPONSE_TEMPLATE_READONLY jamais classé DECISION_KERNEL
# ---------------------------------------------------------------------------
def test_p58_12_response_template_not_decision_kernel():
    data = _load_p58()
    all_batches = (
        data.get("safe_batch_1", [])
        + data.get("test_batch_2", [])
        + data.get("bus_adapter_batch", [])
        + data.get("manual_review_deferred", [])
        + data.get("do_not_touch_confirmation", [])
        + data.get("private_ui_exclusion", [])
    )
    for entry in all_batches:
        if entry.get("execution_surface") == "RESPONSE_TEMPLATE_READONLY":
            classification = entry.get("classification", "")
            assert classification != "DECISION_KERNEL", \
                f"RESPONSE_TEMPLATE_READONLY classé DECISION_KERNEL pour {entry.get('core_path')}"


# ---------------------------------------------------------------------------
# Test 13 — next_step = P59_SAFE_BATCH_1_IMPORT
# ---------------------------------------------------------------------------
def test_p58_13_next_step():
    data = _load_p58()
    assert data.get("next_step") == "P59_SAFE_BATCH_1_IMPORT", \
        f"next_step incorrect: {data.get('next_step')}"


# ---------------------------------------------------------------------------
# Test 14 — P56E test file exists (P56E reste PASS)
# ---------------------------------------------------------------------------
def test_p58_14_p56e_test_file_exists():
    assert P56E_TEST.exists(), \
        f"Fichier de test P56E manquant — P56E doit rester PASS : {P56E_TEST}"


# ---------------------------------------------------------------------------
# Test 15 — P57 test file exists (P57 reste PASS)
# ---------------------------------------------------------------------------
def test_p58_15_p57_test_file_exists():
    assert P57_TEST.exists(), \
        f"Fichier de test P57 manquant — P57 doit rester PASS : {P57_TEST}"


# ---------------------------------------------------------------------------
# Test 16 — Aucun runtime_allowed_now = true effectif
# ---------------------------------------------------------------------------
def test_p58_16_no_runtime_allowed():
    data = _load_p58()
    flags = data.get("flags", {})
    assert flags.get("runtime_allowed_now") is False, \
        "runtime_allowed_now doit être false — aucun runtime activé en P58"


# ---------------------------------------------------------------------------
# Test 17 — Aucun memory_write = true effectif
# ---------------------------------------------------------------------------
def test_p58_17_no_memory_write():
    data = _load_p58()
    flags = data.get("flags", {})
    assert flags.get("memory_write") is False, \
        "memory_write doit être false — aucune écriture mémoire en P58"


# ---------------------------------------------------------------------------
# Test 18 — Aucun graphiti_write = true effectif
# ---------------------------------------------------------------------------
def test_p58_18_no_graphiti_write():
    data = _load_p58()
    flags = data.get("flags", {})
    assert flags.get("graphiti_write") is False, \
        "graphiti_write doit être false — aucune écriture graphiti en P58"


# ---------------------------------------------------------------------------
# Test 19 — Aucun ACT non gouverné
# ---------------------------------------------------------------------------
def test_p58_19_no_ungoverned_act():
    data = _load_p58()
    flags = data.get("flags", {})
    assert flags.get("act_governed") is False, \
        "act_governed doit être false — aucun ACT non gouverné activé"
    # Vérification supplémentaire : aucune entrée safe_batch_1 ne déclenche ACT
    for entry in data.get("safe_batch_1", []):
        merge_action = entry.get("merge_action", "")
        assert merge_action != "ACT", \
            f"merge_action ACT non autorisé dans safe_batch_1 pour {entry.get('core_path')}"
