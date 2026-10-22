"""M42 B11 Compétence & Calibration — Caractérisation Empirique Descriptive V1.

Module de caractérisation descriptive des observations vérifiées Rail A (`tooling_build`).
Conforme à docs/architecture/M42_B11_EMPIRICAL_CHARACTERIZATION_SPEC_V1.md.

Garanties doctrinales V1 :
- Description pure sans inférence : les taux observés ne sont pas extrapolés en fiabilité latente.
- Régime épistémique UNKNOWN_COMPETENCE strict pour tout profil émis (confidence=0.0, reliability=None, calibration=None).
- B11_EFFECTS scrupuleusement respecté : lecture seule, zéro écriture mémoire/kernel, autorité KX108_ONLY.
- Aucune attribution causale trans-mécanisme (séparation absolue entre Rail A et Brody/modèles neuronaux).
- Déduplication technique distincte de l'indépendance statistique (indépendance non établie).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from app.cognition.b11.contracts import (
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)
from app.cognition.b11.rail_a_observation_adapter import (
    OUTCOME_FAILURE,
    OUTCOME_PASS,
    RailAVerifiedObservation,
    load_and_verify_rail_a_observations_batch,
)


def _append_unique(target: list[str], code: str) -> None:
    if code not in target:
        target.append(code)


@dataclass(frozen=True)
class EmpiricalContextualCharacterization:
    """Structure intermédiaire immuable et consultative de caractérisation empirique."""

    characterization_id: str
    target_mechanism_ref: str
    domain: str
    task_ref: str
    conditions: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    data_provenance_type: str
    raw_observation_count: int
    distinct_execution_count: int
    retained_in_context_count: int
    pass_count: int
    fail_count: int
    error_count: int
    excluded_count: int
    observed_success_rate: float | None
    context_group_keys: tuple[str, ...]
    context_group_count: int
    statistical_independence_status: str
    predictive_data_status: str
    descriptive_admissibility_status: str
    diagnostic_codes: tuple[str, ...]
    unknowns: tuple[str, ...]


def characterize_empirical_observations(
    characterization_id: str,
    domain: str,
    task_ref: str,
    target_resources: Sequence[str],
    conditions: Sequence[str] = (),
    *,
    kxpost_decision_record_ids: Sequence[Any] = (),
    kx108_decision_dir: Path,
    pre_execution_context_dir: Path,
    sealed_receipt_dir: Path,
    sealed_rollback_evidence_dir: Path,
    test_contract_results_dir: Path,
) -> tuple[EmpiricalContextualCharacterization, ContextualCompetenceProfile]:
    """Caractérise descriptivement les observations réelles vérifiées du Rail A.

    Ne produit aucune qualification positive ou négative de compétence.
    Retourne la caractérisation intermédiaire descriptive et le profil B11 sous UNKNOWN_COMPETENCE.
    """
    diagnostic_codes: list[str] = []
    unknowns: list[str] = []
    evidence_refs: list[str] = []
    retained_observations: list[RailAVerifiedObservation] = []
    context_group_keys: list[str] = []

    # 1. Validation passive et fail-closed des entrées scalaires et conteneurs
    safe_char_id = (
        characterization_id.strip()
        if type(characterization_id) is str and characterization_id.strip()
        else "char-fallback"
    )
    if type(characterization_id) is not str or not characterization_id.strip():
        _append_unique(diagnostic_codes, "INVALID_CHARACTERIZATION_ID_REJECTED")

    safe_domain = domain.strip() if type(domain) is str and domain.strip() else "domain-fallback"
    if type(domain) is not str or not domain.strip():
        _append_unique(diagnostic_codes, "INVALID_DOMAIN_REJECTED")

    safe_task = task_ref.strip() if type(task_ref) is str and task_ref.strip() else "task-fallback"
    if type(task_ref) is not str or not task_ref.strip():
        _append_unique(diagnostic_codes, "INVALID_TASK_REF_REJECTED")

    safe_resources: list[str] = []
    if type(target_resources) in (tuple, list):
        for r in target_resources:
            if type(r) is str and r.strip():
                safe_resources.append(r.strip())
            else:
                _append_unique(diagnostic_codes, "INVALID_RESOURCE_STRUCTURE_REJECTED")
    else:
        _append_unique(diagnostic_codes, "INVALID_RESOURCE_CONTAINER_REJECTED")

    eff_resources = tuple(safe_resources) if safe_resources else ("invalid:target_resource",)

    safe_conditions: list[str] = []
    if type(conditions) in (tuple, list):
        for c in conditions:
            if type(c) is str and c.strip():
                safe_conditions.append(c.strip())
            else:
                _append_unique(diagnostic_codes, "INVALID_CONDITION_STRUCTURE_REJECTED")
    else:
        _append_unique(diagnostic_codes, "INVALID_CONDITION_CONTAINER_REJECTED")

    eff_conditions = tuple(safe_conditions)

    # 2. Filtrage passif des identifiants d'observations soumis
    raw_count = len(kxpost_decision_record_ids) if type(kxpost_decision_record_ids) in (tuple, list) else 0
    valid_record_ids: list[str] = []
    if type(kxpost_decision_record_ids) in (tuple, list):
        for item in kxpost_decision_record_ids:
            if type(item) is str and item.strip():
                valid_record_ids.append(item.strip())
            elif isinstance(item, dict):
                _append_unique(diagnostic_codes, "SELF_ATTESTATION_REJECTED")
            else:
                _append_unique(diagnostic_codes, "INVALID_RECORD_STRUCTURE_REJECTED")
    else:
        _append_unique(diagnostic_codes, "INVALID_RECORD_CONTAINER_REJECTED")

    # 3. Acquisition et vérification canonique via l'adaptateur Rail A
    batch_obs: tuple[RailAVerifiedObservation, ...] = ()
    if valid_record_ids:
        b_obs, b_unknowns, b_risks = load_and_verify_rail_a_observations_batch(
            valid_record_ids,
            kx108_decision_dir=kx108_decision_dir,
            pre_execution_context_dir=pre_execution_context_dir,
            sealed_receipt_dir=sealed_receipt_dir,
            sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
            test_contract_results_dir=test_contract_results_dir,
        )
        batch_obs = b_obs
        for u in b_unknowns:
            _append_unique(unknowns, u)
        for r in b_risks:
            _append_unique(diagnostic_codes, r)

    distinct_count = len(batch_obs)
    excluded_count = max(0, raw_count - distinct_count)
    pass_count = 0
    fail_count = 0
    error_count = 0

    # 4. Projection contextuelle et catégorisation descriptive
    for obs in batch_obs:
        matches = True

        # Attribution causale stricte du mécanisme
        if obs.executing_mechanism_ref not in safe_resources:
            _append_unique(diagnostic_codes, "CAUSAL_ATTRIBUTION_MISMATCH")
            _append_unique(diagnostic_codes, "CONTEXT_MISMATCH:TARGET_RESOURCE")
            matches = False

        if obs.mutated_target_path in safe_resources:
            _append_unique(diagnostic_codes, "MUTATED_PATH_NOT_AN_EXECUTING_MECHANISM")
            matches = False

        # Domaine
        if obs.domain != safe_domain:
            _append_unique(diagnostic_codes, "CONTEXT_MISMATCH:DOMAIN")
            matches = False

        # Tâche
        if obs.task_ref != safe_task:
            _append_unique(diagnostic_codes, "CONTEXT_MISMATCH:TASK")
            matches = False

        # Conditions
        for cond in eff_conditions:
            if cond.startswith("mutated_target_path:"):
                exp_path = cond[len("mutated_target_path:"):].strip()
                if obs.mutated_target_path != exp_path:
                    _append_unique(diagnostic_codes, "CONTEXT_MISMATCH:MUTATED_TARGET_PATH")
                    _append_unique(diagnostic_codes, "CONTEXT_MISMATCH:CONDITIONS")
                    matches = False
            elif cond.startswith("test_contract_hash:"):
                exp_hash = cond[len("test_contract_hash:"):].strip()
                if obs.test_contract_hash != exp_hash:
                    _append_unique(diagnostic_codes, "CONTEXT_MISMATCH:TEST_CONTRACT_HASH")
                    _append_unique(diagnostic_codes, "CONTEXT_MISMATCH:CONDITIONS")
                    matches = False
            else:
                if cond not in obs.conditions:
                    _append_unique(diagnostic_codes, "CONTEXT_MISMATCH:CONDITIONS")
                    matches = False

        if not matches:
            excluded_count += 1
            continue

        retained_observations.append(obs)

        # Référencement de la preuve post-décision
        kxpost_ref = next(
            (ref for ref in obs.anchor_refs if ref.startswith("kxpost:")),
            f"kxpost:{obs.observation_id}",
        )
        if kxpost_ref not in evidence_refs:
            evidence_refs.append(kxpost_ref)

        # Résultat contractuel
        if (
            obs.verified_execution_outcome == OUTCOME_PASS
            or obs.test_aggregate_status == "AGGREGATE_ALL_REQUIRED_PASS"
        ):
            pass_count += 1
        elif (
            obs.verified_execution_outcome == OUTCOME_FAILURE
            or obs.test_aggregate_status == "AGGREGATE_REQUIRED_TEST_FAILED"
        ):
            fail_count += 1
        else:
            error_count += 1

        # Clé de dépendance contextuelle
        grp_key = (
            f"{obs.executing_mechanism_ref}|{obs.task_ref}|"
            f"{obs.mutated_target_path}|{obs.test_contract_hash}"
        )
        if grp_key not in context_group_keys:
            context_group_keys.append(grp_key)

    retained_count = len(retained_observations)
    context_group_count = len(context_group_keys)

    # 5. Calcul des métriques descriptives et régimes
    if retained_count == 0:
        observed_success_rate = None
        descriptive_admissibility_status = "NO_DATA"
        _append_unique(unknowns, "NO_HISTORICAL_EVIDENCE")
        statistical_independence_status = "NOT_ESTABLISHED"
    else:
        observed_success_rate = float(pass_count / retained_count)
        descriptive_admissibility_status = "ADMISSIBLE_DESCRIPTIVE_ONLY"

        if pass_count > 0 and fail_count > 0:
            _append_unique(diagnostic_codes, "EMPIRICAL_VARIABILITY_OBSERVED")

        if context_group_count == 1:
            statistical_independence_status = "MONO_CONTEXT_INDEPENDENCE_UNESTABLISHED"
        else:
            statistical_independence_status = "INDEPENDENCE_NOT_ASSUMED"

    _append_unique(unknowns, "PREDICTIVE_CALIBRATION_UNAVAILABLE")

    target_mech = eff_resources[0] if eff_resources else "unknown:mechanism"
    if retained_count > 0:
        provenance_type = "PROVENANCE_UNESTABLISHED"
        _append_unique(diagnostic_codes, "LOCAL_INTEGRITY_VERIFIED")
    else:
        provenance_type = "UNAUTHENTICATED"

    char = EmpiricalContextualCharacterization(
        characterization_id=safe_char_id,
        target_mechanism_ref=target_mech,
        domain=safe_domain,
        task_ref=safe_task,
        conditions=eff_conditions,
        evidence_refs=tuple(evidence_refs),
        data_provenance_type=provenance_type,
        raw_observation_count=raw_count,
        distinct_execution_count=distinct_count,
        retained_in_context_count=retained_count,
        pass_count=pass_count,
        fail_count=fail_count,
        error_count=error_count,
        excluded_count=excluded_count,
        observed_success_rate=observed_success_rate,
        context_group_keys=tuple(context_group_keys),
        context_group_count=context_group_count,
        statistical_independence_status=statistical_independence_status,
        predictive_data_status="PREDICTIVE_DATA_ABSENT",
        descriptive_admissibility_status=descriptive_admissibility_status,
        diagnostic_codes=tuple(diagnostic_codes),
        unknowns=tuple(unknowns),
    )

    # 6. Profil B11 projeté (UNKNOWN_COMPETENCE obligatoire)
    profile_unknowns = list(unknowns)
    if not evidence_refs:
        _append_unique(profile_unknowns, "NO_HISTORICAL_EVIDENCE")
    _append_unique(profile_unknowns, "M42_STATISTICAL_THRESHOLDS_PENDING")
    _append_unique(profile_unknowns, "PREDICTIVE_CALIBRATION_UNAVAILABLE")

    profile = ContextualCompetenceProfile(
        evaluation_id=safe_char_id,
        domain=safe_domain,
        task_ref=safe_task,
        target_resources=eff_resources,
        conditions=eff_conditions,
        competence_regime=CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=tuple(evidence_refs),
        unknowns=tuple(profile_unknowns),
        contradictions=(),
        risk_indicators=tuple(diagnostic_codes),
        advisory_notes="Empirical descriptive characterization V1 (strictly descriptive, unpromoted).",
    )

    return char, profile


__all__ = [
    "B11_EFFECTS",
    "EmpiricalContextualCharacterization",
    "characterize_empirical_observations",
]
