"""
app/cognition/b11/offline_pilot_assembly.py

Offline Pilot Canonical Assembly V1 for M42/B11 Protocol (Phase F3-D6).
Pure in-memory assembly and canonical serialization boundary:
- Ingests raw observation and task fixture dictionaries without disk/network I/O
- Enforces strict input immutability
- Maps dictionaries to RawObservationRecordV1 and EmpiricalTaskV1
- Applies OMEGA9_PRE_AGGREGATION_GUARD for tasks without admissible oracle (forcing INDETERMINATE)
- Delegates normalization and evaluation to collect_and_compare_offline_pilot
- Produces deterministic, acyclic JSON serialization and content_hash

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

import copy
import dataclasses
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

from app.cognition.b11.empirical_comparison import (
    EmpiricalComparisonReportV1,
    EmpiricalTaskV1,
    EmpiricalTrialReceiptV1,
    compare_empirical_trials,
)
from app.cognition.b11.offline_collection_pilot import (
    OfflineCollectionPilotResultV1,
    RawObservationRecordV1,
    collect_and_compare_offline_pilot,
)


@dataclass(frozen=True)
class OfflinePilotAssemblyResultV1:
    assembly_id: str
    schema: Literal["OFFLINE_PILOT_ASSEMBLY_RESULT_V1"]
    content_hash: str
    pilot_result: OfflineCollectionPilotResultV1
    assembled_tasks_count: int
    assembled_trials_count: int
    export_payload: dict[str, Any]
    metadata: dict[str, Any]


def _canonical_json_dumps(obj: Any) -> str:
    """Format JSON canonique déterministe avec clés triées et séparateurs stricts."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def serialize_assembly_result_canonical_json(
    result: OfflinePilotAssemblyResultV1,
) -> str:
    """Sérialisation canonique du payload métier sans content_hash (acyclicité stricte)."""
    return _canonical_json_dumps(result.export_payload)


def _to_serializable(val: Any) -> Any:
    """Conversion récursive en types JSON purs sérialisables sans perte de structure."""
    if dataclasses.is_dataclass(val):
        return {k: _to_serializable(v) for k, v in dataclasses.asdict(val).items()}
    if isinstance(val, dict):
        return {str(k): _to_serializable(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set, frozenset)):
        return [_to_serializable(item) for item in val]
    return val


def assemble_offline_pilot_v1(
    raw_fixtures: list[dict[str, Any]],
    task_fixtures: list[dict[str, Any]],
    assembly_metadata: dict[str, Any] | None = None,
) -> OfflinePilotAssemblyResultV1:
    """Fonction pure d'assemblage et d'orchestration en mémoire."""
    # 1. Protection contre les mutations (Immutabilité stricte)
    raw_copy = copy.deepcopy(raw_fixtures)
    task_copy = copy.deepcopy(task_fixtures)

    # 2. Conversion des fixtures de tâches vers EmpiricalTaskV1
    tasks: list[EmpiricalTaskV1] = []
    for tf in task_copy:
        t = EmpiricalTaskV1(
            task_id=tf["task_id"],
            prompt=tf.get("prompt", ""),
            task_category=tf.get("task_category", "FACT_KNOWN"),
            oracle_reference=tf.get("oracle_reference"),
            metadata=tf.get("metadata", {}),
        )
        tasks.append(t)

    # 3. Conversion des fixtures brutes vers RawObservationRecordV1
    observations: list[RawObservationRecordV1] = []
    for rf in raw_copy:
        prov_kind = rf.get("provenance_kind", "SYNTHETIC_FIXTURE")
        obs = RawObservationRecordV1(
            task_id=rf["task_id"],
            trial_id=rf["trial_id"],
            condition=rf["condition"],
            raw_response_text=rf.get("raw_response_text", ""),
            provenance_kind=prov_kind,
            system_identity=rf.get("system_identity", "brody-offline-pilot"),
            components=rf.get("components", {}),
            external_telemetry=rf.get("external_telemetry", {}),
            field_provenances=rf.get("field_provenances", {}),
            timestamp_iso=rf.get("timestamp_iso", "2026-10-24T18:00:00Z"),
            abstained=rf.get("abstained", False),
            abstention_reason=rf.get("abstention_reason"),
            oracle_version=rf.get("oracle_version", "v1"),
        )
        observations.append(obs)

    # 4. Exécution du collecteur F3-D2
    initial_pilot_result = collect_and_compare_offline_pilot(observations, tasks)

    # 5. OMEGA9_PRE_AGGREGATION_GUARD : alignement strict avec E3
    # Pour toute tâche sans oracle documentaire (ex. Omega-9, oracle_reference is None),
    # l'absence de fait ne peut jamais justifier ABSTAIN_CORRECT ni EVAL_PASS.
    # Le verdict d'évaluation doit être souverainement maintenu à INDETERMINATE.
    tasks_by_id = {t.task_id: t for t in tasks}
    guarded_trials: list[EmpiricalTrialReceiptV1] = []
    verdicts_updated = False

    for trial in initial_pilot_result.normalized_trials:
        target_task = tasks_by_id.get(trial.task_id)
        if target_task and not target_task.oracle_reference:
            guarded_eval = dict(trial.evaluation_result)
            original_v = guarded_eval.get("verdict", "INDETERMINATE")
            guarded_eval["original_verdict"] = original_v
            guarded_eval["verdict"] = "INDETERMINATE"
            guarded_eval["evaluator"] = "OfflinePilotAssemblyPolicyGuardV1"
            reasons = list(guarded_eval.get("reasons", []))
            reason_msg = "GROUND_TRUTH_MISSING: unpinned task without oracle must evaluate to INDETERMINATE"
            if reason_msg not in reasons:
                reasons.append(reason_msg)
            guarded_eval["reasons"] = reasons
            trial = dataclasses.replace(trial, evaluation_result=guarded_eval)
            if original_v != "INDETERMINATE":
                verdicts_updated = True
        guarded_trials.append(trial)

    # Si des verdicts ont été alignés sur E3, recalculer la comparaison
    comparison_report: EmpiricalComparisonReportV1 | None = initial_pilot_result.comparison_report
    if verdicts_updated and "ORACLE_VERSION_MISMATCH" not in initial_pilot_result.hold_reasons:
        try:
            comparison_report = compare_empirical_trials(guarded_trials, tasks)
        except Exception:
            comparison_report = None

    # Reconstitution du résultat pilot avec les trials gardés
    pilot_result = dataclasses.replace(
        initial_pilot_result,
        normalized_trials=guarded_trials,
        comparison_report=comparison_report,
    )

    # 6. Construction de export_payload (sans content_hash)
    # F-F3-D8-01 (Option B): Exclure report_id (UUID volatil d'instanciation runtime F2)
    # de la projection canonique export_payload pour garantir un content_hash purement sémantique.
    comp_report_payload: dict[str, Any] | None = None
    if comparison_report:
        comp_report_payload = _to_serializable(comparison_report)
        comp_report_payload.pop("report_id", None)

    assembly_id = f"assembly-m42-{hashlib.sha256(str(len(tasks)).encode()).hexdigest()[:8]}"
    export_payload: dict[str, Any] = {
        "assembly_id": assembly_id,
        "schema": "OFFLINE_PILOT_ASSEMBLY_RESULT_V1",
        "competence_regime": pilot_result.competence_regime,
        "decision_authority": pilot_result.decision_authority,
        "advisory_only": pilot_result.advisory_only,
        "verdict": pilot_result.verdict,
        "assembled_tasks_count": len(tasks),
        "assembled_trials_count": len(observations),
        "unique_tasks_count": pilot_result.unique_tasks_count,
        "independent_facts_count": pilot_result.independent_facts_count,
        "hold_reasons": list(pilot_result.hold_reasons),
        "unpaired_tasks": list(pilot_result.unpaired_tasks),
        "tasks": [_to_serializable(t) for t in tasks],
        "normalized_trials": [_to_serializable(tr) for tr in guarded_trials],
        "comparison_report": comp_report_payload,
        "metadata": _to_serializable(pilot_result.metadata),
    }

    # 7. Calcul du content_hash sur le JSON canonique du payload
    canonical_json_str = _canonical_json_dumps(export_payload)
    content_hash = hashlib.sha256(canonical_json_str.encode("utf-8")).hexdigest()

    meta = {
        "pilot_scope": "M42_B11_OFFLINE_PILOT_ASSEMBLY_V1",
        "assembly_metadata": assembly_metadata or {},
    }

    return OfflinePilotAssemblyResultV1(
        assembly_id=assembly_id,
        schema="OFFLINE_PILOT_ASSEMBLY_RESULT_V1",
        content_hash=content_hash,
        pilot_result=pilot_result,
        assembled_tasks_count=len(tasks),
        assembled_trials_count=len(observations),
        export_payload=export_payload,
        metadata=meta,
    )
