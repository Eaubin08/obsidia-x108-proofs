"""M42 B11 Compétence & Calibration — Pont Contextuel d'Observations Rail A V1.

Raccordement passif, fail-closed et en lecture seule stricte entre les
observations d'exécution réelles et vérifiées du Rail A (`tooling_build`)
et le profil canonique `ContextualCompetenceProfile`.

Régime épistémique V1:
Tant que les seuils statistiques N_min et les formules de calibration empirique
de M42 ne sont pas validés et arrêtés, tout profil émis demeure impérativement
sous `CompetenceRegime.UNKNOWN_COMPETENCE` avec `confidence_score = 0.0`,
`reliability_score = None` et `calibration_metric = None`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from app.cognition.b11.contracts import (
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)
from app.cognition.b11.rail_a_observation_adapter import (
    RailAVerifiedObservation,
    load_and_verify_rail_a_observations_batch,
)


def _append_unique(target: list[str], code: str) -> None:
    if code not in target:
        target.append(code)


def evaluate_rail_a_contextual_competence(
    evaluation_id: str,
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
) -> ContextualCompetenceProfile:
    """Évalue la compétence contextuelle à partir des observations réelles vérifiées du Rail A.

    Garanties doctrinales V1 :
    - Zéro I/O d'écriture (B11_EFFECTS respecté).
    - Régime fixé à UNKNOWN_COMPETENCE (confidence=0.0, reliability=None, calibration=None).
    - Traçabilité stricte dans evidence_refs uniquement pour les observations vérifiées
      correspondant exactement au contexte d'évaluation demandé.
    - Aucune promotion prématurée en compétence ou incompétence.
    """
    unknowns: list[str] = []
    risk_indicators: list[str] = []
    evidence_refs: list[str] = []

    # 1. Validation passive et fail-closed des identifiants et contextes scalaires
    safe_evaluation_id = "invalid-evaluation-id"
    if type(evaluation_id) is str and evaluation_id.strip():
        safe_evaluation_id = evaluation_id.strip()
    else:
        _append_unique(risk_indicators, "INVALID_EVALUATION_ID_REJECTED")

    safe_domain = "invalid-domain"
    if type(domain) is str and domain.strip():
        safe_domain = domain.strip()
    else:
        _append_unique(risk_indicators, "INVALID_DOMAIN_REJECTED")

    safe_task_ref = "invalid-task-ref"
    if type(task_ref) is str and task_ref.strip():
        safe_task_ref = task_ref.strip()
    else:
        _append_unique(risk_indicators, "INVALID_TASK_REF_REJECTED")

    # 2. Validation passive des ressources cibles
    safe_resources: list[str] = []
    if type(target_resources) not in (tuple, list):
        _append_unique(risk_indicators, "INVALID_RESOURCE_CONTAINER_REJECTED")
    else:
        for r in target_resources:
            if type(r) is str:
                s_r = r.strip()
                if s_r:
                    safe_resources.append(s_r)
                else:
                    _append_unique(risk_indicators, "INVALID_RESOURCE_STRUCTURE_REJECTED")
            else:
                _append_unique(risk_indicators, "INVALID_RESOURCE_STRUCTURE_REJECTED")

    eff_resources = tuple(safe_resources) if safe_resources else ("invalid:target_resource",)

    # 3. Validation passive des conditions contextuelles
    safe_conditions: list[str] = []
    if type(conditions) not in (tuple, list):
        _append_unique(risk_indicators, "INVALID_CONDITION_CONTAINER_REJECTED")
    else:
        for c in conditions:
            if type(c) is str:
                s_c = c.strip()
                if s_c:
                    safe_conditions.append(s_c)
                else:
                    _append_unique(risk_indicators, "INVALID_CONDITION_STRUCTURE_REJECTED")
            else:
                _append_unique(risk_indicators, "INVALID_CONDITION_STRUCTURE_REJECTED")

    eff_conditions = tuple(safe_conditions)

    # 4. Filtrage passif et sécurisé de kxpost_decision_record_ids
    valid_record_ids: list[str] = []
    if type(kxpost_decision_record_ids) not in (tuple, list):
        _append_unique(risk_indicators, "INVALID_RECORD_CONTAINER_REJECTED")
    else:
        for item in kxpost_decision_record_ids:
            if type(item) is str:
                s_item = item.strip()
                if not s_item:
                    _append_unique(risk_indicators, "INVALID_RECORD_STRUCTURE_REJECTED")
                else:
                    valid_record_ids.append(s_item)
            elif isinstance(item, dict):
                # Dictionnaires auto-déclarés ou de falsification
                _append_unique(risk_indicators, "SELF_ATTESTATION_REJECTED")
                _append_unique(risk_indicators, "FORGED_OBSERVATION_OBJECT_REJECTED")
            else:
                # Objets hostiles ou forgés sans str valide : aucun dunder exécuté
                _append_unique(risk_indicators, "FORGED_OBSERVATION_OBJECT_REJECTED")
                _append_unique(risk_indicators, "INVALID_RECORD_STRUCTURE_REJECTED")

    # 5. Acquisition et vérification canonique des observations Rail A
    batch_observations: tuple[RailAVerifiedObservation, ...] = ()
    if valid_record_ids:
        batch_obs, batch_unknowns, batch_risks = load_and_verify_rail_a_observations_batch(
            valid_record_ids,
            kx108_decision_dir=kx108_decision_dir,
            pre_execution_context_dir=pre_execution_context_dir,
            sealed_receipt_dir=sealed_receipt_dir,
            sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
            test_contract_results_dir=test_contract_results_dir,
        )
        batch_observations = batch_obs
        for u in batch_unknowns:
            _append_unique(unknowns, u)
        for r in batch_risks:
            _append_unique(risk_indicators, r)

    # 6. Projection contextuelle stricte des observations vérifiées
    for obs in batch_observations:
        matches = True

        # Domaine
        if obs.domain != safe_domain:
            _append_unique(risk_indicators, "CONTEXT_MISMATCH:DOMAIN")
            matches = False

        # Tâche
        if obs.task_ref != safe_task_ref:
            _append_unique(risk_indicators, "CONTEXT_MISMATCH:TASK")
            matches = False

        # Ressources cibles
        if obs.mutated_target_path in safe_resources:
            _append_unique(risk_indicators, "MUTATED_PATH_NOT_AN_EXECUTING_MECHANISM")
            matches = False

        if obs.executing_mechanism_ref not in safe_resources:
            _append_unique(risk_indicators, "CONTEXT_MISMATCH:TARGET_RESOURCE")
            matches = False

        # Conditions
        for cond in safe_conditions:
            if cond.startswith("mutated_target_path:"):
                expected_path = cond[len("mutated_target_path:"):].strip()
                if obs.mutated_target_path != expected_path:
                    _append_unique(risk_indicators, "CONTEXT_MISMATCH:MUTATED_TARGET_PATH")
                    _append_unique(risk_indicators, "CONTEXT_MISMATCH:CONDITIONS")
                    matches = False
            elif cond.startswith("test_contract_hash:"):
                expected_hash = cond[len("test_contract_hash:"):].strip()
                if obs.test_contract_hash != expected_hash:
                    _append_unique(risk_indicators, "CONTEXT_MISMATCH:TEST_CONTRACT_HASH")
                    _append_unique(risk_indicators, "CONTEXT_MISMATCH:CONDITIONS")
                    matches = False
            else:
                if cond not in obs.conditions:
                    _append_unique(risk_indicators, "CONTEXT_MISMATCH:CONDITIONS")
                    matches = False

        if matches:
            # Référencer l'ancre post-décision canonique
            kxpost_ref = next(
                (ref for ref in obs.anchor_refs if ref.startswith("kxpost:")),
                f"kxpost:{obs.observation_id}",
            )
            if kxpost_ref not in evidence_refs:
                evidence_refs.append(kxpost_ref)

    # 7. Préservation des invariants épistémiques UNKNOWN_COMPETENCE
    if not evidence_refs:
        _append_unique(unknowns, "NO_HISTORICAL_EVIDENCE")

    _append_unique(unknowns, "M42_STATISTICAL_THRESHOLDS_PENDING")

    return ContextualCompetenceProfile(
        evaluation_id=safe_evaluation_id,
        domain=safe_domain,
        task_ref=safe_task_ref,
        target_resources=eff_resources,
        conditions=eff_conditions,
        competence_regime=CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=tuple(evidence_refs),
        unknowns=tuple(unknowns),
        contradictions=(),
        risk_indicators=tuple(risk_indicators),
        advisory_notes="Rail A verified observations contextual projection V1 (advisory only, unpromoted).",
    )


__all__ = [
    "B11_EFFECTS",
    "evaluate_rail_a_contextual_competence",
]
