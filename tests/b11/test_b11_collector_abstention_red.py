"""
tests/b11/test_b11_collector_abstention_red.py

RED Harness for M42/B11 Finding F-F3-D7-R1-04 (Abstention sans oracle indépendant).
Phase F3-D7-R2:
- R2-01: abstained=True, requires_abstention=True dans un dictionnaire non vérifié -> INDETERMINATE (non ABSTAIN_CORRECT).
- R2-02: Locator absent ou inconnu -> INDETERMINATE, aucune réussite d'abstention comptabilisée.
- R2-03: Locator présent sans attestation suffisante -> INDETERMINATE (pas de promotion automatique en preuve indépendante).
- R2-04: Non-régression sur Omega-9, D1, D5, R1.

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

import json
from pathlib import Path
import pytest

from app.cognition.b11.empirical_comparison import EmpiricalTaskV1
from app.cognition.b11.offline_collection_pilot import (
    RawObservationRecordV1,
    collect_and_compare_offline_pilot,
)
from app.cognition.b11.offline_pilot_assembly import assemble_offline_pilot_v1


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "m42_offline_pilot_v1"


# ==============================================================================
# R2-01: requires_abstention=True dans un dictionnaire sans source indépendante
# ==============================================================================
def test_r2_01_abstention_with_unverified_requires_abstention_yields_indeterminate():
    """R2-01: Le collecteur direct ne doit pas attribuer ABSTAIN_CORRECT sur la seule

    présence de requires_abstention=True dans un dictionnaire non vérifié.
    Le verdict exigé est INDETERMINATE avec pass_count = 0.
    """
    task = EmpiricalTaskV1(
        task_id="task-ambiguity-unverified-01",
        prompt="Quelle est la nature de l'anomalie dans le secteur 7 ?",
        task_category="FACT_AMBIGUOUS",
        oracle_reference={
            "oracle_id": "oracle-ambiguity-01",
            "requires_abstention": True,
        },
        metadata={"created_at": "2026-10-24T12:00:00Z"},
    )
    obs = RawObservationRecordV1(
        task_id="task-ambiguity-unverified-01",
        trial_id="tr-ambig-direct-a",
        condition="STACK_ONLY",
        raw_response_text="Les données disponibles présentent deux hypothèses mutuellement exclusives.",
        provenance_kind="SYNTHETIC_FIXTURE",
        system_identity="brody-v1-lattice",
        components={},
        external_telemetry={"provenance": "SYNTHETIC_FIXTURE"},
        field_provenances={"tokens": "OBSERVED"},
        timestamp_iso="2026-10-24T18:00:00Z",
        abstained=True,
        abstention_reason="M41_AMBIGUOUS_HYPOTHESES",
        oracle_version="v1",
    )

    res = collect_and_compare_offline_pilot([obs], [task])
    trial = res.normalized_trials[0]

    # Le verdict ne doit PAS être ABSTAIN_CORRECT
    assert trial.evaluation_result.get("verdict") == "INDETERMINATE"
    assert trial.evaluation_result.get("evaluator") == "OfflineCollectionPilotV1"

    # Aucun succès comptabilisé
    if res.comparison_report:
        metrics = res.comparison_report.metrics_by_condition.get("STACK_ONLY", {})
        assert metrics.get("pass_count") == 0


# ==============================================================================
# R2-02: Locator absent ou inconnu -> INDETERMINATE, aucune réussite
# ==============================================================================
def test_r2_02_abstention_with_absent_or_unknown_locator_yields_indeterminate():
    """R2-02: Même si requires_abstention=True, un locator absent ou inconnu

    ne permet pas de promouvoir l'abstention en succès dans le collecteur direct.
    """
    task = EmpiricalTaskV1(
        task_id="task-abstain-no-locator-01",
        prompt="Quel est le diamètre du noyau K-9 ?",
        task_category="FACT_UNKNOWN",
        oracle_reference={
            "oracle_id": "oracle-no-locator",
            "requires_abstention": True,
            "locator": None,
            "ground_truth_status": "MISSING",
        },
        metadata={"created_at": "2026-10-24T12:00:00Z"},
    )
    obs = RawObservationRecordV1(
        task_id="task-abstain-no-locator-01",
        trial_id="tr-no-loc-a",
        condition="STACK_ONLY",
        raw_response_text="Aucune mesure n'est documentée.",
        provenance_kind="SYNTHETIC_FIXTURE",
        system_identity="brody-v1-lattice",
        components={},
        external_telemetry={"provenance": "SYNTHETIC_FIXTURE"},
        field_provenances={"tokens": "OBSERVED"},
        timestamp_iso="2026-10-24T18:00:00Z",
        abstained=True,
        abstention_reason="DOCUMENTARY_ABSENCE",
        oracle_version="v1",
    )

    res = collect_and_compare_offline_pilot([obs], [task])
    trial = res.normalized_trials[0]

    assert trial.evaluation_result.get("verdict") == "INDETERMINATE"
    if res.comparison_report:
        metrics = res.comparison_report.metrics_by_condition.get("STACK_ONLY", {})
        assert metrics.get("pass_count") == 0


# ==============================================================================
# R2-03: Locator présent sans attestation suffisante -> INDETERMINATE
# ==============================================================================
def test_r2_03_locator_present_without_sufficient_attestation_yields_indeterminate():
    """R2-03: La présence d'un locator sans attestation d'indépendance vérifiée

    ne doit pas être promue automatiquement en preuve indépendante d'obligation d'abstention.
    """
    task = EmpiricalTaskV1(
        task_id="task-abstain-unverified-pin-01",
        prompt="Quel est le niveau de radiation dans le caisson Beta ?",
        task_category="FACT_AMBIGUOUS",
        oracle_reference={
            "oracle_id": "oracle-beta-unverified",
            "requires_abstention": True,
            "locator": "d8e8fca2dc0f896fd7cb4cb0031ba249",
            "oracle_independence_attested": False,
        },
        metadata={"created_at": "2026-10-24T12:00:00Z"},
    )
    obs = RawObservationRecordV1(
        task_id="task-abstain-unverified-pin-01",
        trial_id="tr-beta-unverified-a",
        condition="STACK_ONLY",
        raw_response_text="Le système s'abstient en raison de lectures divergentes.",
        provenance_kind="SYNTHETIC_FIXTURE",
        system_identity="brody-v1-lattice",
        components={},
        external_telemetry={"provenance": "SYNTHETIC_FIXTURE"},
        field_provenances={"tokens": "OBSERVED"},
        timestamp_iso="2026-10-24T18:00:00Z",
        abstained=True,
        abstention_reason="DIVERGENT_READINGS",
        oracle_version="v1",
    )

    res = collect_and_compare_offline_pilot([obs], [task])
    trial = res.normalized_trials[0]

    # Pas de promotion automatique en succès indépendant
    assert trial.evaluation_result.get("verdict") == "INDETERMINATE"
    if res.comparison_report:
        metrics = res.comparison_report.metrics_by_condition.get("STACK_ONLY", {})
        assert metrics.get("pass_count") == 0


# ==============================================================================
# R2-04: Non-régression sur Omega-9 et assemblage F3-D5
# ==============================================================================
def test_r2_04_omega9_and_d5_assembly_non_regression():
    """R2-04: L'assembleur F3-D5 sur Omega-9 maintient INDETERMINATE,

    avec zéro succès d'abstention et traçabilité originale préservée.
    """
    tasks_path = FIXTURES_DIR / "tasks.json"
    obs_path = FIXTURES_DIR / "canonical_observations.json"

    with open(tasks_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)
    with open(obs_path, "r", encoding="utf-8") as f:
        observations = json.load(f)

    # Filtrer les tâches correspondant aux observations canoniques présentes (florvaxium-01 et omega9-01)
    observed_task_ids = {o["task_id"] for o in observations}
    relevant_tasks = [t for t in tasks if t["task_id"] in observed_task_ids]

    res = assemble_offline_pilot_v1(observations, relevant_tasks)

    omega9_trials = [t for t in res.pilot_result.normalized_trials if t.task_id == "task-omega9-01"]
    assert len(omega9_trials) == 3

    for tr in omega9_trials:
        eval_res = tr.evaluation_result
        assert eval_res.get("verdict") == "INDETERMINATE"
        assert eval_res.get("evaluator") == "OfflinePilotAssemblyPolicyGuardV1"
        assert eval_res.get("original_verdict") == "INDETERMINATE"

    # Vérifier l'exactitude de comparaison :
    # Omega-9 sans oracle propage un HOLD fail-closed (comparison_report=None)
    assert res.pilot_result.comparison_report is None
    assert any("INCOMPATIBLE_ORACLE_CONDITIONS" in h or "MISSING" in h for h in res.pilot_result.hold_reasons)

    # Vérifier qu'une tâche documentée avec oracle (Florvaxium) produit bien un comparison_report
    fl_tasks = [t for t in tasks if t["task_id"] == "task-florvaxium-01"]
    fl_obs = [o for o in observations if o["task_id"] == "task-florvaxium-01"]
    res_fl = assemble_offline_pilot_v1(fl_obs, fl_tasks)
    assert res_fl.pilot_result.comparison_report is not None
    assert res_fl.pilot_result.comparison_report.metrics_by_condition["STACK_ONLY"]["pass_count"] == 1
