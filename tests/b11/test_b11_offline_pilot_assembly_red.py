"""
tests/b11/test_b11_offline_pilot_assembly_red.py

RED Harness for M42/B11 Offline Pilot Canonical Assembly (Phase F3-D5).
Tests the contractual interfaces of:
- OfflinePilotAssemblyResultV1
- assemble_offline_pilot_v1
- serialize_assembly_result_canonical_json

Invariants:
- KX108_ONLY
- UNKNOWN_COMPETENCE
- advisory_only = True
- memory_write = False
- emits_act = False
- kernel_mutation = False
- b12_selection = False

Zero network calls, zero file mutations, zero runtime implementation during Phase F3-D5.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any
import pytest

# Target module to be implemented in Phase F3-D6
from app.cognition.b11.offline_pilot_assembly import (  # type: ignore[import-not-found]
    OfflinePilotAssemblyResultV1,
    assemble_offline_pilot_v1,
    serialize_assembly_result_canonical_json,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "m42_offline_pilot_v1"


def _load_json(filename: str) -> list[dict[str, Any]]:
    path = FIXTURES_DIR / filename
    assert path.is_file(), f"Fixture file not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list), f"Expected list in {filename}, got {type(data)}"
    return data


# ==============================================================================
# Fixture Sanity Pre-assertions
# ==============================================================================
def test_d5_pre_fixtures_validity():
    """Verify that required JSON fixtures exist and contain well-formed tasks and observations."""
    tasks = _load_json("tasks.json")
    canonical_obs = _load_json("canonical_observations.json")
    variant_obs = _load_json("variant_observations.json")

    assert len(tasks) == 3
    assert len(canonical_obs) == 6
    assert len(variant_obs) == 3

    florvaxium_task = next(t for t in tasks if t["task_id"] == "task-florvaxium-01")
    assert florvaxium_task["oracle_reference"]["locator"] == "16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b"
    assert florvaxium_task["oracle_reference"]["expected_assertion"]["numeric_value"] == 12.0

    # Ensure condition A in fixtures is qualified as SYNTHETIC_FIXTURE (F-F3-D5-REV-02)
    fl_obs_a = next(o for o in canonical_obs if o["trial_id"] == "tr-florvaxium-01-a")
    assert fl_obs_a["provenance_kind"] == "SYNTHETIC_FIXTURE"


# ==============================================================================
# D5-01: Assemblage A/B/C d'une tâche Florvaxium, avec identifiants appariés
# ==============================================================================
def test_d5_01_florvaxium_abc_assembly():
    """D5-01: Assembling conditions A, B, and C for Florvaxium produces valid 3-trial assembly."""
    tasks = [t for t in _load_json("tasks.json") if t["task_id"] == "task-florvaxium-01"]
    obs = [o for o in _load_json("canonical_observations.json") if o["task_id"] == "task-florvaxium-01"]

    res = assemble_offline_pilot_v1(obs, tasks)
    assert isinstance(res, OfflinePilotAssemblyResultV1)
    assert res.schema == "OFFLINE_PILOT_ASSEMBLY_RESULT_V1"
    assert res.assembled_tasks_count == 1
    assert res.assembled_trials_count == 3
    assert res.pilot_result.unique_tasks_count == 1
    assert res.pilot_result.independent_facts_count == 1
    assert res.pilot_result.verdict == "HARNESS_VALIDATED"
    assert res.pilot_result.comparison_report is not None

    # Check that all 3 conditions PASS against 12.0 K oracle
    verdicts = [t.evaluation_result.get("verdict") for t in res.pilot_result.normalized_trials]
    assert verdicts == ["EVAL_PASS", "EVAL_PASS", "EVAL_PASS"]


# ==============================================================================
# D5-02: Une contradiction connue produit un verdict E3 admissible
# ==============================================================================
def test_d5_02_contradiction_produces_admissible_fail():
    """D5-02: Known numeric contradiction (99 K vs expected 12 K) yields EVAL_FAIL."""
    tasks = [t for t in _load_json("tasks.json") if t["task_id"] == "task-florvaxium-01"]
    obs = [o for o in _load_json("variant_observations.json") if o["trial_id"] == "tr-contradiction-01"]

    res = assemble_offline_pilot_v1(obs, tasks)
    assert res.assembled_trials_count == 1
    trial = res.pilot_result.normalized_trials[0]
    assert trial.evaluation_result.get("verdict") == "EVAL_FAIL"


# ==============================================================================
# D5-03: Un inconnu sans oracle ne produit aucune fausse vérité terrain (F-F3-D5-REV-01)
# ==============================================================================
def test_d5_03_unknown_without_oracle_no_false_truth():
    """D5-03: Fact without oracle produces INDETERMINATE for both abstained and non-abstained responses."""
    tasks = [t for t in _load_json("tasks.json") if t["task_id"] == "task-omega9-01"]
    obs = [o for o in _load_json("canonical_observations.json") if o["task_id"] == "task-omega9-01"]

    res = assemble_offline_pilot_v1(obs, tasks)
    trials_by_cond = {t.condition: t for t in res.pilot_result.normalized_trials}

    # Under E3, without an oracle requiring abstention or M41 bundle,
    # abstained and non-abstained both yield INDETERMINATE (ground truth missing)
    assert trials_by_cond["STACK_ONLY"].evaluation_result.get("verdict") == "INDETERMINATE"
    assert trials_by_cond["QWEN_ONLY"].evaluation_result.get("verdict") == "INDETERMINATE"

    # Oracle independence audit must be False
    task_audit = res.pilot_result.metadata.get("task_audit", {}).get("task-omega9-01", {})
    assert task_audit.get("oracle_independence_attested") is False


# ==============================================================================
# D5-04: Les sorties Qwen simulées restent MOCKED_EXTERNAL
# ==============================================================================
def test_d5_04_simulated_qwen_remains_mocked_external():
    """D5-04: Simulated Qwen outputs must carry MOCKED_EXTERNAL and force HARNESS_VALIDATED."""
    tasks = [t for t in _load_json("tasks.json") if t["task_id"] == "task-florvaxium-01"]
    obs = [o for o in _load_json("canonical_observations.json") if o["condition"] in ("STACK_PLUS_QWEN", "QWEN_ONLY") and o["task_id"] == "task-florvaxium-01"]

    res = assemble_offline_pilot_v1(obs, tasks)
    for trial in res.pilot_result.normalized_trials:
        assert trial.is_mock is True
        assert trial.external_telemetry.get("provenance") == "MOCKED_EXTERNAL"

    assert res.pilot_result.verdict == "HARNESS_VALIDATED"


# ==============================================================================
# D5-05: Deux formulations du même fait ne gonflent pas independent_facts_count
# ==============================================================================
def test_d5_05_two_reformulations_do_not_inflate_independent_facts():
    """D5-05: 2 prompt variants on the same oracle fact yield 2 tasks but 1 independent fact."""
    tasks = [t for t in _load_json("tasks.json") if t["task_id"] in ("task-florvaxium-01", "task-florvaxium-02")]
    obs_1 = [o for o in _load_json("canonical_observations.json") if o["trial_id"] == "tr-florvaxium-01-a"]
    obs_2 = [o for o in _load_json("variant_observations.json") if o["trial_id"] == "tr-florvaxium-02-a"]

    res = assemble_offline_pilot_v1(obs_1 + obs_2, tasks)
    assert res.assembled_tasks_count == 2
    assert res.pilot_result.unique_tasks_count == 2
    assert res.pilot_result.independent_facts_count == 1


# ==============================================================================
# D5-06: Une différence de version d'oracle entraîne HOLD et comparison_report=None
# ==============================================================================
def test_d5_06_oracle_version_mismatch_yields_hold():
    """D5-06: Trials on same task with conflicting oracle versions force HOLD and comparison_report=None."""
    tasks = [t for t in _load_json("tasks.json") if t["task_id"] == "task-florvaxium-01"]
    obs_v1 = [o for o in _load_json("canonical_observations.json") if o["trial_id"] == "tr-florvaxium-01-a"]
    obs_v2 = [o for o in _load_json("variant_observations.json") if o["trial_id"] == "tr-mismatch-01"]

    res = assemble_offline_pilot_v1(obs_v1 + obs_v2, tasks)
    assert res.pilot_result.verdict == "HOLD"
    assert "ORACLE_VERSION_MISMATCH" in res.pilot_result.hold_reasons
    assert res.pilot_result.comparison_report is None


# ==============================================================================
# D5-07: Observation synthétique condition A conserve sa qualification (F-F3-D5-REV-02)
# ==============================================================================
def test_d5_07_synthetic_fixture_preserves_qualification():
    """D5-07: SYNTHETIC_FIXTURE carries is_mock=True without claiming on-disk physical recording."""
    tasks = [t for t in _load_json("tasks.json") if t["task_id"] == "task-florvaxium-01"]
    obs = [o for o in _load_json("canonical_observations.json") if o["trial_id"] == "tr-florvaxium-01-a"]

    res = assemble_offline_pilot_v1(obs, tasks)
    trial = res.pilot_result.normalized_trials[0]
    assert trial.is_mock is True
    assert trial.external_telemetry.get("provenance") == "SYNTHETIC_FIXTURE"
    assert "VerificationRecord" not in str(res.metadata)


# ==============================================================================
# D5-08: Les champs absents restent UNAVAILABLE sans coût ou latence inventés
# ==============================================================================
def test_d5_08_unavailable_fields_preserved():
    """D5-08: Absent cost telemetry remains UNAVAILABLE without fabricating financial metrics."""
    tasks = [t for t in _load_json("tasks.json") if t["task_id"] == "task-florvaxium-01"]
    obs = [o for o in _load_json("canonical_observations.json") if o["task_id"] == "task-florvaxium-01"]

    res = assemble_offline_pilot_v1(obs, tasks)
    field_audit = res.pilot_result.metadata.get("field_provenance_audit", {})
    assert field_audit.get("cost") == "UNAVAILABLE"
    assert "cost_usd" not in res.export_payload or res.export_payload.get("cost_usd") is None


# ==============================================================================
# D5-09: Sérialisation canonique reproductible et acyclique (F-F3-D5-REV-03)
# ==============================================================================
def test_d5_09_canonical_serialization_reproducibility():
    """D5-09: Canonical serialization is acyclic and produces deterministic JSON with matching SHA256."""
    tasks = [t for t in _load_json("tasks.json") if t["task_id"] == "task-florvaxium-01"]
    obs = [o for o in _load_json("canonical_observations.json") if o["task_id"] == "task-florvaxium-01"]

    res = assemble_offline_pilot_v1(obs, tasks)

    # Acyclicity: export_payload does NOT contain content_hash
    assert "content_hash" not in res.export_payload

    json_str_1 = serialize_assembly_result_canonical_json(res)
    json_str_2 = serialize_assembly_result_canonical_json(res)

    assert json_str_1 == json_str_2
    expected_hash = hashlib.sha256(json_str_1.encode("utf-8")).hexdigest()
    assert res.content_hash == expected_hash
    # Content hash must not be claimed as an external signature
    assert "external_signature" not in res.export_payload


# ==============================================================================
# D5-10: Pureté, immutabilité et conservation des invariants KX108
# ==============================================================================
def test_d5_10_purity_and_kx108_invariants(monkeypatch):
    """D5-10: assemble_offline_pilot_v1 is pure: zero network, input immutability, KX108_ONLY."""
    import socket

    def _block_net(*args, **kwargs):
        raise RuntimeError("NETWORK_ACCESS_FORBIDDEN")

    monkeypatch.setattr(socket, "socket", _block_net)

    tasks = _load_json("tasks.json")
    obs = _load_json("canonical_observations.json")

    tasks_copy = copy.deepcopy(tasks)
    obs_copy = copy.deepcopy(obs)

    res = assemble_offline_pilot_v1(obs, tasks)
    assert tasks == tasks_copy
    assert obs == obs_copy

    assert res.pilot_result.decision_authority == "KX108_ONLY"
    assert res.pilot_result.competence_regime == "UNKNOWN_COMPETENCE"
    assert res.pilot_result.advisory_only is True
