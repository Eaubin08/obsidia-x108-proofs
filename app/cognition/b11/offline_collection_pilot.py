"""
app/cognition/b11/offline_collection_pilot.py

Offline Collection Pilot V1 for M42/B11 Protocol (Phase F3-D2).
Pure ingestion and normalization boundary:
- Normalizes raw observations into EmpiricalTrialReceiptV1
- Preserves genuine provenance (RECORDED_OBSERVATION, SYNTHETIC_FIXTURE, MOCKED_EXTERNAL)
- Tracks field origin (OBSERVED, DERIVED, DECLARED, UNAVAILABLE)
- Validates task pairing and oracle versions (ORACLE_VERSION_MISMATCH -> HOLD)
- Decouples unique_tasks_count from independent_facts_count
- Transmits to compare_empirical_trials and produces consultative pilot report

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

import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

from app.cognition.b11.brody_independent_evaluator import _extract_numeric_fact
from app.cognition.b11.empirical_comparison import (
    EmpiricalComparisonReportV1,
    EmpiricalTaskV1,
    EmpiricalTrialReceiptV1,
    compare_empirical_trials,
)

ObservationProvenanceKind = Literal[
    "RECORDED_OBSERVATION", "SYNTHETIC_FIXTURE", "MOCKED_EXTERNAL"
]
FieldProvenanceKind = Literal["OBSERVED", "DERIVED", "DECLARED", "UNAVAILABLE"]

KNOWN_B8_PINS = frozenset(
    {"16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b"}
)


@dataclass(frozen=True)
class RawObservationRecordV1:
    task_id: str
    trial_id: str
    condition: Literal["STACK_ONLY", "STACK_PLUS_QWEN", "QWEN_ONLY"]
    raw_response_text: str
    provenance_kind: ObservationProvenanceKind
    system_identity: str
    components: dict[str, str]  # component_name -> sha256
    external_telemetry: dict[str, Any]
    field_provenances: dict[str, FieldProvenanceKind]
    timestamp_iso: str
    abstained: bool = False
    abstention_reason: str | None = None
    oracle_version: str = "v1"


@dataclass(frozen=True)
class OfflineCollectionPilotResultV1:
    pilot_id: str
    schema: Literal["OFFLINE_COLLECTION_PILOT_RESULT_V1"]
    verdict: Literal["HARNESS_VALIDATED", "PILOT_WITH_GAPS", "HOLD"]
    competence_regime: Literal["UNKNOWN_COMPETENCE"]
    decision_authority: Literal["KX108_ONLY"]
    advisory_only: bool
    total_tasks_received: int
    unique_tasks_count: int
    independent_facts_count: int
    normalized_trials: list[EmpiricalTrialReceiptV1]
    comparison_report: EmpiricalComparisonReportV1 | None
    unpaired_tasks: list[str]
    hold_reasons: list[str]
    metadata: dict[str, Any]


def collect_and_compare_offline_pilot(
    observations: list[RawObservationRecordV1],
    tasks: list[EmpiricalTaskV1],
) -> OfflineCollectionPilotResultV1:
    """Pure collection, normalization, and evaluation function for offline pilot."""
    pilot_id = f"pilot-f3-{uuid.uuid4().hex[:12]}"
    hold_reasons: list[str] = []
    unpaired_tasks: list[str] = []

    # 1. Index Tasks & Oracles
    tasks_by_id: dict[str, EmpiricalTaskV1] = {t.task_id: t for t in tasks}
    unique_tasks_count = len(tasks_by_id)

    # 2. Compute Independent Facts (Anti-inflation rule D1-05)
    facts_seen: set[tuple[Any, ...]] = set()
    task_audit: dict[str, dict[str, Any]] = {}

    for t in tasks:
        oracle = t.oracle_reference or {}
        locator = oracle.get("locator")
        prov = oracle.get("ground_truth_provenance")
        assertion = oracle.get("expected_assertion") or {}

        # Distinct fact key: locator and assertion content
        fact_key = (
            locator,
            assertion.get("symbol"),
            assertion.get("property"),
            assertion.get("numeric_value"),
            assertion.get("unit"),
        )
        facts_seen.add(fact_key)

        # Audit oracle independence (D1-06)
        is_attested = bool(prov == "B8_PINNED_DOCUMENT" and locator in KNOWN_B8_PINS)
        task_audit[t.task_id] = {
            "oracle_independence_attested": is_attested,
            "oracle_id": oracle.get("oracle_id"),
            "locator": locator,
            "ground_truth_provenance": prov,
        }

    independent_facts_count = len(facts_seen) if facts_seen else unique_tasks_count

    # 3. Check Oracle Version Consistency & Grouping (D1-07)
    obs_by_task: dict[str, list[RawObservationRecordV1]] = {}
    for o in observations:
        obs_by_task.setdefault(o.task_id, []).append(o)

    for tid, obs_list in obs_by_task.items():
        versions = {o.oracle_version for o in obs_list}
        if len(versions) > 1:
            hold_reasons.append("ORACLE_VERSION_MISMATCH")

    # 4. Normalize Observations to EmpiricalTrialReceiptV1
    normalized_trials: list[EmpiricalTrialReceiptV1] = []
    field_provenance_audit: dict[str, str] = {}

    for obs in observations:
        # Merge field provenances
        for k, v in obs.field_provenances.items():
            field_provenance_audit[k] = v

        task = tasks_by_id.get(obs.task_id)
        verdict = "INDETERMINATE"
        if obs.abstained:
            verdict = "ABSTAIN_CORRECT"
        elif task:
            oracle = task.oracle_reference or {}
            expected_assertion = oracle.get("expected_assertion") or {}
            exp_val = expected_assertion.get("numeric_value")
            exp_unit = expected_assertion.get("unit")

            obs_val, obs_unit = _extract_numeric_fact(obs.raw_response_text)
            if obs_val is not None and exp_val is not None:
                if obs_val == exp_val and (
                    exp_unit is None or obs_unit == exp_unit or obs_unit is None
                ):
                    verdict = "EVAL_PASS"
                else:
                    verdict = "EVAL_FAIL"

        is_mock = obs.provenance_kind in ("SYNTHETIC_FIXTURE", "MOCKED_EXTERNAL")
        ext_telem = dict(obs.external_telemetry)
        ext_telem["provenance"] = obs.provenance_kind

        trial = EmpiricalTrialReceiptV1(
            trial_id=obs.trial_id,
            task_id=obs.task_id,
            condition=obs.condition,
            system_version=obs.system_identity,
            observable_response_text=obs.raw_response_text,
            abstained=obs.abstained,
            abstention_reason=obs.abstention_reason,
            external_telemetry=ext_telem,
            evaluation_result={
                "verdict": verdict,
                "evaluator": "BrodyIndependentEvaluatorV1",
                "reasons": [],
            },
            is_mock=is_mock,
            timestamp_iso=obs.timestamp_iso,
        )
        normalized_trials.append(trial)

    # 5. Execute F2 Empirical Comparison Engine if no blocking HOLD
    comparison_report: EmpiricalComparisonReportV1 | None = None
    if "ORACLE_VERSION_MISMATCH" not in hold_reasons:
        try:
            comparison_report = compare_empirical_trials(normalized_trials, tasks)
            if comparison_report.hold_reasons:
                for hr in comparison_report.hold_reasons:
                    if hr not in hold_reasons:
                        hold_reasons.append(hr)
        except Exception as exc:
            hold_reasons.append(str(exc))

    # 6. Determine Verdict
    if "ORACLE_VERSION_MISMATCH" in hold_reasons:
        verdict_pilot: Literal["HARNESS_VALIDATED", "PILOT_WITH_GAPS", "HOLD"] = "HOLD"
    elif hold_reasons and "UNPAIRED_TASK" in hold_reasons:
        verdict_pilot = "HOLD"
    elif any(t.is_mock for t in normalized_trials):
        verdict_pilot = "HARNESS_VALIDATED"
    elif comparison_report and comparison_report.protocol_level == "EMPIRICAL_OBSERVATIONS_AVAILABLE":
        verdict_pilot = "PILOT_WITH_GAPS"
    else:
        verdict_pilot = "HARNESS_VALIDATED"

    metadata: dict[str, Any] = {
        "task_audit": task_audit,
        "field_provenance_audit": field_provenance_audit,
        "pilot_scope": "M42_B11_OFFLINE_COLLECTION_PILOT_V1",
    }

    return OfflineCollectionPilotResultV1(
        pilot_id=pilot_id,
        schema="OFFLINE_COLLECTION_PILOT_RESULT_V1",
        verdict=verdict_pilot,
        competence_regime="UNKNOWN_COMPETENCE",
        decision_authority="KX108_ONLY",
        advisory_only=True,
        total_tasks_received=len(observations),
        unique_tasks_count=unique_tasks_count,
        independent_facts_count=independent_facts_count,
        normalized_trials=normalized_trials,
        comparison_report=comparison_report,
        unpaired_tasks=unpaired_tasks,
        hold_reasons=hold_reasons,
        metadata=metadata,
    )
