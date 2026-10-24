"""
app/cognition/b11/empirical_comparison.py

Pure Empirical Comparison Engine V1 for M42/B11 Protocol.
Evaluates and compares trials across STACK_ONLY, STACK_PLUS_QWEN, and QWEN_ONLY.

Invariants:
- KX108_ONLY
- UNKNOWN_COMPETENCE
- advisory_only = True
- memory_write = False
- emits_act = False
- kernel_mutation = False
- b12_selection = False

Pure analysis function: zero network, zero persistence, zero input mutation.
"""
from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

EmpiricalConditionV1 = Literal["STACK_ONLY", "STACK_PLUS_QWEN", "QWEN_ONLY"]


@dataclass(frozen=True)
class EmpiricalTaskV1:
    task_id: str
    prompt: str
    task_category: str
    oracle_reference: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EmpiricalTrialReceiptV1:
    trial_id: str
    task_id: str
    condition: EmpiricalConditionV1
    system_version: str
    observable_response_text: str
    abstained: bool
    abstention_reason: str | None
    external_telemetry: dict[str, Any]
    evaluation_result: dict[str, Any] | None
    is_mock: bool
    timestamp_iso: str


@dataclass(frozen=True)
class EmpiricalComparisonReportV1:
    report_id: str
    schema: Literal["EMPIRICAL_COMPARISON_REPORT_V1"]
    protocol_level: Literal[
        "HARNESS_VALIDATED",
        "EMPIRICAL_OBSERVATIONS_AVAILABLE",
        "STATISTICAL_CALIBRATION_SUPPORTED",
    ]
    competence_regime: Literal["UNKNOWN_COMPETENCE"]
    decision_authority: Literal["KX108_ONLY"]
    advisory_only: bool
    total_tasks: int
    total_trials: int
    contains_mocked_data: bool
    metrics_by_condition: dict[str, dict[str, Any]]
    pairwise_comparisons: dict[str, dict[str, Any]]
    causal_attribution: dict[str, Any]
    limitations: list[str]
    hold_reasons: list[str]


def _wilson_score_interval(p: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """Calculate 95% Wilson score interval for binomial proportion p with sample size n."""
    if n <= 0:
        return (0.0, 0.0)
    denominator = 1.0 + (z * z) / n
    center = (p + (z * z) / (2.0 * n)) / denominator
    margin = (z * math.sqrt((p * (1.0 - p) + (z * z) / (4.0 * n)) / n)) / denominator
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return (round(lower, 4), round(upper, 4))


def compare_empirical_trials(
    trials: list[EmpiricalTrialReceiptV1],
    tasks: list[EmpiricalTaskV1],
) -> EmpiricalComparisonReportV1:
    """Pure analysis function comparing empirical trials across conditions.

    Does not modify input arguments. Raises ValueError on circular or incompatible oracles.
    """
    # 1. Validate Tasks & Oracles
    tasks_by_id: dict[str, EmpiricalTaskV1] = {}
    for task in tasks:
        oracle_ref = task.oracle_reference or {}
        # F1-02: Check circular oracle
        if (
            oracle_ref.get("ground_truth_provenance") == "CANDIDATE_OUTPUT"
            or oracle_ref.get("is_circular") is True
        ):
            raise ValueError(
                f"INVALID_CIRCULAR_ORACLE: Task {task.task_id} has circular oracle derived from candidate output"
            )

        # F1-09: Check incompatible or missing locator
        locator = oracle_ref.get("locator")
        if locator is None or str(locator).strip() == "":
            raise ValueError(
                f"INCOMPATIBLE_ORACLE_CONDITIONS: Task {task.task_id} has empty or missing oracle locator"
            )

        tasks_by_id[task.task_id] = task

    total_tasks = len(tasks_by_id)
    total_trials = len(trials)

    # 2. Check Mock data presence (F1-06)
    contains_mocked_data = any(
        trial.is_mock
        or (trial.external_telemetry and trial.external_telemetry.get("provenance") == "MOCKED_EXTERNAL")
        for trial in trials
    )
    protocol_level: Literal[
        "HARNESS_VALIDATED",
        "EMPIRICAL_OBSERVATIONS_AVAILABLE",
        "STATISTICAL_CALIBRATION_SUPPORTED",
    ] = "HARNESS_VALIDATED" if contains_mocked_data else "EMPIRICAL_OBSERVATIONS_AVAILABLE"

    # 3. Metrics by condition (F1-01, F1-04, F1-07)
    conditions_present = {t.condition for t in trials}
    standard_conditions: list[EmpiricalConditionV1] = ["STACK_ONLY", "STACK_PLUS_QWEN", "QWEN_ONLY"]
    # Only include standard conditions that appear in trials, or all three if at least one is present
    target_conditions = [c for c in standard_conditions if c in conditions_present]

    metrics_by_condition: dict[str, dict[str, Any]] = {}
    trials_by_cond: dict[str, list[EmpiricalTrialReceiptV1]] = {c: [] for c in standard_conditions}
    for trial in trials:
        if trial.condition in trials_by_cond:
            trials_by_cond[trial.condition].append(trial)

    for c in target_conditions:
        cond_trials = trials_by_cond[c]
        unique_tasks_in_cond = set(t.task_id for t in cond_trials)
        sample_size_tasks = len(unique_tasks_in_cond)
        total_runs = len(cond_trials)

        pass_count = 0
        fail_count = 0
        abstain_count = 0
        indeterminate_count = 0

        for t in cond_trials:
            eval_res = t.evaluation_result or {}
            verdict = eval_res.get("verdict")
            if verdict == "EVAL_PASS":
                pass_count += 1
            elif verdict == "EVAL_FAIL":
                fail_count += 1
            elif verdict == "ABSTAIN_CORRECT" or t.abstained:
                abstain_count += 1
            elif verdict == "INDETERMINATE":
                indeterminate_count += 1

        pass_rate = (pass_count / total_runs) if total_runs > 0 else 0.0
        wilson_interval = _wilson_score_interval(pass_rate, sample_size_tasks)

        metrics_by_condition[c] = {
            "condition": c,
            "sample_size_tasks": sample_size_tasks,
            "total_runs": total_runs,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "abstain_count": abstain_count,
            "indeterminate_count": indeterminate_count,
            "pass_rate": round(pass_rate, 4),
            "wilson_95_ci": wilson_interval,
        }

    # 4. Pairwise comparisons (F1-03)
    pairwise_comparisons: dict[str, dict[str, Any]] = {}
    hold_reasons: list[str] = []

    pairs_to_evaluate = [
        ("STACK_ONLY_vs_STACK_PLUS_QWEN", "STACK_ONLY", "STACK_PLUS_QWEN"),
        ("STACK_PLUS_QWEN_vs_QWEN_ONLY", "STACK_PLUS_QWEN", "QWEN_ONLY"),
        ("STACK_ONLY_vs_QWEN_ONLY", "STACK_ONLY", "QWEN_ONLY"),
    ]

    for pair_name, c1, c2 in pairs_to_evaluate:
        c1_trials = trials_by_cond.get(c1, [])
        c2_trials = trials_by_cond.get(c2, [])
        if not c1_trials or not c2_trials:
            continue

        c1_tasks = {t.task_id: t for t in c1_trials}
        c2_tasks = {t.task_id: t for t in c2_trials}
        common_task_ids = set(c1_tasks.keys()) & set(c2_tasks.keys())
        paired_count = len(common_task_ids)

        if paired_count == 0:
            pairwise_comparisons[pair_name] = {
                "paired_tasks_count": 0,
                "status": "UNPAIRED_TASKS",
                "reason": f"No overlapping task_id between {c1} and {c2}",
            }
            if "UNPAIRED_TASK" not in hold_reasons:
                hold_reasons.append("UNPAIRED_TASK")
        else:
            pairwise_comparisons[pair_name] = {
                "paired_tasks_count": paired_count,
                "status": "PAIRED",
                "c1_pass": sum(
                    1
                    for tid in common_task_ids
                    if (c1_tasks[tid].evaluation_result or {}).get("verdict") == "EVAL_PASS"
                ),
                "c2_pass": sum(
                    1
                    for tid in common_task_ids
                    if (c2_tasks[tid].evaluation_result or {}).get("verdict") == "EVAL_PASS"
                ),
            }

    # 5. Causal attribution for Qwen in condition B (F1-05)
    causal_attribution: dict[str, Any] = {}
    b_trials = trials_by_cond.get("STACK_PLUS_QWEN", [])
    if b_trials:
        ext_called = any(
            (t.external_telemetry or {}).get("external_called")
            or (t.external_telemetry or {}).get("model_calls", 0) > 0
            for t in b_trials
        )
        ext_received = any((t.external_telemetry or {}).get("external_received") for t in b_trials)
        ext_admitted = any((t.external_telemetry or {}).get("external_admitted") for t in b_trials)

        a_trials = trials_by_cond.get("STACK_ONLY", [])
        a_by_task = {t.task_id: t for t in a_trials}
        b_by_task = {t.task_id: t for t in b_trials}
        common_ab = set(a_by_task.keys()) & set(b_by_task.keys())

        answer_changed = False
        perf_diff_observed = False
        if common_ab:
            for tid in common_ab:
                at = a_by_task[tid]
                bt = b_by_task[tid]
                if at.observable_response_text != bt.observable_response_text:
                    answer_changed = True
                at_verdict = (at.evaluation_result or {}).get("verdict")
                bt_verdict = (bt.evaluation_result or {}).get("verdict")
                if at_verdict != bt_verdict:
                    perf_diff_observed = True

        # Strictest attribution requirement: must satisfy full chain and not be mock
        causal_effect_supported = bool(
            ext_called
            and ext_received
            and ext_admitted
            and answer_changed
            and perf_diff_observed
            and not contains_mocked_data
        )

        causal_attribution["STACK_PLUS_QWEN"] = {
            "external_called": ext_called,
            "external_data_received": ext_received,
            "external_data_admitted": ext_admitted,
            "answer_changed": answer_changed,
            "performance_difference_observed": perf_diff_observed,
            "causal_effect_supported": causal_effect_supported,
        }

    limitations = [
        "E3_SCALAR_FACT_EVALUATION_ONLY",
        "NO_DISCURSIVE_QUALITY_ASSESSMENT",
        "PILOT_SAMPLE_SIZE_NOT_GENERAL_COMPETENCE",
    ]

    return EmpiricalComparisonReportV1(
        report_id=f"rep-emp-{uuid.uuid4().hex[:12]}",
        schema="EMPIRICAL_COMPARISON_REPORT_V1",
        protocol_level=protocol_level,
        competence_regime="UNKNOWN_COMPETENCE",
        decision_authority="KX108_ONLY",
        advisory_only=True,
        total_tasks=total_tasks,
        total_trials=total_trials,
        contains_mocked_data=contains_mocked_data,
        metrics_by_condition=metrics_by_condition,
        pairwise_comparisons=pairwise_comparisons,
        causal_attribution=causal_attribution,
        limitations=limitations,
        hold_reasons=hold_reasons,
    )
