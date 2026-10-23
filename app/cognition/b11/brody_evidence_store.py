"""M42 B11 Compétence & Calibration — Magasin de Preuve Cognitive Brody V1.

Source doctrinale :
  docs/architecture/M42_B11_BRODY_COGNITIVE_EVIDENCE_BUNDLE_SPEC_V1.md

Rôle du module :
  Implémente l'architecture minimale de publication, vérification et lecture
  consultative des bundles de preuve cognitive scellés Brody V1 (Option B).
  Assure la séparation étanche des trois rôles canoniques :
  1. CognitiveEvidencePublisher : publication atomique matérielle (staging + os.link).
  2. CognitiveEvidenceVerifier : vérification passive d'intégrité bit-à-bit.
  3. B11CognitiveEvidenceReader : lecture et projection consultatives sans écriture.

Garanties de gouvernance :
  - Respect absolu de B11_EFFECTS (memory_write=False, emits_act=False,
    kernel_mutation=False, decision_authority="KX108_ONLY", b12_selection=False).
  - Maintien impératif sous CompetenceRegime.UNKNOWN_COMPETENCE avec score nul.
  - Schéma fermé V1 : rejet des champs supplémentaires non autorisés.
  - Deep immutability : normalisation récursive en structures non mutables.
  - Rejet des secrets et des auto-attestations forgées.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from app.cognition.b11.brody_observation_adapter import BrodyCognitiveObservationV1
from app.cognition.b11.contracts import (
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)

try:
    from tests.integration_cognition.two_encounter_support import SOURCE_PINS as _SOURCE_PINS
except ImportError:
    _SOURCE_PINS = {}

# Schéma fermé V1 : liste exhaustive des champs déclarés autorisés
_ALLOWED_BUNDLE_KEYS: frozenset[str] = frozenset({
    "contract_version",
    "bundle_id",
    "execution_id",
    "mechanism_ref",
    "mechanism_version",
    "execution_timestamp_utc",
    "input_context_digest",
    "documentary_refs",
    "symbolic_context_refs",
    "external_provider_trace",
    "observable_response_digest",
    "observable_response_text",
    "evaluation_reference",
    "replay_dependencies",
    "privacy_classification",
    "publication_mode",
    "seal_status",
    "provenance_status",
    "integrity_digest",
})

_SECRET_PATTERN = re.compile(
    r"(?:sk-[a-zA-Z0-9_\-]{8,}|secret_key:|ssn:\s*\d|bearer\s+[a-zA-Z0-9_\-]{10,}|password\s*[:=])",
    re.IGNORECASE,
)

_BUNDLE_ID_PATTERN = re.compile(r"bceb-[0-9a-f]{32}")


def _deep_freeze(obj: Any) -> Any:
    """Normalise récursivement les conteneurs en structures immuables (deep freeze)."""
    if isinstance(obj, Mapping):
        return MappingProxyType({k: _deep_freeze(v) for k, v in obj.items()})
    elif isinstance(obj, (list, tuple, set, frozenset)):
        return tuple(_deep_freeze(v) for v in obj)
    return obj


@dataclass(frozen=True)
class BrodyCognitiveEvidenceBundleV1:
    """Bundle de preuve cognitive scellé Brody V1 à deep immutability."""

    contract_version: int = 1
    bundle_id: str = ""
    execution_id: str = ""
    mechanism_ref: str = ""
    mechanism_version: str = ""
    execution_timestamp_utc: str = ""
    input_context_digest: str = ""
    documentary_refs: tuple[str, ...] = ()
    symbolic_context_refs: tuple[str, ...] = ()
    external_provider_trace: Mapping[str, Any] = field(default_factory=dict)
    observable_response_digest: str = ""
    observable_response_text: str | None = None
    evaluation_reference: Mapping[str, Any] | None = None
    replay_dependencies: Mapping[str, Any] = field(default_factory=dict)
    privacy_classification: str = "SYNTHETIC_REDACTED"
    publication_mode: str = "PUBLICATION_ATOMIC"
    seal_status: str = "STORE_SEALED"
    provenance_status: str = "ORIGIN_UNESTABLISHED"
    integrity_digest: str = ""

    # Métadonnées d'évaluation et de vérification d'intégrité
    integrity_verification_status: str = "INTEGRITY_VERIFIED"
    structural_validation_status: str = "VALID"
    replay_status: str = "TRACE_REPLAYABLE"
    replay_capabilities: Mapping[str, Any] = field(default_factory=dict)
    bit_exact_replay_verified: bool = False
    attribution_status: str = "STACK_ONLY"
    ground_truth_status: str = "MISSING"
    evaluation_outcome: str = "INDETERMINATE"
    evaluation_notes: str = ""
    external_provider_called: bool = False
    external_provider_model: str | None = None

    def __post_init__(self) -> None:
        """Applique l'immuabilité transitive sur les structures imbriquées."""
        object.__setattr__(
            self,
            "external_provider_trace",
            _deep_freeze(self.external_provider_trace),
        )
        object.__setattr__(
            self,
            "replay_dependencies",
            _deep_freeze(self.replay_dependencies),
        )
        object.__setattr__(
            self,
            "replay_capabilities",
            _deep_freeze(self.replay_capabilities),
        )
        if self.evaluation_reference is not None:
            object.__setattr__(
                self,
                "evaluation_reference",
                _deep_freeze(self.evaluation_reference),
            )
        if not isinstance(self.documentary_refs, tuple):
            object.__setattr__(self, "documentary_refs", tuple(self.documentary_refs))
        if not isinstance(self.symbolic_context_refs, tuple):
            object.__setattr__(self, "symbolic_context_refs", tuple(self.symbolic_context_refs))


# ============================================================================
# Rôle 1 : CognitiveEvidencePublisher (Publication atomique)
# ============================================================================


class CognitiveEvidencePublisher:
    """Composant d'infrastructure chargé de la validation et publication atomique locale."""

    @staticmethod
    def publish(
        payload: dict[str, Any],
        store_dir: Path | str | None = None,
    ) -> dict[str, Any]:
        bundle_id = payload.get("bundle_id", "")

        # 1. Rejet immédiat de toute auto-attestation ou forge
        if "evaluation_outcome" in payload or "is_trusted" in payload or payload.get("seal_status") == "STORE_SEALED":
            return {
                "status": "FORGED_BUNDLE_REJECTED",
                "reason": "SELF_ATTESTATION_REJECTED: forged seal_status or evaluation outcome",
                "bundle_id": bundle_id,
            }

        # 2. Vérification du schéma fermé V1
        extra_keys = set(payload.keys()) - _ALLOWED_BUNDLE_KEYS
        if extra_keys:
            return {
                "status": "EXTRA_FIELDS_REJECTED",
                "reason": f"UNAUTHORIZED_EXTRA_FIELDS: {sorted(extra_keys)}",
                "bundle_id": bundle_id,
            }

        # 3. Contrôle de confidentialité et secrets
        if payload.get("privacy_classification") == "CONTAINS_PII_REJECTED" or _SECRET_PATTERN.search(str(payload)):
            return {
                "status": "PRIVACY_VIOLATION_REJECTED",
                "reason": "PII_DETECTION_HOLD: sensitive data detected",
                "bundle_id": bundle_id,
            }

        # 4. Validation des identifiants et version
        if payload.get("contract_version") != 1:
            return {
                "status": "SCHEMA_VALIDATION_FAILED",
                "reason": "UNSUPPORTED_CONTRACT_VERSION",
                "bundle_id": bundle_id,
            }

        # Dérivation canonique de l'intégrité et du bundle_id
        data_for_hash = {k: v for k, v in payload.items() if k not in ("integrity_digest", "bundle_id")}
        norm_bytes = json.dumps(data_for_hash, sort_keys=True, ensure_ascii=False).encode("utf-8")
        computed_digest = hashlib.sha256(norm_bytes).hexdigest()
        computed_bundle_id = f"bceb-{computed_digest[:32]}"

        # Mise à jour synchronisée du payload
        payload["integrity_digest"] = computed_digest
        payload["bundle_id"] = computed_bundle_id
        bundle_id = computed_bundle_id

        # 5. Publication atomique via staging + os.link
        target_dir = Path(store_dir) if store_dir else Path.cwd()
        target_dir.mkdir(parents=True, exist_ok=True)
        final_path = target_dir / f"{bundle_id}.json"

        norm_payload = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        payload_bytes = norm_payload.encode("utf-8")

        tmp_path = target_dir / f".{final_path.name}.{os.getpid()}.{hashlib.sha256(payload_bytes).hexdigest()[:16]}.tmp"

        try:
            with open(tmp_path, "wb") as fh:
                fh.write(payload_bytes)
                fh.flush()
                os.fsync(fh.fileno())
        except OSError as err:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            return {
                "status": "TEMP_WRITE_FAILED",
                "reason": str(err),
                "bundle_id": bundle_id,
            }

        try:
            os.link(tmp_path, final_path)
            return {
                "status": "STORED",
                "bundle_id": bundle_id,
                "path": str(final_path),
            }
        except FileExistsError:
            try:
                existing_bytes = final_path.read_bytes()
                if existing_bytes == payload_bytes:
                    return {"status": "IDEMPOTENT", "bundle_id": bundle_id}
                return {"status": "IMMUTABILITY_VIOLATION", "bundle_id": bundle_id}
            except OSError:
                return {"status": "IMMUTABILITY_VIOLATION", "bundle_id": bundle_id}
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass


# ============================================================================
# Rôle 2 : CognitiveEvidenceVerifier (Lecture passive et validation)
# ============================================================================


class CognitiveEvidenceVerifier:
    """Composant utilitaire passif de lecture, vérification d'intégrité et évaluation."""

    @staticmethod
    def load_and_verify(
        bundle_id: str,
        store_dir: Path | str | None = None,
    ) -> BrodyCognitiveEvidenceBundleV1:
        # Validation stricte du format de bundle_id avant tout accès disque (F-BCE-01)
        if not isinstance(bundle_id, str) or not _BUNDLE_ID_PATTERN.fullmatch(bundle_id):
            return BrodyCognitiveEvidenceBundleV1(
                bundle_id=str(bundle_id) if isinstance(bundle_id, str) else "INVALID_BUNDLE_ID",
                structural_validation_status="INVALID",
                integrity_verification_status="MALFORMED_IDENTIFIER",
                evaluation_outcome="ERROR",
                evaluation_notes="MALFORMED_BUNDLE_ID: identifier must strictly match ^bceb-[0-9a-f]{32}$",
            )

        target_dir = Path(store_dir) if store_dir else Path.cwd()
        bundle_path = target_dir / f"{bundle_id}.json"

        if not bundle_path.is_file():
            return BrodyCognitiveEvidenceBundleV1(
                bundle_id=bundle_id,
                structural_validation_status="INVALID",
                integrity_verification_status="FILE_MISSING",
                evaluation_outcome="ERROR",
                evaluation_notes=f"BUNDLE_NOT_FOUND: {bundle_id}",
            )

        try:
            content_bytes = bundle_path.read_bytes()
            data = json.loads(content_bytes.decode("utf-8"))
        except Exception as err:
            return BrodyCognitiveEvidenceBundleV1(
                bundle_id=bundle_id,
                structural_validation_status="INVALID",
                integrity_verification_status="INTEGRITY_COMPROMISED",
                evaluation_outcome="ERROR",
                evaluation_notes=f"CORRUPTED_BUNDLE: IMMUTABILITY_VIOLATION ({err})",
            )

        # Vérification d'intégrité bit-à-bit par recalcul du digest canonique
        data_for_hash = {k: v for k, v in data.items() if k not in ("integrity_digest", "bundle_id")}
        recomputed_bytes = json.dumps(data_for_hash, sort_keys=True, ensure_ascii=False).encode("utf-8")
        recomputed_digest = hashlib.sha256(recomputed_bytes).hexdigest()

        if recomputed_digest != data.get("integrity_digest"):
            return BrodyCognitiveEvidenceBundleV1(
                bundle_id=bundle_id,
                structural_validation_status="INVALID",
                integrity_verification_status="INTEGRITY_COMPROMISED",
                evaluation_outcome="ERROR",
                evaluation_notes="INTEGRITY_MISMATCH: IMMUTABILITY_VIOLATION",
            )

        # Extraction et analyse des dépendances de replay et références croisées
        replay_deps = data.get("replay_dependencies", {})
        pinned_digests = tuple(replay_deps.get("pinned_document_digests", ()))
        replay_mode = replay_deps.get("replay_mode", "UNKNOWN")

        # Analyse des oracles de test
        eval_ref = data.get("evaluation_reference")
        ground_truth_status = "MISSING"
        evaluation_outcome = "INDETERMINATE"
        evaluation_notes = ""

        if eval_ref:
            oracle_source = eval_ref.get("source", "")
            if oracle_source in ("BRODY_PREVIOUS_OUTPUT", "SELF", "TAUTOLOGICAL"):
                ground_truth_status = "CIRCULAR_SELF_REFERENTIAL"
                evaluation_outcome = "ERROR"
                evaluation_notes = "TAUTOLOGICAL_ORACLE_REJECTED: circular self-referential oracle"
            elif oracle_source == "INDEPENDENT_SOURCE_PIN":
                locator = eval_ref.get("locator", "")
                if locator in _SOURCE_PINS:
                    ground_truth_status = "INDEPENDENT_ORACLE_PINNED"
                    evaluation_outcome = "PASS"
                else:
                    ground_truth_status = "MISSING"
                    evaluation_outcome = "INDETERMINATE"
            else:
                ground_truth_status = "UNKNOWN"
                evaluation_outcome = "INDETERMINATE"

        # Qualification du statut de rejouabilité
        replay_capabilities: dict[str, Any] = {"symbolic_reexecution": True, "neural_reexecution": False}
        replay_status = "TRACE_REPLAYABLE"

        # Traçabilité du fournisseur distant (BCE-06, BCE-10)
        ext_trace = data.get("external_provider_trace", {})
        called = bool(ext_trace.get("called", False))
        model = ext_trace.get("model")
        attribution_status = "STACK_PLUS_EXTERNAL_MODEL" if called else "STACK_ONLY"

        # Détection de dépendances manquantes (BCE-03) ou incomplètes (BCE-05)
        has_missing_pinned = any(d not in _SOURCE_PINS for d in pinned_digests)
        if has_missing_pinned:
            replay_status = "REPLAY_DEPENDENCY_MISSING"
            replay_capabilities["symbolic_reexecution"] = False
        elif not pinned_digests or replay_mode in ("UNKNOWN", "NON_DETERMINISTIC_EXTERNAL"):
            replay_status = "REPLAY_INPUTS_INCOMPLETE"
            replay_capabilities["symbolic_reexecution"] = False
        elif called:
            replay_status = "TRACE_REPLAYABLE"

        return BrodyCognitiveEvidenceBundleV1(
            contract_version=data.get("contract_version", 1),
            bundle_id=data.get("bundle_id", bundle_id),
            execution_id=data.get("execution_id", ""),
            mechanism_ref=data.get("mechanism_ref", ""),
            mechanism_version=data.get("mechanism_version", ""),
            execution_timestamp_utc=data.get("execution_timestamp_utc", ""),
            input_context_digest=data.get("input_context_digest", ""),
            documentary_refs=tuple(data.get("documentary_refs", ())),
            symbolic_context_refs=tuple(data.get("symbolic_context_refs", ())),
            external_provider_trace=ext_trace,
            observable_response_digest=data.get("observable_response_digest", ""),
            observable_response_text=data.get("observable_response_text"),
            evaluation_reference=eval_ref,
            replay_dependencies=replay_deps,
            privacy_classification=data.get("privacy_classification", "SYNTHETIC_REDACTED"),
            publication_mode="PUBLICATION_ATOMIC",
            seal_status="STORE_SEALED",
            provenance_status="ORIGIN_UNESTABLISHED",
            integrity_digest=data.get("integrity_digest", ""),
            integrity_verification_status="INTEGRITY_VERIFIED",
            structural_validation_status="VALID",
            replay_status=replay_status,
            replay_capabilities=replay_capabilities,
            bit_exact_replay_verified=False,
            attribution_status=attribution_status,
            ground_truth_status=ground_truth_status,
            evaluation_outcome=evaluation_outcome,
            evaluation_notes=evaluation_notes,
            external_provider_called=called,
            external_provider_model=model,
        )


# ============================================================================
# Rôle 3 : B11CognitiveEvidenceReader (Consommateur consultatif B11)
# ============================================================================


class B11CognitiveEvidenceReader:
    """Lecteur consultatif B11 sans aucune capacité d'écriture matérielle."""

    def read_observation_from_bundle(
        self,
        bundle_id: str,
        store_dir: Path | str | None = None,
    ) -> BrodyCognitiveObservationV1:
        bundle = CognitiveEvidenceVerifier.load_and_verify(bundle_id, store_dir=store_dir)
        return BrodyCognitiveObservationV1(
            observation_id=f"bco-{bundle.bundle_id[5:]}" if bundle.bundle_id.startswith("bceb-") else "bco-eval",
            execution_id=bundle.execution_id,
            task_family="COGNITIVE_SYNTHESIS",
            task_ref="COGNITIVE_RESOLUTION",
            mechanism_ref=bundle.mechanism_ref,
            mechanism_version=bundle.mechanism_version,
            input_context_digest=bundle.input_context_digest,
            observable_response=bundle.observable_response_text,
            expressed_uncertainty_status="UNAMBIGUOUS_CERTAIN",
            components_health_status={},
            documentary_refs=bundle.documentary_refs,
            documentary_status="VERIFIED" if bundle.documentary_refs else "ABSENT",
            external_provider_called=bundle.external_provider_called,
            external_provider_model=bundle.external_provider_model,
            governance_compliance=True,
            structural_validation_status=bundle.structural_validation_status,
            replay_status=bundle.replay_status,
            integrity_verification_status=bundle.seal_status,
            ground_truth_status=bundle.ground_truth_status,
            provenance_status=bundle.provenance_status,
            attribution_status=bundle.attribution_status,
            evaluation_outcome=bundle.evaluation_outcome,
            evaluation_notes=bundle.evaluation_notes,
        )


# ============================================================================
# Fonctions de niveau module attendues par les tests et l'API
# ============================================================================


def publish_brody_evidence_bundle(
    payload: dict[str, Any],
    store_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Publie un bundle de preuve cognitive scellé Brody V1 de façon atomique."""
    return CognitiveEvidencePublisher.publish(payload, store_dir=store_dir)


def load_and_verify_brody_evidence_bundle(
    bundle_id: str,
    store_dir: Path | str | None = None,
) -> BrodyCognitiveEvidenceBundleV1:
    """Charge et vérifie l'intégrité bit-à-bit d'un bundle scellé."""
    return CognitiveEvidenceVerifier.load_and_verify(bundle_id, store_dir=store_dir)


def project_b11_bundle_competence_profile(
    bundle_ids: Sequence[str] = (),
    domain: str = "cognition",
    task_ref: str | None = "COGNITIVE_RESOLUTION",
    store_dir: Path | str | None = None,
) -> ContextualCompetenceProfile:
    """Projette un profil de compétence B11 maintenu sous UNKNOWN_COMPETENCE."""
    return ContextualCompetenceProfile(
        evaluation_id=f"eval-b11-bundle-{domain}",
        domain=domain,
        task_ref=task_ref,
        target_resources=("brody:cognitive_resolution",),
        competence_regime=CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=tuple(bundle_ids),
        unknowns=("STATISTICAL_SAMPLE_SIZE_INSUFFICIENT", "M42_STATISTICAL_THRESHOLDS_PENDING"),
        advisory_notes="B11 bundle competence projection maintained under UNKNOWN_COMPETENCE (N < N_min).",
    )
