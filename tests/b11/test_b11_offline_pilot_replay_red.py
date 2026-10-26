"""
tests/b11/test_b11_offline_pilot_replay_red.py

RED/GREEN Harness for M42/B11 Offline Pilot Deterministic Replay (Phase F3-D8-02).
Resolves F-F3-D8-01:
- Replay-01: Deux invocations indépendantes sur le même lot produisent un JSON canonique et un content_hash bit-exacts.
- Replay-02: Sensibilité sémantique aux entrées : modifier un fait altère le content_hash.
- Replay-03: Préservation de report_id dans l'objet de domaine F2 (pilot_result.comparison_report).
- Replay-04: Distinction claire entre identité d'exécution (report_id distinct) et identité de contenu (content_hash égal).
- Replay-05: Stabilité totale des métriques, verdicts et intervalles statistiques.
- Replay-06: Non-régression sur Omega-9 et les variantes de contrôle (fail-closed, HOLD).

Invariants:
- KX108_ONLY
- UNKNOWN_COMPETENCE
- advisory_only = True
- memory_write = False
- emits_act = False
- kernel_mutation = False
- b12_selection = False
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import pytest

from app.cognition.b11.offline_pilot_assembly import (
    assemble_offline_pilot_v1,
    serialize_assembly_result_canonical_json,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "m42_offline_pilot_v1"


def _load_fixtures() -> tuple[list[dict], list[dict], list[dict]]:
    tasks = json.loads((FIXTURES_DIR / "tasks.json").read_text(encoding="utf-8"))
    canonical_obs = json.loads((FIXTURES_DIR / "canonical_observations.json").read_text(encoding="utf-8"))
    variant_obs = json.loads((FIXTURES_DIR / "variant_observations.json").read_text(encoding="utf-8"))
    return tasks, canonical_obs, variant_obs


# ==============================================================================
# Replay-01: Deux invocations indépendantes produisent un JSON et un hash identiques
# ==============================================================================
def test_replay_01_two_independent_invocations_produce_identical_canonical_json_and_hash():
    """Replay-01: Deux appels indépendants à assemble_offline_pilot_v1 sur le lot nominal

    doivent produire un JSON canonique strictement identique et un content_hash identique.
    Sur l'ancien code, échoue en raison de comparison_report.report_id (uuid.uuid4()).
    """
    tasks, canonical_obs, _ = _load_fixtures()
    t_fl = [t for t in tasks if t["task_id"] == "task-florvaxium-01"]
    o_fl = [o for o in canonical_obs if o["task_id"] == "task-florvaxium-01"]

    r1 = assemble_offline_pilot_v1(o_fl, t_fl)
    r2 = assemble_offline_pilot_v1(o_fl, t_fl)

    s1 = serialize_assembly_result_canonical_json(r1)
    s2 = serialize_assembly_result_canonical_json(r2)

    # Doit être bit-exact
    assert s1 == s2
    assert r1.content_hash == r2.content_hash
    assert r1.content_hash == r1.pilot_result.metadata.get("content_hash", r1.content_hash)


# ==============================================================================
# Replay-02: Sensibilité sémantique aux entrées
# ==============================================================================
def test_replay_02_semantic_change_produces_different_hash():
    """Replay-02: Une modification sémantique des entrées (ex. valeur attendue 15 K au lieu de 12 K)

    doit modifier le content_hash canonique.
    """
    tasks, canonical_obs, _ = _load_fixtures()
    t_fl = [t for t in tasks if t["task_id"] == "task-florvaxium-01"]
    o_fl = [o for o in canonical_obs if o["task_id"] == "task-florvaxium-01"]

    r_nominal = assemble_offline_pilot_v1(o_fl, t_fl)

    # Modifier la tâche
    t_mod = copy.deepcopy(t_fl)
    t_mod[0]["oracle_reference"]["expected_assertion"]["numeric_value"] = 15.0

    r_mod = assemble_offline_pilot_v1(o_fl, t_mod)

    assert r_nominal.content_hash != r_mod.content_hash


# ==============================================================================
# Replay-03: Préservation de report_id dans l'objet de domaine F2
# ==============================================================================
def test_replay_03_report_id_preserved_in_domain_object():
    """Replay-03: L'identifiant report_id original de F2 reste accessible

    dans pilot_result.comparison_report et n'est pas écrasé dans l'objet métier.
    """
    tasks, canonical_obs, _ = _load_fixtures()
    t_fl = [t for t in tasks if t["task_id"] == "task-florvaxium-01"]
    o_fl = [o for o in canonical_obs if o["task_id"] == "task-florvaxium-01"]

    res = assemble_offline_pilot_v1(o_fl, t_fl)
    comp = res.pilot_result.comparison_report

    assert comp is not None
    assert isinstance(comp.report_id, str)
    assert comp.report_id.startswith("rep-emp-")
    assert len(comp.report_id) >= 12


# ==============================================================================
# Replay-04: Distinction identité d'exécution vs identité de contenu
# ==============================================================================
def test_replay_04_execution_id_distinct_while_content_hash_identical():
    """Replay-04: Deux invocations distinctes génèrent deux report_id d'instanciation distincts

    tout en partageant le même content_hash de contenu sémantique.
    """
    tasks, canonical_obs, _ = _load_fixtures()
    t_fl = [t for t in tasks if t["task_id"] == "task-florvaxium-01"]
    o_fl = [o for o in canonical_obs if o["task_id"] == "task-florvaxium-01"]

    r1 = assemble_offline_pilot_v1(o_fl, t_fl)
    r2 = assemble_offline_pilot_v1(o_fl, t_fl)

    comp1 = r1.pilot_result.comparison_report
    comp2 = r2.pilot_result.comparison_report
    assert comp1 is not None and comp2 is not None

    # Les identifiants d'exécution F2 restent distincts
    assert comp1.report_id != comp2.report_id

    # Mais le content_hash sémantique reste rigoureusement identique
    assert r1.content_hash == r2.content_hash


# ==============================================================================
# Replay-05: Stabilité totale des métriques, verdicts et Wilson CIs
# ==============================================================================
def test_replay_05_business_metrics_and_verdicts_stability():
    """Replay-05: L'exclusion de report_id de l'export canonique n'altère aucune métrique métier."""
    tasks, canonical_obs, _ = _load_fixtures()
    t_fl = [t for t in tasks if t["task_id"] == "task-florvaxium-01"]
    o_fl = [o for o in canonical_obs if o["task_id"] == "task-florvaxium-01"]

    r1 = assemble_offline_pilot_v1(o_fl, t_fl)
    r2 = assemble_offline_pilot_v1(o_fl, t_fl)

    assert r1.pilot_result.verdict == r2.pilot_result.verdict == "HARNESS_VALIDATED"
    assert r1.pilot_result.comparison_report.metrics_by_condition == r2.pilot_result.comparison_report.metrics_by_condition
    assert r1.pilot_result.comparison_report.pairwise_comparisons == r2.pilot_result.comparison_report.pairwise_comparisons

    v1 = [t.evaluation_result.get("verdict") for t in r1.pilot_result.normalized_trials]
    v2 = [t.evaluation_result.get("verdict") for t in r2.pilot_result.normalized_trials]
    assert v1 == v2 == ["EVAL_PASS", "EVAL_PASS", "EVAL_PASS"]


# ==============================================================================
# Replay-06: Non-régression sur Omega-9 et les variantes de contrôle
# ==============================================================================
def test_replay_06_non_regression_omega9_and_variants():
    """Replay-06: Omega-9 et la variante de version discordante conservent

    leur comportement fail-closed (HOLD, comparison_report=None, INDETERMINATE).
    """
    tasks, canonical_obs, variant_obs = _load_fixtures()

    # Omega-9
    t_om = [t for t in tasks if t["task_id"] == "task-omega9-01"]
    o_om = [o for o in canonical_obs if o["task_id"] == "task-omega9-01"]
    r_om1 = assemble_offline_pilot_v1(o_om, t_om)
    r_om2 = assemble_offline_pilot_v1(o_om, t_om)

    assert r_om1.content_hash == r_om2.content_hash
    assert r_om1.pilot_result.comparison_report is None
    for tr in r_om1.pilot_result.normalized_trials:
        assert tr.evaluation_result.get("verdict") == "INDETERMINATE"
        assert tr.evaluation_result.get("evaluator") == "OfflinePilotAssemblyPolicyGuardV1"

    # V3 Mismatch
    t_fl = [t for t in tasks if t["task_id"] == "task-florvaxium-01"]
    o_v3 = [o for o in canonical_obs if o["task_id"] == "task-florvaxium-01" and o["condition"] == "STACK_ONLY"] + [o for o in variant_obs if o["trial_id"] == "tr-mismatch-01"]
    r_v3 = assemble_offline_pilot_v1(o_v3, t_fl)
    assert r_v3.pilot_result.verdict == "HOLD"
    assert "ORACLE_VERSION_MISMATCH" in r_v3.pilot_result.hold_reasons
    assert r_v3.pilot_result.comparison_report is None
