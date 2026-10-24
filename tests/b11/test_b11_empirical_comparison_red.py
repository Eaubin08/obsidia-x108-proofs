"""
tests/b11/test_b11_empirical_comparison_red.py

RED Harness for M42/B11 Empirical Comparison Protocol V1.
Tests the contractual interfaces of:
- EmpiricalTaskV1
- EmpiricalTrialReceiptV1
- EmpiricalComparisonReportV1
- compare_empirical_trials

Invariants:
- KX108_ONLY
- UNKNOWN_COMPETENCE
- advisory_only=True
- memory_write=False
- emits_act=False
- kernel_mutation=False
- b12_selection=False

Zero network calls, zero file mutations, zero runtime implementation during Phase F1.
"""
from __future__ import annotations

import copy
from typing import Any
import pytest

# Target module to be implemented in Phase F2
from app.cognition.b11.empirical_comparison import (  # type: ignore[import-not-found]
    EmpiricalConditionV1,
    EmpiricalTaskV1,
    EmpiricalTrialReceiptV1,
    EmpiricalComparisonReportV1,
    compare_empirical_trials,
)


# ==============================================================================
# Helper fixtures
# ==============================================================================

def _make_task(
    task_id: str = "task-001",
    prompt: str = "Quelle est la température de florvaxium ?",
    task_category: str = "FACT_KNOWN",
    locator: str = "16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b",
    expected_value: float = 12.0,
    unit: str = "K",
    provenance: str = "B8_PINNED_DOCUMENT",
) -> EmpiricalTaskV1:
    return EmpiricalTaskV1(
        task_id=task_id,
        prompt=prompt,
        task_category=task_category,
        oracle_reference={
            "oracle_id": f"oracle-{task_id}",
            "locator": locator,
            "ground_truth_provenance": provenance,
            "expected_assertion": {
                "symbol": "florvaxium",
                "property": "temperature",
                "numeric_value": expected_value,
                "unit": unit,
            },
        },
        metadata={"created_at": "2026-10-24T12:00:00Z"},
    )


def _make_trial(
    trial_id: str,
    task_id: str,
    condition: EmpiricalConditionV1,
    response_text: str = "La température de florvaxium est de 12 K.",
    abstained: bool = False,
    abstention_reason: str | None = None,
    verdict: str = "EVAL_PASS",
    model_calls: int = 0,
    external_provenance: str = "NONE",
    external_received: bool = False,
    external_admitted: bool = False,
    is_mock: bool = True,
) -> EmpiricalTrialReceiptV1:
    return EmpiricalTrialReceiptV1(
        trial_id=trial_id,
        task_id=task_id,
        condition=condition,
        system_version="brody-m42-b11-v1",
        observable_response_text=response_text,
        abstained=abstained,
        abstention_reason=abstention_reason,
        external_telemetry={
            "external_called": model_calls > 0,
            "external_received": external_received,
            "external_admitted": external_admitted,
            "provenance": external_provenance,
            "model_calls": model_calls,
            "prompt_tokens": 15 if model_calls > 0 else 0,
            "completion_tokens": 20 if model_calls > 0 else 0,
            "latency_ms": 42.5 if model_calls > 0 else 2.1,
        },
        evaluation_result={
            "verdict": verdict,
            "evaluator": "BrodyIndependentEvaluatorV1",
            "reasons": [],
        },
        is_mock=is_mock,
        timestamp_iso="2026-10-24T12:00:01Z",
    )


# ==============================================================================
# F1-01: Même tâche, mêmes références, trois conditions distinctes (A, B, C)
# ==============================================================================
def test_f1_01_same_task_three_conditions_paired():
    """F1-01: A single task must be evaluable across A, B, and C with paired metrics."""
    task = _make_task("task-01")
    t_a = _make_trial("tr-01-a", "task-01", "STACK_ONLY", response_text="Température: 12 K.", verdict="EVAL_PASS")
    t_b = _make_trial("tr-01-b", "task-01", "STACK_PLUS_QWEN", response_text="Température: 12 K.", verdict="EVAL_PASS", model_calls=1, external_provenance="MOCKED_EXTERNAL", external_received=True, external_admitted=True)
    t_c = _make_trial("tr-01-c", "task-01", "QWEN_ONLY", response_text="Température estimée à 12 K.", verdict="EVAL_PASS", model_calls=1, external_provenance="MOCKED_EXTERNAL", external_received=True, external_admitted=True)

    report = compare_empirical_trials([t_a, t_b, t_c], [task])
    assert isinstance(report, EmpiricalComparisonReportV1)
    assert report.total_tasks == 1
    assert report.total_trials == 3
    assert set(report.metrics_by_condition.keys()) == {"STACK_ONLY", "STACK_PLUS_QWEN", "QWEN_ONLY"}
    assert report.metrics_by_condition["STACK_ONLY"]["pass_count"] == 1
    assert report.metrics_by_condition["STACK_PLUS_QWEN"]["pass_count"] == 1
    assert report.metrics_by_condition["QWEN_ONLY"]["pass_count"] == 1


# ==============================================================================
# F1-02: Refus d'un oracle produit à partir de la réponse évaluée
# ==============================================================================
def test_f1_02_refuse_circular_oracle():
    """F1-02: Oracles derived from candidate output must be strictly rejected."""
    circular_task = _make_task(
        "task-circular",
        provenance="CANDIDATE_OUTPUT",  # Forbidden circular ground truth
    )
    trial = _make_trial("tr-circ", "task-circular", "STACK_ONLY")

    with pytest.raises(ValueError, match="INVALID_CIRCULAR_ORACLE"):
        compare_empirical_trials([trial], [circular_task])


# ==============================================================================
# F1-03: Correspondance stricte des task_id pour comparaison appariée
# ==============================================================================
def test_f1_03_strict_task_id_matching_for_pairing():
    """F1-03: Trials on differing task_ids cannot be paired in pairwise comparisons."""
    task_1 = _make_task("task-01")
    task_2 = _make_task("task-02")
    t_a = _make_trial("tr-a", "task-01", "STACK_ONLY")
    t_b = _make_trial("tr-b", "task-02", "STACK_PLUS_QWEN")  # Mismatched task_id

    report = compare_empirical_trials([t_a, t_b], [task_1, task_2])
    pair_ab = report.pairwise_comparisons.get("STACK_ONLY_vs_STACK_PLUS_QWEN", {})
    assert pair_ab.get("paired_tasks_count", 0) == 0
    assert "UNPAIRED_TASK" in report.hold_reasons or pair_ab.get("status") == "UNPAIRED_TASKS"


# ==============================================================================
# F1-04: Interdiction de compter des répétitions comme des tâches indépendantes
# ==============================================================================
def test_f1_04_repetitions_do_not_inflate_sample_size():
    """F1-04: 5 trials on the same task_id must count as N=1 task, not N=5 tasks."""
    task = _make_task("task-repeated")
    trials = [
        _make_trial(f"tr-rep-{i}", "task-repeated", "STACK_PLUS_QWEN", model_calls=1)
        for i in range(5)
    ]
    report = compare_empirical_trials(trials, [task])
    assert report.total_tasks == 1
    assert report.total_trials == 5
    # Statistical sample size for inferential comparisons must remain 1
    pair_metrics = report.metrics_by_condition["STACK_PLUS_QWEN"]
    assert pair_metrics["sample_size_tasks"] == 1
    assert pair_metrics["total_runs"] == 5


# ==============================================================================
# F1-05: Aucune contribution causale attribuée au seul model_calls > 0
# ==============================================================================
def test_f1_05_no_causal_contribution_from_model_calls_alone():
    """F1-05: model_calls > 0 without answer change or performance diff yields CAUSAL_EFFECT_SUPPORTED=False."""
    task = _make_task("task-causal-test")
    # Condition A: PASS without Qwen
    t_a = _make_trial("tr-a", "task-causal-test", "STACK_ONLY", response_text="Florvaxium: 12 K.", verdict="EVAL_PASS")
    # Condition B: Called Qwen, but answer is identical and verdict unchanged
    t_b = _make_trial(
        "tr-b", "task-causal-test", "STACK_PLUS_QWEN",
        response_text="Florvaxium: 12 K.", verdict="EVAL_PASS",
        model_calls=1, external_provenance="MOCKED_EXTERNAL", external_received=True, external_admitted=True
    )
    report = compare_empirical_trials([t_a, t_b], [task])
    causal = report.causal_attribution.get("STACK_PLUS_QWEN", {})
    assert causal.get("external_called") is True
    assert causal.get("answer_changed") is False
    assert causal.get("performance_difference_observed") is False
    assert causal.get("causal_effect_supported") is False


# ==============================================================================
# F1-06: Distinction MOCKED_EXTERNAL et REAL_EXTERNAL
# ==============================================================================
def test_f1_06_mocked_vs_real_provenance_distinction():
    """F1-06: Mocked external telemetry forces protocol_level='HARNESS_VALIDATED' and marks contains_mocked_data=True."""
    task = _make_task("task-mock-check")
    t_mock = _make_trial("tr-mock", "task-mock-check", "STACK_PLUS_QWEN", is_mock=True, external_provenance="MOCKED_EXTERNAL", model_calls=1)

    report = compare_empirical_trials([t_mock], [task])
    assert report.contains_mocked_data is True
    assert report.protocol_level == "HARNESS_VALIDATED"
    assert report.protocol_level != "EMPIRICAL_OBSERVATIONS_AVAILABLE"


# ==============================================================================
# F1-07: Conservation des verdicts E3 PASS/FAIL/ABSTAIN/INDETERMINATE
# ==============================================================================
def test_f1_07_preserve_e3_verdicts_faithfully():
    """F1-07: All 4 E3 verdicts (PASS, FAIL, ABSTAIN, INDETERMINATE) are conserved without remapping."""
    tasks = [_make_task(f"task-{i}") for i in range(4)]
    trials = [
        _make_trial("tr-pass", "task-0", "STACK_ONLY", verdict="EVAL_PASS"),
        _make_trial("tr-fail", "task-1", "STACK_ONLY", verdict="EVAL_FAIL"),
        _make_trial("tr-abstain", "task-2", "STACK_ONLY", abstained=True, abstention_reason="UNKNOWN_KNOWLEDGE", verdict="ABSTAIN_CORRECT"),
        _make_trial("tr-indet", "task-3", "STACK_ONLY", verdict="INDETERMINATE"),
    ]
    report = compare_empirical_trials(trials, tasks)
    metrics = report.metrics_by_condition["STACK_ONLY"]
    assert metrics["pass_count"] == 1
    assert metrics["fail_count"] == 1
    assert metrics["abstain_count"] == 1
    assert metrics["indeterminate_count"] == 1


# ==============================================================================
# F1-08: Calcul de métriques sans promotion de UNKNOWN_COMPETENCE
# ==============================================================================
def test_f1_08_unknown_competence_maintained():
    """F1-08: Generating metrics never promotes UNKNOWN_COMPETENCE to established competence."""
    task = _make_task("task-regime")
    trial = _make_trial("tr-reg", "task-regime", "STACK_ONLY", verdict="EVAL_PASS")

    report = compare_empirical_trials([trial], [task])
    assert report.competence_regime == "UNKNOWN_COMPETENCE"
    assert report.decision_authority == "KX108_ONLY"
    assert report.advisory_only is True


# ==============================================================================
# F1-09: Refus d'une comparaison non recevable si oracles incompatibles
# ==============================================================================
def test_f1_09_refuse_incompatible_oracle_conditions():
    """F1-09: Tasks with conflicting or mismatched evaluation locators are rejected from comparison."""
    # Task configured with invalid missing locator
    invalid_task = EmpiricalTaskV1(
        task_id="task-bad-oracle",
        prompt="Incompatible query",
        task_category="FACT_KNOWN",
        oracle_reference={"oracle_id": "bad", "locator": ""},  # Empty locator
    )
    trial = _make_trial("tr-bad", "task-bad-oracle", "STACK_ONLY")

    with pytest.raises(ValueError, match="INCOMPATIBLE_ORACLE_CONDITIONS"):
        compare_empirical_trials([trial], [invalid_task])


# ==============================================================================
# F1-10: Pureté de l'analyseur (zéro I/O réseau, zéro écriture, zéro mutation)
# ==============================================================================
def test_f1_10_analyzer_purity_no_mutation(monkeypatch):
    """F1-10: compare_empirical_trials is a pure function: no network, no write, no argument mutation."""
    import socket
    def _fail_network(*args, **kwargs):
        raise RuntimeError("NETWORK_ACCESS_FORBIDDEN")
    monkeypatch.setattr(socket, "socket", _fail_network)

    task = _make_task("task-pure")
    task_copy = copy.deepcopy(task)
    trial = _make_trial("tr-pure", "task-pure", "STACK_ONLY")
    trial_copy = copy.deepcopy(trial)

    report = compare_empirical_trials([trial], [task])
    assert isinstance(report, EmpiricalComparisonReportV1)
    # Check that input arguments were not mutated in place
    assert task == task_copy
    assert trial == trial_copy
