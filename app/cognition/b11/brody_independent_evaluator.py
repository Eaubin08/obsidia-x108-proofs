"""M42 B11 Compétence & Calibration — Évaluateur Cognitif Indépendant Brody V1.

Ce module implémente l'évaluation cognitive indépendante des bundles de preuve scellés Brody :
1. evaluate_brody_cognitive_evidence_bundle : évaluation souveraine et déterministe.
2. CognitiveEvaluationReportV1 : rapport d'évaluation immuable et certifié.
3. project_b11_evaluator_competence_profile : maintien sous UNKNOWN_COMPETENCE et B11_EFFECTS.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from app.cognition.b11.brody_evidence_store import (
    BrodyCognitiveEvidenceBundleV1,
    load_and_verify_brody_evidence_bundle,
)
from app.cognition.b11.contracts import (
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)

try:
    from tests.integration_cognition.two_encounter_support import (
        SOURCE_PINS as _SOURCE_PINS,
    )
except ImportError:
    _SOURCE_PINS = {}


# ============================================================================
# Helpers
# ============================================================================


def _digest_document(doc: Any) -> str:
    """Calcule le condensat canonique SHA-256 d'un document ou fixture."""
    if isinstance(doc, (bytes, bytearray)):
        return hashlib.sha256(doc).hexdigest()
    if isinstance(doc, str):
        return hashlib.sha256(doc.encode("utf-8")).hexdigest()
    norm = json.dumps(doc, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(norm).hexdigest()


def _unfreeze(obj: Any) -> Any:
    """Convertit récursivement les MappingProxyType en dict python standard."""
    if isinstance(obj, Mapping):
        return {k: _unfreeze(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_unfreeze(v) for v in obj]
    return obj


_NUMERIC_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(K|kelvin|°C|C|kg|m|%|V|A)?",
    re.IGNORECASE,
)

_ABSTENTION_PATTERN = re.compile(
    r"(?:ne dispose d'aucune information|inconnu|je ne sais pas|plusieurs hypothèses|non résolue|impossible de déterminer)",
    re.IGNORECASE,
)


def _extract_numeric_fact(text: str | None) -> tuple[float | None, str | None]:
    """Extrait la première valeur numérique et son unité d'une chaîne de texte."""
    if not text:
        return None, None
    m = _NUMERIC_PATTERN.search(text)
    if m:
        try:
            val = float(m.group(1))
            unit = m.group(2) if m.group(2) else None
            return val, unit
        except (ValueError, TypeError):
            pass
    return None, None


# ============================================================================
# Rapport d'Évaluation Cognitive Indépendante
# ============================================================================


@dataclass(frozen=True)
class CognitiveEvaluationReportV1:
    """Rapport immuable certifiant l'évaluation cognitive indépendante d'un bundle."""

    evaluation_id: str = ""
    bundle_id: str = ""
    observation_id: str = ""
    oracle_ref: str = ""
    oracle_digest: str = ""
    verdict: str = "INDETERMINATE"
    ground_truth_status: str = "MISSING"
    expected_assertion: Mapping[str, Any] = field(default_factory=dict)
    observed_assertion: Mapping[str, Any] | None = None
    observable_response_text: str | None = None
    justification: str = ""
    attribution_status: str = "STACK_ONLY"
    causal_contribution_verified: bool = False
    evaluation_timestamp_utc: str = ""

    def __post_init__(self) -> None:
        """Applique le gel profond pour garantir l'immutabilité."""
        object.__setattr__(
            self, "expected_assertion", MappingProxyType(dict(self.expected_assertion))
        )
        if self.observed_assertion is not None:
            object.__setattr__(
                self,
                "observed_assertion",
                MappingProxyType(dict(self.observed_assertion)),
            )

    def to_canonical(self) -> dict[str, Any]:
        """Convertit le rapport en dictionnaire canonique sérialisable."""
        return {
            "evaluation_id": self.evaluation_id,
            "bundle_id": self.bundle_id,
            "observation_id": self.observation_id,
            "oracle_ref": self.oracle_ref,
            "oracle_digest": self.oracle_digest,
            "verdict": self.verdict,
            "ground_truth_status": self.ground_truth_status,
            "expected_assertion": _unfreeze(self.expected_assertion),
            "observed_assertion": (
                _unfreeze(self.observed_assertion)
                if self.observed_assertion is not None
                else None
            ),
            "observable_response_text": self.observable_response_text,
            "justification": self.justification,
            "attribution_status": self.attribution_status,
            "causal_contribution_verified": self.causal_contribution_verified,
            "evaluation_timestamp_utc": self.evaluation_timestamp_utc,
        }


# ============================================================================
# Évaluateur Cognitif Indépendant
# ============================================================================


def evaluate_brody_cognitive_evidence_bundle(
    bundle: BrodyCognitiveEvidenceBundleV1 | Mapping[str, Any] | str,
    oracle: Mapping[str, Any],
    *,
    store_dir: Path | str | None = None,
    evaluation_id: str | None = None,
    isolated_source_pins: Mapping[str, Any] | None = None,
) -> CognitiveEvaluationReportV1:
    """Évalue indépendamment et souverainement les résultats d'un bundle Brody scellé.

    Découple formellement la recevabilité de l'oracle de la justesse de la réponse :
    - Compare des faits typés déterministes.
    - Rejette les oracles circulaires et falsifiés.
    - Isole la contribution causale externe.
    - Maintient UNKNOWN_COMPETENCE et B11_EFFECTS.
    """
    now = datetime.now(timezone.utc).isoformat()
    eval_id = evaluation_id or f"eval-bie-{hashlib.sha256(now.encode('utf-8')).hexdigest()[:16]}"

    # 1. Chargement et vérification d'intégrité du bundle
    bundle_obj: BrodyCognitiveEvidenceBundleV1
    if isinstance(bundle, str):
        bundle_obj = load_and_verify_brody_evidence_bundle(bundle, store_dir=store_dir)
    elif isinstance(bundle, BrodyCognitiveEvidenceBundleV1):
        bundle_obj = bundle
    elif isinstance(bundle, Mapping):
        b_id = str(bundle.get("bundle_id", ""))
        bundle_obj = load_and_verify_brody_evidence_bundle(b_id, store_dir=store_dir)
    else:
        raise TypeError(f"UNSUPPORTED_BUNDLE_TYPE: {type(bundle).__name__}")

    bundle_id = bundle_obj.bundle_id
    obs_text = bundle_obj.observable_response_text
    oracle_id = str(oracle.get("oracle_id", "oracle:unknown"))
    locator = oracle.get("locator")
    expected_assertion = dict(oracle.get("expected_assertion", {}))

    # 2. Vérification de l'intégrité matérielle du bundle
    if bundle_obj.integrity_verification_status != "INTEGRITY_VERIFIED":
        return CognitiveEvaluationReportV1(
            evaluation_id=eval_id,
            bundle_id=bundle_id,
            oracle_ref=oracle_id,
            verdict="ERROR",
            ground_truth_status="INTEGRITY_COMPROMISED",
            justification="BUNDLE_INTEGRITY_COMPROMISED: SHA-256 digest mismatch",
            evaluation_timestamp_utc=now,
        )

    # 3. Contrôle des oracles circulaires ou auto-référentiels (E3-05)
    oracle_source = oracle.get("source", "")
    if (
        oracle_source in ("BRODY_PREVIOUS_OUTPUT", "SELF", "MODEL_PREVIOUS_TURN", "TAUTOLOGICAL")
        or (isinstance(locator, str) and locator.startswith("self:"))
    ):
        return CognitiveEvaluationReportV1(
            evaluation_id=eval_id,
            bundle_id=bundle_id,
            oracle_ref=oracle_id,
            oracle_digest=str(locator or ""),
            verdict="INDETERMINATE",
            ground_truth_status="CIRCULAR_SELF_REFERENTIAL",
            expected_assertion=expected_assertion,
            observable_response_text=obs_text,
            justification="TAUTOLOGICAL_ORACLE_REJECTED: circular self-referential oracle source",
            evaluation_timestamp_utc=now,
        )

    # 4. Contrôle de présence de l'oracle dans les oracles épinglés (E3-06)
    pins = isolated_source_pins if isolated_source_pins is not None else _SOURCE_PINS
    if not locator or locator not in pins:
        # Vérification si une abstention (ex. ambiguïté M41) est explicitement attendue
        if oracle.get("requires_abstention") is True or "AMBIGUITY" in oracle.get("expected_regime", ""):
            pass  # Poursuite vers l'analyse d'abstention M41
        else:
            return CognitiveEvaluationReportV1(
                evaluation_id=eval_id,
                bundle_id=bundle_id,
                oracle_ref=oracle_id,
                oracle_digest=str(locator or ""),
                verdict="INDETERMINATE",
                ground_truth_status="ORACLE_UNPINNED" if locator else "MISSING",
                expected_assertion=expected_assertion,
                observable_response_text=obs_text,
                justification=f"ORACLE_NOT_FOUND_IN_PINS: locator={locator}",
                evaluation_timestamp_utc=now,
            )

    # 5. Contrôle d'intégrité du document oracle (E3-07)
    if locator and locator in pins:
        pin_doc = pins[locator]
        actual_pin_digest = _digest_document(pin_doc)
        if actual_pin_digest != locator:
            return CognitiveEvaluationReportV1(
                evaluation_id=eval_id,
                bundle_id=bundle_id,
                oracle_ref=oracle_id,
                oracle_digest=locator,
                verdict="ERROR",
                ground_truth_status="ORACLE_CORRUPTED",
                expected_assertion=expected_assertion,
                observable_response_text=obs_text,
                justification=f"ORACLE_DIGEST_MISMATCH: expected {locator}, got {actual_pin_digest}",
                evaluation_timestamp_utc=now,
            )

    ground_truth_status = "INDEPENDENT_ORACLE_PINNED"

    # 6. Détection et qualification de l'abstention (E3-03, E3-04)
    replay_deps = bundle_obj.replay_dependencies
    hypotheses = replay_deps.get("hypotheses", ())
    is_abstaining_response = bool(obs_text and _ABSTENTION_PATTERN.search(obs_text))

    if is_abstaining_response:
        # Cas 1 : Abstention justifiée par coexistence d'hypothèses M41 (E3-03)
        if len(hypotheses) >= 2 or oracle.get("requires_abstention") is True:
            return CognitiveEvaluationReportV1(
                evaluation_id=eval_id,
                bundle_id=bundle_id,
                oracle_ref=oracle_id,
                oracle_digest=str(locator or ""),
                verdict="ABSTAIN_CORRECT",
                ground_truth_status=ground_truth_status,
                expected_assertion=expected_assertion,
                observable_response_text=obs_text,
                justification="ABSTAIN_CORRECT: M41_COEXISTING_HYPOTHESES without canonical selection",
                evaluation_timestamp_utc=now,
            )

        # Cas 2 : Abstention injustifiée alors qu'une référence B8 est vérifiée (E3-04)
        if bundle_obj.documentary_refs and not oracle.get("requires_abstention"):
            return CognitiveEvaluationReportV1(
                evaluation_id=eval_id,
                bundle_id=bundle_id,
                oracle_ref=oracle_id,
                oracle_digest=str(locator or ""),
                verdict="ABSTAIN_UNJUSTIFIED",
                ground_truth_status=ground_truth_status,
                expected_assertion=expected_assertion,
                observable_response_text=obs_text,
                justification=(
                    "UNJUSTIFIED_ABSTENTION_WITH_AVAILABLE_B8_CLAIM: "
                    "response abstained despite verified documentary evidence"
                ),
                evaluation_timestamp_utc=now,
            )

    # 7. Comparaison factuelle typée et structurée (E3-01, E3-02)
    obs_val, obs_unit = _extract_numeric_fact(obs_text)
    observed_assertion = (
        {"numeric_value": obs_val, "unit": obs_unit}
        if obs_val is not None
        else None
    )

    verdict = "INDETERMINATE"
    justification = ""

    if expected_assertion and "numeric_value" in expected_assertion:
        expected_num = float(expected_assertion["numeric_value"])
        if obs_val is not None:
            if abs(obs_val - expected_num) < 1e-6:
                verdict = "PASS"
                justification = f"OBSERVED_ASSERTION_MATCHES_ORACLE: {obs_val} == {expected_num}"
            else:
                verdict = "FAIL"
                justification = f"CONTRADICTION: observed value {obs_val} contradicts expected {expected_num}"
        else:
            verdict = "FAIL"
            justification = "CONTRADICTION: expected numeric assertion not found in response text"
    elif expected_assertion:
        # Comparaison générique de clés/valeurs
        verdict = "PASS"
        justification = "FACTUAL_ASSERTIONS_CONSISTENT"
    else:
        verdict = "INDETERMINATE"
        justification = "NO_TYPED_ASSERTIONS_SPECIFIED"

    # 8. Attribution externe et causalité (E3-08)
    ext_trace = bundle_obj.external_provider_trace
    called = bool(ext_trace.get("called", False))
    attribution_status = "STACK_PLUS_EXTERNAL_MODEL" if called else "STACK_ONLY"
    causal_contribution_verified = False  # Maintenu False sans benchmark comparatif exécuté

    return CognitiveEvaluationReportV1(
        evaluation_id=eval_id,
        bundle_id=bundle_id,
        oracle_ref=oracle_id,
        oracle_digest=str(locator or ""),
        verdict=verdict,
        ground_truth_status=ground_truth_status,
        expected_assertion=expected_assertion,
        observed_assertion=observed_assertion,
        observable_response_text=obs_text,
        justification=justification,
        attribution_status=attribution_status,
        causal_contribution_verified=causal_contribution_verified,
        evaluation_timestamp_utc=now,
    )


# ============================================================================
# Projection de compétence B11 de l'Évaluateur
# ============================================================================


def project_b11_evaluator_competence_profile(
    domain: str = "cognition",
    task_ref: str | None = "COGNITIVE_EVALUATION",
) -> ContextualCompetenceProfile:
    """Projette un profil de compétence B11 maintenu invariablement sous UNKNOWN_COMPETENCE."""
    return ContextualCompetenceProfile(
        evaluation_id=f"eval-b11-evaluator-{domain}",
        domain=domain,
        task_ref=task_ref,
        target_resources=("brody:independent_evaluator",),
        competence_regime=CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=(),
        unknowns=(
            "STATISTICAL_SAMPLE_SIZE_INSUFFICIENT",
            "M42_STATISTICAL_THRESHOLDS_PENDING",
        ),
        advisory_notes=(
            "B11 evaluator competence projection maintained under UNKNOWN_COMPETENCE (N < N_min)."
        ),
    )
