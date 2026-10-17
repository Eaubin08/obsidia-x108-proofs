"""M42 B11 Compétence & Calibration — Contrats minimaux V1.

Source de vérité :
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_DOCTRINE_V1.md
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_SPEC_V1.md

Représentation pure, transitoire et consultative :
- Aucun I/O, aucune persistance durable dans B10 (memory_write=False).
- Aucune émission d'action (emits_act=False).
- Aucune mutation du noyau (kernel_mutation=False).
- Autorité de décision exclusive KX108_ONLY.
- Aucune admissibilité ni sélection d'organe (réservé à B12 / M43).
"""
from __future__ import annotations

from types import MappingProxyType as _MappingProxyType
from typing import Any, Sequence


class CompetenceRegime:
    """Régimes épistémiques d'évaluation d'aptitude selon la doctrine M42 §4.2."""
    EVIDENCED_COMPETENCE: str = "EVIDENCED_COMPETENCE"
    EVIDENCED_INCOMPETENCE: str = "EVIDENCED_INCOMPETENCE"
    UNKNOWN_COMPETENCE: str = "UNKNOWN_COMPETENCE"


_VALID_REGIMES: frozenset[str] = frozenset({
    CompetenceRegime.EVIDENCED_COMPETENCE,
    CompetenceRegime.EVIDENCED_INCOMPETENCE,
    CompetenceRegime.UNKNOWN_COMPETENCE,
})

B11_EFFECTS: _MappingProxyType = _MappingProxyType({
    "memory_write": False,
    "emits_act": False,
    "kernel_mutation": False,
    "decision_authority": "KX108_ONLY",
    "advisory_only": True,
    "b12_selection": False,
})


def _validate_score(val: Any, name: str) -> float | None:
    """Valide qu'un score est un flottant dans [0.0, 1.0] ou None."""
    if val is None:
        return None
    if type(val) is bool or not isinstance(val, (int, float)):
        raise ValueError(f"M42_INVALID_SCORE: {name} must be a numeric float, got {type(val).__name__}")
    f_val = float(val)
    if f_val < 0.0 or f_val > 1.0:
        raise ValueError(f"M42_INVALID_SCORE: {name} must be in [0.0, 1.0], got {f_val}")
    return f_val


class ContextualCompetenceProfile:
    """Profil d'aptitude contextualisé et immuable B11 (Doctrine M42 §3.2, §6.1)."""

    __slots__ = (
        "_evaluation_id",
        "_domain",
        "_task_ref",
        "_conditions",
        "_target_resources",
        "_competence_regime",
        "_reliability_score",
        "_confidence_score",
        "_calibration_metric",
        "_evidence_refs",
        "_unknowns",
        "_contradictions",
        "_risk_indicators",
        "_advisory_notes",
        "_hash",
        "_initialized",
    )

    def __init__(
        self,
        evaluation_id: str,
        domain: str,
        task_ref: str | None = None,
        conditions: Sequence[str] = (),
        target_resources: Sequence[str] | None = None,
        competence_regime: str | None = None,
        reliability_score: float | None = None,
        confidence_score: float = 0.0,
        calibration_metric: float | None = None,
        evidence_refs: Sequence[str] = (),
        unknowns: Sequence[str] = (),
        contradictions: Sequence[str] = (),
        risk_indicators: Sequence[str] = (),
        advisory_notes: str = "",
        # Aliases doctrinaux acceptés
        task_fingerprint: str | None = None,
        target_resource_or_composition: Sequence[str] | None = None,
    ) -> None:
        # Résolution des alias
        eff_task_ref = task_ref if task_ref is not None else task_fingerprint
        eff_resources = target_resources if target_resources is not None else target_resource_or_composition

        # Validation des identifiants requis
        if not isinstance(evaluation_id, str) or not evaluation_id.strip():
            raise ValueError(f"M42_EMPTY_IDENTIFIER: evaluation_id must be a non-empty string, got {evaluation_id!r}")
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError(f"M42_EMPTY_IDENTIFIER: domain must be a non-empty string, got {domain!r}")
        if not isinstance(eff_task_ref, str) or not eff_task_ref.strip():
            raise ValueError(f"M42_EMPTY_IDENTIFIER: task_ref must be a non-empty string, got {eff_task_ref!r}")

        # Validation du régime épistémique
        if competence_regime not in _VALID_REGIMES:
            raise ValueError(f"M42_INVALID_REGIME: {competence_regime!r} not in {sorted(_VALID_REGIMES)}")

        # Validation des scores
        val_rel = _validate_score(reliability_score, "reliability_score")
        val_conf = _validate_score(confidence_score, "confidence_score")
        if val_conf is None:
            raise ValueError("M42_INVALID_SCORE: confidence_score cannot be None")
        val_calib = _validate_score(calibration_metric, "calibration_metric")

        # Détachement profond des séquences mutables
        t_conditions = tuple(str(c) for c in conditions) if conditions else ()
        t_resources = tuple(str(r) for r in eff_resources) if eff_resources else ()
        t_evidence = tuple(str(e) for e in evidence_refs) if evidence_refs else ()
        t_unknowns = tuple(str(u) for u in unknowns) if unknowns else ()
        t_contradictions = tuple(str(c) for c in contradictions) if contradictions else ()
        t_risks = tuple(str(r) for r in risk_indicators) if risk_indicators else ()

        # Validation de présence d'au moins une ressource
        if not t_resources:
            raise ValueError("M42_EMPTY_RESOURCES: target_resources cannot be empty")

        # Invariants spécifiques sous UNKNOWN_COMPETENCE (Doctrine §4.1, §4.2)
        if competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE:
            if val_conf != 0.0:
                raise ValueError(
                    f"M42_UNKNOWN_REGIME_ZERO_CONFIDENCE: UNKNOWN_COMPETENCE requires confidence_score=0.0, got {val_conf}"
                )
            if val_rel is not None:
                raise ValueError(
                    f"M42_UNKNOWN_REGIME_NO_RELIABILITY: UNKNOWN_COMPETENCE requires reliability_score=None, got {val_rel}"
                )
            if val_calib is not None:
                raise ValueError(
                    f"M42_UNKNOWN_REGIME_NO_CALIBRATION: UNKNOWN_COMPETENCE requires calibration_metric=None, got {val_calib}"
                )
            if not t_unknowns:
                raise ValueError(
                    "M42_UNKNOWN_REGIME_REQUIRES_UNKNOWNS: UNKNOWN_COMPETENCE requires at least one non-empty unknown"
                )

        # Affectation protégée des attributs
        super().__setattr__("_evaluation_id", evaluation_id.strip())
        super().__setattr__("_domain", domain.strip())
        super().__setattr__("_task_ref", eff_task_ref.strip())
        super().__setattr__("_conditions", t_conditions)
        super().__setattr__("_target_resources", t_resources)
        super().__setattr__("_competence_regime", competence_regime)
        super().__setattr__("_reliability_score", val_rel)
        super().__setattr__("_confidence_score", val_conf)
        super().__setattr__("_calibration_metric", val_calib)
        super().__setattr__("_evidence_refs", t_evidence)
        super().__setattr__("_unknowns", t_unknowns)
        super().__setattr__("_contradictions", t_contradictions)
        super().__setattr__("_risk_indicators", t_risks)
        super().__setattr__("_advisory_notes", str(advisory_notes) if advisory_notes else "")
        super().__setattr__(
            "_hash",
            hash((
                self._evaluation_id,
                self._domain,
                self._task_ref,
                self._conditions,
                self._target_resources,
                self._competence_regime,
                self._reliability_score,
                self._confidence_score,
                self._calibration_metric,
                self._evidence_refs,
                self._unknowns,
                self._contradictions,
                self._risk_indicators,
                self._advisory_notes,
            )),
        )
        super().__setattr__("_initialized", True)

    @property
    def evaluation_id(self) -> str:
        return self._evaluation_id

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def task_ref(self) -> str:
        return self._task_ref

    @property
    def task_fingerprint(self) -> str:
        return self._task_ref

    @property
    def conditions(self) -> tuple[str, ...]:
        return self._conditions

    @property
    def target_resources(self) -> tuple[str, ...]:
        return self._target_resources

    @property
    def target_resource_or_composition(self) -> tuple[str, ...]:
        return self._target_resources

    @property
    def competence_regime(self) -> str:
        return self._competence_regime

    @property
    def reliability_score(self) -> float | None:
        return self._reliability_score

    @property
    def confidence_score(self) -> float:
        return self._confidence_score

    @property
    def calibration_metric(self) -> float | None:
        return self._calibration_metric

    @property
    def evidence_refs(self) -> tuple[str, ...]:
        return self._evidence_refs

    @property
    def unknowns(self) -> tuple[str, ...]:
        return self._unknowns

    @property
    def contradictions(self) -> tuple[str, ...]:
        return self._contradictions

    @property
    def risk_indicators(self) -> tuple[str, ...]:
        return self._risk_indicators

    @property
    def advisory_notes(self) -> str:
        return self._advisory_notes

    def __setattr__(self, key: str, value: Any) -> None:
        if getattr(self, "_initialized", False):
            raise AttributeError("ContextualCompetenceProfile is immutable")
        super().__setattr__(key, value)

    def __delattr__(self, key: str) -> None:
        raise AttributeError("ContextualCompetenceProfile is immutable")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ContextualCompetenceProfile):
            return False
        return (
            self._evaluation_id == other._evaluation_id
            and self._domain == other._domain
            and self._task_ref == other._task_ref
            and self._conditions == other._conditions
            and self._target_resources == other._target_resources
            and self._competence_regime == other._competence_regime
            and self._reliability_score == other._reliability_score
            and self._confidence_score == other._confidence_score
            and self._calibration_metric == other._calibration_metric
            and self._evidence_refs == other._evidence_refs
            and self._unknowns == other._unknowns
            and self._contradictions == other._contradictions
            and self._risk_indicators == other._risk_indicators
            and self._advisory_notes == other._advisory_notes
        )

    def __hash__(self) -> int:
        return self._hash

    def __repr__(self) -> str:
        return (
            f"ContextualCompetenceProfile(evaluation_id={self._evaluation_id!r}, "
            f"domain={self._domain!r}, task_ref={self._task_ref!r}, "
            f"regime={self._competence_regime!r}, confidence={self._confidence_score})"
        )
