"""M42 B11 Compétence & Calibration — Adaptateur d'Observation Cognitive Brody V1.

Source doctrinale :
  docs/architecture/M42_B11_BRODY_COGNITIVE_OBSERVATION_SPEC_V1.md

Rôle du module :
  Adaptateur consultatif, passif et en lecture seule stricte permettant d'observer
  et d'évaluer les cycles cognitifs de Brody sans jamais confondre trace d'exécution,
  pureté de réponse, conformité documentaire et compétence empirique.

Garanties de gouvernance :
  - Respect absolu de B11_EFFECTS (memory_write=False, emits_act=False,
    kernel_mutation=False, decision_authority="KX108_ONLY", b12_selection=False).
  - Aucune promotion prématurée : maintien impératif sous CompetenceRegime.UNKNOWN_COMPETENCE
    avec confidence_score=0.0, reliability_score=None, calibration_metric=None.
  - Séparation stricte des mécanismes (rejet immédiat de toute observation Rail A sous
    CAUSAL_ATTRIBUTION_MISMATCH).
  - Rejet fail-closed immédiat de tout reçu auto-attesté (SELF_ATTESTATION_REJECTED) ou
    d'oracle circulaire (CIRCULAR_SELF_REFERENTIAL / TAUTOLOGICAL_ORACLE_REJECTED).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.cognition.b11.contracts import (
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)
import app.world_model as wm


@dataclass(frozen=True)
class BrodyCognitiveObservationV1:
    """Observation cognitive consultative et immuable d'un cycle Brody V1."""

    # Groupe A : Identité
    observation_id: str
    execution_id: str
    task_family: str
    task_ref: str
    mechanism_ref: str
    mechanism_version: str
    input_context_digest: str | None

    # Groupe B : Observation
    observable_response: str | None
    expressed_uncertainty_status: str
    components_health_status: dict[str, str] = field(default_factory=dict)
    documentary_refs: tuple[str, ...] = ()
    documentary_status: str = "ABSENT"
    external_provider_called: bool = False
    external_provider_model: str | None = None
    governance_compliance: bool = True

    # Groupe C : Garanties
    structural_validation_status: str = "VALID"
    replay_status: str = "NOT_REPLAYABLE"
    integrity_verification_status: str = "EPHEMERAL_UNSEALED"
    ground_truth_status: str = "MISSING"
    provenance_status: str = "PROVENANCE_UNESTABLISHED"
    attribution_status: str = "STACK_ONLY"

    # Groupe D : Évaluation
    evaluation_outcome: str = "INDETERMINATE"
    evaluation_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convertit l'observation en dictionnaire sérialisable."""
        return asdict(self)


def evaluate_brody_cognitive_observation(
    receipt: dict[str, Any] | None = None,
    candidate_response: str | None = None,
    ground_truth_pin: Any | None = None,
    bundles: Sequence[Any] = (),
    hypothesis_set: Any | None = None,
    oracle: dict[str, Any] | None = None,
    candidate_claim: Any | None = None,
    context_family: str = "COGNITIVE_SYNTHESIS",
    task_ref: str = "COGNITIVE_RESOLUTION",
    mechanism_ref: str = "brody:cognitive_resolution:V1",
    mechanism_version: str = "REAL_COGNITIVE_JOIN_C1_V1",
    **kwargs: Any,
) -> BrodyCognitiveObservationV1:
    """Évalue consultativement une observation cognitive de Brody face à ses preuves.

    Applique rigoureusement les frontières doctrinales M42 B11 :
    - Rejet immédiat de mauvaise attribution causale (Rail A -> Brody).
    - Rejet fail-closed immédiat de tout reçu portant des auto-attestations.
    - Rejet immédiat de tout oracle de test circulaire ou auto-référentiel.
    - Traçabilité de l'appel modèle externe sans causalité inférée.
    - Préservation d'ambiguïté évaluée en ABSTAIN_CORRECT uniquement sous oracle conforme.
    - Abstention ou trace éphémère sans oracle maintenue en INDETERMINATE.
    """
    # 1. Vérification d'attribution causale croisée (Rail A / tooling_build)
    if receipt is not None and isinstance(receipt, dict):
        rec_domain = str(receipt.get("domain", ""))
        rec_mech = str(receipt.get("executing_mechanism_ref", receipt.get("mechanism_ref", "")))
        if (
            rec_domain == "tooling_build"
            or rec_mech.startswith("rail_a:")
            or "rail_a" in rec_mech
            or "mutated_target_path" in receipt
        ):
            return BrodyCognitiveObservationV1(
                observation_id=f"brody-cogo-mismatch-{hashlib.sha256(str(receipt).encode('utf-8')).hexdigest()[:16]}",
                execution_id=str(receipt.get("execution_id", "mismatch-exec")),
                task_family=context_family,
                task_ref=str(receipt.get("task_ref", task_ref)),
                mechanism_ref=rec_mech or "mismatched:rail_a",
                mechanism_version="MISMATCHED",
                input_context_digest=None,
                observable_response=None,
                expressed_uncertainty_status="UNESTABLISHED",
                components_health_status={},
                documentary_refs=(),
                documentary_status="ABSENT",
                external_provider_called=False,
                external_provider_model=None,
                governance_compliance=False,
                structural_validation_status="INVALID",
                replay_status="NOT_REPLAYABLE",
                integrity_verification_status="EPHEMERAL_UNSEALED",
                ground_truth_status="MISSING",
                provenance_status="PROVENANCE_UNESTABLISHED",
                attribution_status="STACK_ONLY",
                evaluation_outcome="ERROR",
                evaluation_notes="CAUSAL_ATTRIBUTION_MISMATCH: Rail A payload rejected for Brody cognitive observation",
            )

    # 2. Vérification des tentatives de falsification ou d'auto-attestation
    if receipt is not None and isinstance(receipt, dict):
        forbidden_self_keys = {"evaluation_outcome", "is_verified", "trusted_by", "self_certified"}
        found_forbidden = sorted(k for k in forbidden_self_keys if k in receipt)
        if found_forbidden:
            sig_id = str(receipt.get("signal_id", "forged-signal"))
            return BrodyCognitiveObservationV1(
                observation_id=f"brody-cogo-forged-{hashlib.sha256(sig_id.encode('utf-8')).hexdigest()[:16]}",
                execution_id=sig_id,
                task_family=context_family,
                task_ref=task_ref,
                mechanism_ref=mechanism_ref,
                mechanism_version=str(receipt.get("version", mechanism_version)),
                input_context_digest=receipt.get("input_context_digest"),
                observable_response=None,
                expressed_uncertainty_status="UNESTABLISHED",
                components_health_status={},
                documentary_refs=(),
                documentary_status="ABSENT",
                external_provider_called=False,
                external_provider_model=None,
                governance_compliance=False,
                structural_validation_status="INVALID",
                replay_status="NOT_REPLAYABLE",
                integrity_verification_status="EPHEMERAL_UNSEALED",
                ground_truth_status="MISSING",
                provenance_status="PROVENANCE_UNESTABLISHED",
                attribution_status="STACK_ONLY",
                evaluation_outcome="ERROR",
                evaluation_notes=f"SELF_ATTESTATION_REJECTED: receipt contains illegal self-attestation keys: {found_forbidden}",
            )

    # 3. Vérification de circularité ou auto-référentialité de l'oracle de test
    oracle_to_check = oracle if oracle is not None else (ground_truth_pin if isinstance(ground_truth_pin, dict) else None)
    if oracle_to_check is not None:
        source_val = str(oracle_to_check.get("source", "")).upper()
        if "BRODY" in source_val or "SELF" in source_val:
            return BrodyCognitiveObservationV1(
                observation_id=f"brody-cogo-circular-{hashlib.sha256(str(candidate_response).encode('utf-8')).hexdigest()[:16]}",
                execution_id="exec-circular",
                task_family=context_family,
                task_ref=task_ref,
                mechanism_ref=mechanism_ref,
                mechanism_version=mechanism_version,
                input_context_digest=hashlib.sha256(str(candidate_response).encode("utf-8")).hexdigest() if candidate_response else None,
                observable_response=candidate_response,
                expressed_uncertainty_status="RESOLVED",
                components_health_status={},
                documentary_refs=(),
                documentary_status="UNVERIFIED",
                external_provider_called=False,
                external_provider_model=None,
                governance_compliance=True,
                structural_validation_status="VALID",
                replay_status="NOT_REPLAYABLE",
                integrity_verification_status="EPHEMERAL_UNSEALED",
                ground_truth_status="CIRCULAR_SELF_REFERENTIAL",
                provenance_status="PROVENANCE_UNESTABLISHED",
                attribution_status="STACK_ONLY",
                evaluation_outcome="ERROR",
                evaluation_notes="TAUTOLOGICAL_ORACLE_REJECTED: oracle is circular or self-referential from Brody output",
            )

    # 4. Traitement des ensembles d'hypothèses d'ambiguïté (B7 / M41)
    if hypothesis_set is not None:
        if (
            not isinstance(hypothesis_set, wm.WorldHypothesisSet)
            or not hasattr(hypothesis_set, "members")
            or not isinstance(hypothesis_set.members, tuple)
            or len(hypothesis_set.members) < 2
            or not all(isinstance(m, wm.WorldStateHypothesis) for m in hypothesis_set.members)
        ):
            return BrodyCognitiveObservationV1(
                observation_id=f"brody-cogo-invalid-m41-{hashlib.sha256(str(hypothesis_set).encode('utf-8')).hexdigest()[:16]}",
                execution_id="invalid-m41-exec",
                task_family=context_family,
                task_ref=task_ref,
                mechanism_ref=mechanism_ref,
                mechanism_version=mechanism_version,
                input_context_digest=None,
                observable_response=None,
                expressed_uncertainty_status="UNESTABLISHED",
                components_health_status={},
                documentary_refs=(),
                documentary_status="ABSENT",
                external_provider_called=False,
                external_provider_model=None,
                governance_compliance=True,
                structural_validation_status="INVALID",
                replay_status="NOT_REPLAYABLE",
                integrity_verification_status="EPHEMERAL_UNSEALED",
                ground_truth_status="MISSING",
                provenance_status="PROVENANCE_UNESTABLISHED",
                attribution_status="STACK_ONLY",
                evaluation_outcome="ERROR",
                evaluation_notes="INVALID_M41_HYPOTHESIS_SET: object must be an authentic WorldHypothesisSet with at least 2 WorldStateHypothesis members",
            )

        expressed_uncertainty = "AMBIGUOUS_COEXISTING_HYPOTHESES"

        if oracle is not None and isinstance(oracle, dict) and oracle.get("requires_abstention") is True:
            outcome = "ABSTAIN_CORRECT"
            notes = "ABSTAIN_CORRECT: Ambiguity maintained under oracle confirming abstention requirement"
            gt_status = "INDEPENDENT_ORACLE_PINNED"
        else:
            outcome = "INDETERMINATE"
            notes = "INDETERMINATE: Ambiguous hypothesis set without confirming oracle"
            gt_status = "MISSING" if oracle is None else "INDEPENDENT_ORACLE_PINNED"

        set_id = getattr(hypothesis_set, "set_id", None) or "m41-hypothesis-set"
        input_digest = hashlib.sha256(str(set_id).encode("utf-8")).hexdigest()

        return BrodyCognitiveObservationV1(
            observation_id=f"brody-cogo-ambig-{hashlib.sha256(str(set_id).encode('utf-8')).hexdigest()[:16]}",
            execution_id=str(set_id),
            task_family=context_family,
            task_ref=task_ref,
            mechanism_ref=mechanism_ref,
            mechanism_version=mechanism_version,
            input_context_digest=input_digest,
            observable_response=None,
            expressed_uncertainty_status=expressed_uncertainty,
            components_health_status={},
            documentary_refs=(),
            documentary_status="ABSENT",
            external_provider_called=False,
            external_provider_model=None,
            governance_compliance=True,
            structural_validation_status="VALID",
            replay_status="NOT_REPLAYABLE",
            integrity_verification_status="EPHEMERAL_UNSEALED",
            ground_truth_status=gt_status,
            provenance_status="PROVENANCE_UNESTABLISHED",
            attribution_status="STACK_ONLY",
            evaluation_outcome=outcome,
            evaluation_notes=notes,
        )

    # 5. Extraction des champs d'observation depuis le reçu ou les arguments
    eff_execution_id = "exec-ephemeral"
    eff_observable_response = candidate_response
    eff_components_health: dict[str, str] = {}
    eff_gov_compliance = True
    eff_external_called = False
    eff_external_model: str | None = None
    eff_attribution_status = "STACK_ONLY"
    eff_expressed_uncertainty = "RESOLVED"
    eff_input_context_digest: str | None = None
    eff_structural_status = "VALID"

    if receipt is not None and isinstance(receipt, dict):
        eff_execution_id = str(receipt.get("signal_id") or receipt.get("execution_id") or "exec-ephemeral")
        if candidate_response is None:
            eff_observable_response = receipt.get("brody_cognitive_response")

        if isinstance(receipt.get("components"), dict):
            eff_components_health = dict(receipt["components"])

        eff_gov_compliance = (
            receipt.get("readonly") is True
            and receipt.get("decision_authority") == "KX108_ONLY"
            and receipt.get("emits_act", False) is False
        )

        model_calls = receipt.get("model_calls", 0)
        ext_model = receipt.get("external_model")
        if (isinstance(model_calls, (int, float)) and model_calls > 0) or ext_model:
            eff_external_called = True
            eff_external_model = str(ext_model) if ext_model else None
            eff_attribution_status = "STACK_PLUS_EXTERNAL_MODEL"

        status_str = str(receipt.get("status", ""))
        if status_str == "CLARIFICATION_HOLD":
            eff_expressed_uncertainty = "CLARIFICATION_HOLD"
        elif status_str in ("READY_SHADOW_READONLY", "BLOCKED_READONLY"):
            eff_expressed_uncertainty = "RESOLVED"

        if "input_context_digest" in receipt:
            raw_digest = receipt.get("input_context_digest")
            eff_input_context_digest = str(raw_digest) if raw_digest is not None else None
        elif "semantic_query_snapshot" in receipt and isinstance(receipt["semantic_query_snapshot"], dict):
            orig_msg = receipt["semantic_query_snapshot"].get("original_message", "")
            eff_input_context_digest = hashlib.sha256(str(orig_msg).encode("utf-8")).hexdigest()
    else:
        if candidate_response is not None:
            eff_input_context_digest = hashlib.sha256(candidate_response.encode("utf-8")).hexdigest()

    # 6. Évaluation documentaire et confrontation à l'oracle indépendant
    eff_doc_refs: list[str] = []
    eff_doc_status = "ABSENT"
    eff_gt_status = "MISSING"
    eff_outcome = "INDETERMINATE"
    eff_notes = "INDETERMINATE: Ephemeral observation without independent ground truth oracle pin"

    if bundles:
        for b in bundles:
            if hasattr(b, "claim") and hasattr(b.claim, "claim_id"):
                eff_doc_refs.append(str(b.claim.claim_id))
        eff_doc_status = "CORROBORATED" if any(getattr(b, "source_verified", False) for b in bundles) else "UNVERIFIED"

    if candidate_claim is not None:
        if hasattr(candidate_claim, "claim_id"):
            eff_doc_refs.append(str(candidate_claim.claim_id))

    if ground_truth_pin is not None:
        eff_gt_status = "INDEPENDENT_ORACLE_PINNED"

        expected_statement: str | None = None
        if isinstance(ground_truth_pin, dict):
            expected_statement = ground_truth_pin.get("statement")
        elif hasattr(ground_truth_pin, "statement"):
            expected_statement = getattr(ground_truth_pin, "statement")

        tested_statement: str | None = None
        if candidate_claim is not None:
            if hasattr(candidate_claim, "content") and isinstance(candidate_claim.content, dict):
                tested_statement = candidate_claim.content.get("statement")
            elif hasattr(candidate_claim, "statement"):
                tested_statement = getattr(candidate_claim, "statement")
        elif candidate_response is not None:
            tested_statement = candidate_response
        elif eff_observable_response is not None:
            tested_statement = eff_observable_response

        if expected_statement is not None and tested_statement is not None:
            if tested_statement == expected_statement:
                eff_outcome = "PASS"
                eff_doc_status = "CORROBORATED"
                eff_notes = "PASS: Candidate statement corroborated against independent ground truth pin"
            else:
                eff_outcome = "FAIL"
                eff_doc_status = "CONTRADICTED"
                eff_notes = (
                    f"FACTUAL_CONTRADICTION: Candidate statement '{tested_statement}' "
                    f"contradicts independent ground truth pin '{expected_statement}'"
                )
        else:
            eff_outcome = "INDETERMINATE"
            eff_notes = "INDETERMINATE: Ground truth pin provided but statement comparison inconclusive"

    obs_id = (
        f"brody-cogo-"
        f"{hashlib.sha256((eff_execution_id + context_family + str(eff_observable_response)).encode('utf-8')).hexdigest()[:16]}"
    )

    return BrodyCognitiveObservationV1(
        observation_id=obs_id,
        execution_id=eff_execution_id,
        task_family=context_family,
        task_ref=task_ref,
        mechanism_ref=mechanism_ref,
        mechanism_version=mechanism_version,
        input_context_digest=eff_input_context_digest,
        observable_response=eff_observable_response,
        expressed_uncertainty_status=eff_expressed_uncertainty,
        components_health_status=eff_components_health,
        documentary_refs=tuple(eff_doc_refs),
        documentary_status=eff_doc_status,
        external_provider_called=eff_external_called,
        external_provider_model=eff_external_model,
        governance_compliance=eff_gov_compliance,
        structural_validation_status=eff_structural_status,
        replay_status="NOT_REPLAYABLE",
        integrity_verification_status="EPHEMERAL_UNSEALED",
        ground_truth_status=eff_gt_status,
        provenance_status="PROVENANCE_UNESTABLISHED",
        attribution_status=eff_attribution_status,
        evaluation_outcome=eff_outcome,
        evaluation_notes=eff_notes,
    )


def load_and_verify_brody_observation(
    data: dict[str, Any] | str | Path,
    **kwargs: Any,
) -> BrodyCognitiveObservationV1:
    """Charge et vérifie passivement une observation cognitive Brody."""
    if isinstance(data, (str, Path)):
        p = Path(data)
        if not p.is_file():
            raise FileNotFoundError(f"BRODY_OBSERVATION_FILE_NOT_FOUND: {p}")
        with open(p, "r", encoding="utf-8") as f:
            payload = json.load(f)
    elif isinstance(data, dict):
        payload = data
    else:
        raise TypeError(f"M42_INVALID_PAYLOAD_TYPE: expected dict, str or Path, got {type(data).__name__}")

    return evaluate_brody_cognitive_observation(receipt=payload, **kwargs)


def project_b11_competence_profile(
    observations: Sequence[BrodyCognitiveObservationV1] = (),
    domain: str = "cognition",
    task_ref: str = "COGNITIVE_RESOLUTION",
    conditions: Sequence[str] = (),
    target_resources: Sequence[str] = ("brody:cognitive_resolution",),
    evaluation_id: str | None = None,
) -> ContextualCompetenceProfile:
    """Projette un profil de compétence contextuelle B11 pour le mécanisme Brody.

    Garantie doctrinale V1 inviolable :
    Maintien absolu sous CompetenceRegime.UNKNOWN_COMPETENCE avec confidence_score=0.0,
    reliability_score=None, calibration_metric=None et b12_selection=False.
    """
    eff_eval_id = evaluation_id or f"b11-brody-{domain}-{task_ref}"
    evidence_refs = tuple(obs.observation_id for obs in observations if hasattr(obs, "observation_id"))

    unknowns_list = ["STATISTICAL_SAMPLE_SIZE_INSUFFICIENT", "M42_STATISTICAL_THRESHOLDS_PENDING"]
    if not evidence_refs:
        unknowns_list.insert(0, "NO_HISTORICAL_EVIDENCE")

    return ContextualCompetenceProfile(
        evaluation_id=eff_eval_id,
        domain=domain,
        task_ref=task_ref,
        conditions=conditions,
        target_resources=target_resources,
        competence_regime=CompetenceRegime.UNKNOWN_COMPETENCE,
        confidence_score=0.0,
        reliability_score=None,
        calibration_metric=None,
        evidence_refs=evidence_refs,
        unknowns=tuple(unknowns_list),
        advisory_notes="HOLD: Consultative observation only. No competence promotion authorized.",
    )
