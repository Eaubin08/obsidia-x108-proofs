"""M42 B11 Compétence & Calibration — Évaluateur Contextuel Fail-Closed V1.

Source de vérité :
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_DOCTRINE_V1.md
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_SPEC_V1.md
  docs/architecture/M42_B11_FAIL_CLOSED_SPEC_V1.md

Règles de décision Fail-Closed (FC-01 à FC-13) et Sécurité Passive Totale :
- Conteneurs passifs stricts : seuls list ou tuple natifs (type in (tuple, list)) sont acceptés.
- Enregistrements passifs stricts : seuls les dicts natifs (type is dict) sont inspectés.
- Valeurs passives strictes : seuls les types scalaires natifs (str, bool) sont lus.
- Aucun str(obj), aucun bool(obj), aucun getattr, aucun == contre un objet non-str.
- Zéro exécution de méthode dunder hostile (__iter__, __next__, __str__, __eq__, __getattr__, @property).
- En cas de structure invalide, retombée immédiate et fail-closed sur UNKNOWN_COMPETENCE (conf=0.0, rel=None).
"""
from __future__ import annotations

from typing import Any, Sequence
from app.cognition.b11.contracts import (
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)


def _append_unique(target_list: list[str], code: str) -> None:
    """Ajoute un code diagnostique s'il n'est pas déjà présent."""
    if code not in target_list:
        target_list.append(code)


def evaluate_contextual_competence(
    evaluation_id: str,
    domain: str,
    task_ref: str,
    target_resources: Sequence[Any],
    conditions: Sequence[Any] = (),
    evidence_records: Sequence[Any] = (),
) -> ContextualCompetenceProfile:
    """Évalue l'aptitude contextualisée sous le régime fail-closed avec sécurité passive totale.

    En l'absence de registre d'ancrage indépendant vérifié, tout signal non
    authentifié ou auto-déclaré est rejeté comme preuve d'exécution. L'évaluateur
    retombe impérativement en UNKNOWN_COMPETENCE (confidence_score=0.0,
    reliability_score=None), conformément à la doctrine M32 et à la spécification FC-01..13.

    Sécurité passive totale :
    - Arguments contextuels validés par types natifs sans conversion implicite.
    - Conteneur evidence_records validé comme tuple ou list natif avant itération.
    - Seuls les dicts natifs sont traités.
    - Seules les valeurs scalaires natives de type attendu sont inspectées.
    - Zéro appel de méthode dunder ou dynamique sur des objets hostiles.
    """
    unknowns: list[str] = []
    risk_indicators: list[str] = []
    contradictions: list[str] = []
    evidence_refs: list[str] = []

    # 1. Validation passive stricte des arguments contextuels
    safe_eval_id = evaluation_id if type(evaluation_id) is str and evaluation_id.strip() else "eval-fallback"
    if type(evaluation_id) is not str or not evaluation_id.strip():
        _append_unique(risk_indicators, "INVALID_EVALUATION_ID_REJECTED")

    safe_domain = domain if type(domain) is str and domain.strip() else "domain-fallback"
    if type(domain) is not str or not domain.strip():
        _append_unique(risk_indicators, "INVALID_DOMAIN_REJECTED")

    safe_task_ref = task_ref if type(task_ref) is str and task_ref.strip() else "task-fallback"
    if type(task_ref) is not str or not task_ref.strip():
        _append_unique(risk_indicators, "INVALID_TASK_REF_REJECTED")

    # Validation passive de target_resources (sans str(obj) implicite)
    safe_resources: list[str] = []
    if type(target_resources) in (tuple, list):
        for r in target_resources:
            if type(r) is str and r.strip():
                safe_resources.append(r.strip())
            else:
                _append_unique(risk_indicators, "INVALID_RESOURCE_STRUCTURE_REJECTED")
    else:
        _append_unique(risk_indicators, "INVALID_RESOURCE_CONTAINER_REJECTED")

    if not safe_resources:
        safe_resources = ["resource-fallback-rejected"]

    # Validation passive de conditions (sans str(obj) implicite)
    safe_conditions: list[str] = []
    if type(conditions) in (tuple, list):
        for c in conditions:
            if type(c) is str and c.strip():
                safe_conditions.append(c.strip())
            else:
                _append_unique(risk_indicators, "INVALID_CONDITION_STRUCTURE_REJECTED")
    else:
        _append_unique(risk_indicators, "INVALID_CONDITION_CONTAINER_REJECTED")

    # 2. Validation passive stricte du conteneur evidence_records (FC-11)
    if type(evidence_records) not in (tuple, list):
        _append_unique(risk_indicators, "INVALID_CONTAINER_STRUCTURE_REJECTED")
        _append_unique(unknowns, "NO_HISTORICAL_EVIDENCE")
    elif not evidence_records:
        # FC-06: Absence totale de preuves
        _append_unique(unknowns, "NO_HISTORICAL_EVIDENCE")
    else:
        for rec in evidence_records:
            # Sécurité passive stricte (FC-08, FC-09) : seuls les dicts natifs sont traités
            if type(rec) is not dict:
                _append_unique(risk_indicators, "INVALID_RECORD_STRUCTURE_REJECTED")
                continue

            # FC-10: evidence_id doit être nativement un str
            ev_id = dict.get(rec, "evidence_id")
            if type(ev_id) is str and ev_id.strip():
                _append_unique(evidence_refs, ev_id.strip())
            elif ev_id is not None:
                _append_unique(risk_indicators, "INVALID_EVIDENCE_ID_REJECTED")

            # FC-02: Rejet de l'auto-attestation fournie par l'appelant
            # Vérification par identité stricte de booléen (aucun bool(obj) sur objet hostile)
            is_ver = dict.get(rec, "is_verified")
            is_auth = dict.get(rec, "is_authenticated")
            if is_ver is True or is_auth is True:
                _append_unique(risk_indicators, "SELF_ATTESTATION_REJECTED")

            # Extraction passive des champs avec vérification de type avant comparaison (FC-12)
            outcome = dict.get(rec, "declared_outcome")
            anchor = dict.get(rec, "anchor_ref")
            prov = dict.get(rec, "provenance")
            ext_receipt = dict.get(rec, "external_execution_receipt")
            b7_verd = dict.get(rec, "b7_verdict")
            gate = dict.get(rec, "x108_gate")

            # FC-01: Hash auto-signé non ancré dans un registre indépendant
            if anchor is None and type(outcome) is str and outcome == "SUCCESS":
                _append_unique(unknowns, "EVIDENCE_UNANCHORED")

            # FC-03: Statut B9 non scellé dans CognitivePath.path_id
            if ext_receipt is None and type(prov) is str and prov == "app.cognition.b9":
                _append_unique(unknowns, "B9_PATH_STATUS_UNSEALED")

            # FC-04: Non-conformité cognitive locale B7 REJECT (≠ incompétence technique)
            if type(prov) is str and prov == "app.cognition.b7.validation" and type(b7_verd) is str and b7_verd == "REJECT":
                _append_unique(contradictions, "B7_ROLE_NON_CONFORMANCE")

            # FC-05: Blocage de sécurité GuardX108 (COMPETENCE != AUTHORITY)
            if type(prov) is str and prov == "sigma.guard.GuardX108" and type(gate) is str and gate == "BLOCK":
                _append_unique(risk_indicators, "ACCESS_GATE_BLOCKED")

    # Invariant contractuel: UNKNOWN_COMPETENCE requiert au moins un diagnostic dans unknowns
    if not unknowns:
        _append_unique(unknowns, "NO_HISTORICAL_EVIDENCE")

    return ContextualCompetenceProfile(
        evaluation_id=safe_eval_id,
        domain=safe_domain,
        task_ref=safe_task_ref,
        target_resources=tuple(safe_resources),
        conditions=tuple(safe_conditions),
        competence_regime=CompetenceRegime.UNKNOWN_COMPETENCE,
        confidence_score=0.0,
        reliability_score=None,
        evidence_refs=tuple(evidence_refs),
        unknowns=tuple(unknowns),
        contradictions=tuple(contradictions),
        risk_indicators=tuple(risk_indicators),
        advisory_notes="B11 fail-closed evaluation: passive records only, unanchored evidence defaults strictly to UNKNOWN_COMPETENCE",
    )
