"""
tests/b11/test_b11_collector_e3_provenance_red.py

RED Harness for M42/B11 Source Collector and E3 Provenance Correction (Phase F3-D7-R1).
Demonstrates:
- R1-01: Direct collector call with abstained=True and oracle_reference=None must yield INDETERMINATE (not ABSTAIN_CORRECT).
- R1-02: Evaluator field provenance must reflect actual execution (OfflineCollectionPilotV1 / OfflinePilotAssemblyPolicyGuardV1) instead of fabricating BrodyIndependentEvaluatorV1 without E3 execution.
- R1-03: Assembler guard remains defensive and compatible with D5-03.

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

import pytest

from app.cognition.b11.empirical_comparison import EmpiricalTaskV1
from app.cognition.b11.offline_collection_pilot import (
    RawObservationRecordV1,
    collect_and_compare_offline_pilot,
)
from app.cognition.b11.offline_pilot_assembly import assemble_offline_pilot_v1


# ==============================================================================
# R1-01: Direct collector call with abstained=True on unpinned task without oracle
# ==============================================================================
def test_r1_01_direct_collector_abstention_without_oracle_yields_indeterminate():
    """R1-01: Calling collect_and_compare_offline_pilot directly on an unpinned task without oracle

    must NOT produce ABSTAIN_CORRECT. It must produce INDETERMINATE with 0 pass_count.
    """
    task = EmpiricalTaskV1(
        task_id="task-omega9-01",
        prompt="Quelle est la concentration de florvaxium dans le secteur Omega-9 ?",
        task_category="FACT_UNKNOWN",
        oracle_reference=None,
        metadata={"created_at": "2026-10-24T12:00:00Z"},
    )
    obs = RawObservationRecordV1(
        task_id="task-omega9-01",
        trial_id="tr-omega9-direct-a",
        condition="STACK_ONLY",
        raw_response_text="L'information concernant le secteur Omega-9 n'est pas établie dans le corpus.",
        provenance_kind="SYNTHETIC_FIXTURE",
        system_identity="brody-v1-lattice",
        components={},
        external_telemetry={"provenance": "SYNTHETIC_FIXTURE"},
        field_provenances={"tokens": "OBSERVED", "cost": "UNAVAILABLE"},
        timestamp_iso="2026-10-24T18:00:00Z",
        abstained=True,
        abstention_reason="CORPUS_ABSENCE",
        oracle_version="v1",
    )

    res = collect_and_compare_offline_pilot([obs], [task])
    trial = res.normalized_trials[0]

    # Must NOT be ABSTAIN_CORRECT
    assert trial.evaluation_result.get("verdict") == "INDETERMINATE"

    # Comparison report must not award a pass
    if res.comparison_report:
        accuracy = res.comparison_report.accuracy_by_condition.get("STACK_ONLY", {})
        assert accuracy.get("pass_count") == 0


# ==============================================================================
# R1-02: Evaluator field provenance distinguishes actual execution
# ==============================================================================
def test_r1_02_evaluator_provenance_distinguishes_collector_from_e3():
    """R1-02: Evaluator label must not claim BrodyIndependentEvaluatorV1 when E3 was not executed.

    Collector must identify as OfflineCollectionPilotV1.
    Assembly policy guard must identify as OfflinePilotAssemblyPolicyGuardV1.
    """
    task = EmpiricalTaskV1(
        task_id="task-florvaxium-01",
        prompt="Quelle est la température de florvaxium ?",
        task_category="FACT_KNOWN",
        oracle_reference={
            "oracle_id": "oracle-florvaxium-01",
            "locator": "16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b",
            "ground_truth_provenance": "B8_PINNED_DOCUMENT",
            "expected_assertion": {
                "symbol": "florvaxium",
                "property": "temperature",
                "numeric_value": 12.0,
                "unit": "K",
            },
        },
        metadata={"created_at": "2026-10-24T12:00:00Z"},
    )
    obs = RawObservationRecordV1(
        task_id="task-florvaxium-01",
        trial_id="tr-fl-direct-a",
        condition="STACK_ONLY",
        raw_response_text="La température de florvaxium est de 12 K.",
        provenance_kind="SYNTHETIC_FIXTURE",
        system_identity="brody-v1-lattice",
        components={},
        external_telemetry={"provenance": "SYNTHETIC_FIXTURE"},
        field_provenances={"tokens": "OBSERVED", "cost": "UNAVAILABLE"},
        timestamp_iso="2026-10-24T18:00:00Z",
        abstained=False,
        abstention_reason=None,
        oracle_version="v1",
    )

    res = collect_and_compare_offline_pilot([obs], [task])
    trial = res.normalized_trials[0]

    # Evaluator in collector must NOT claim full E3 execution
    assert trial.evaluation_result.get("evaluator") == "OfflineCollectionPilotV1"


# ==============================================================================
# R1-03: Assembly policy guard identifies as OfflinePilotAssemblyPolicyGuardV1
# ==============================================================================
def test_r1_03_assembler_guard_remains_defensive_and_identifies_policy_guard():
    """R1-03: When assembler guards a trial without oracle, it labels evaluator as OfflinePilotAssemblyPolicyGuardV1."""
    task_dict = {
        "task_id": "task-omega9-01",
        "prompt": "Quelle est la concentration de florvaxium dans le secteur Omega-9 ?",
        "task_category": "FACT_UNKNOWN",
        "oracle_reference": None,
        "metadata": {"created_at": "2026-10-24T12:00:00Z"},
    }
    obs_dict = {
        "task_id": "task-omega9-01",
        "trial_id": "tr-omega9-guard-a",
        "condition": "STACK_ONLY",
        "raw_response_text": "L'information n'est pas établie.",
        "provenance_kind": "SYNTHETIC_FIXTURE",
        "system_identity": "brody-v1-lattice",
        "components": {},
        "external_telemetry": {"provenance": "SYNTHETIC_FIXTURE"},
        "field_provenances": {"cost": "UNAVAILABLE"},
        "timestamp_iso": "2026-10-24T18:00:00Z",
        "abstained": True,
        "abstention_reason": "CORPUS_ABSENCE",
        "oracle_version": "v1",
    }

    res = assemble_offline_pilot_v1([obs_dict], [task_dict])
    trial = res.pilot_result.normalized_trials[0]

    assert trial.evaluation_result.get("verdict") == "INDETERMINATE"
    assert trial.evaluation_result.get("evaluator") == "OfflinePilotAssemblyPolicyGuardV1"
