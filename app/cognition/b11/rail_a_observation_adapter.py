"""M42 B11 Compétence & Calibration — Adaptateur d'Observations Vérifiées Rail A (`tooling_build`) V1.

Source de vérité :
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_DOCTRINE_V1.md
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_SPEC_V1.md
  docs/architecture/M42_B11_FAIL_CLOSED_SPEC_V1.md
  docs/architecture/M42_B11_RAIL_A_VERIFIED_OBSERVATION_SPEC_V1.md

Frontière doctrinale et d'authenticité :
- Lecture seule stricte des stores contrôlés (`memory_write=False`, `emits_act=False`,
  `kernel_mutation=False`, `decision_authority="KX108_ONLY"`, `advisory_only=True`,
  `b12_selection=False`).
- Aucun payload auto-déclaré (`is_verified=True`) ni objet forgé en mémoire n'est accepté.
- Constructeurs verrouillés par jeton privé de module : seule la fonction
  `load_and_verify_rail_a_observation` peut instancier `RailAVerifiedObservation` au terme
  des 6 vérificateurs canoniques et des contrôles de liaison croisée.
- Aucune formule de score, aucun seuil N_min, aucune métrique de calibration, et aucun
  raccordement d'évaluateur promouvant `EVIDENCED_COMPETENCE` ou `EVIDENCED_INCOMPETENCE`
  ne sont activés dans cette tranche.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Sequence

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_execution_closure as CLO  # noqa: E402
import obsidia_kx108_decision_store as DS  # noqa: E402
import obsidia_pre_execution_context as PEC  # noqa: E402
import obsidia_sealed_evidence_v0 as SEV  # noqa: E402
import obsidia_test_contract as TC  # noqa: E402
from app.cognition.b11.contracts import B11_EFFECTS  # noqa: E402

_BUNDLE_VERIFIER_TOKEN = object()

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

RAIL_A_DOMAIN = "tooling_build"
RAIL_A_TASK_REF = "UPDATE_TARGET_FROM_SOURCE"
RAIL_A_EXECUTING_MECHANISM_REF = "rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE"

OUTCOME_PASS = "VERIFIED_TEST_CONTRACT_PASS"
OUTCOME_FAILURE = "VERIFIED_TEST_CONTRACT_FAILURE"
OUTCOME_HOLD_OR_BLOCK = "VERIFIED_GOVERNANCE_POST_HOLD_OR_BLOCK"


def _is_sha256_hex(val: Any) -> bool:
    return type(val) is str and bool(_SHA256_RE.match(val))


def _is_nonempty_str(val: Any) -> bool:
    return type(val) is str and bool(val.strip())


def _append_unique(target: list[str], code: str) -> None:
    if code not in target:
        target.append(code)


class RailAVerifiedObservation:
    """Observation d'exécution Rail A (`tooling_build`) immuable et vérifiée sur 6 artefacts.

    Ne peut être instanciée que par `load_and_verify_rail_a_observation` via `_BUNDLE_VERIFIER_TOKEN`.
    """

    __slots__ = (
        "_observation_id",
        "_domain",
        "_task_ref",
        "_executing_mechanism_ref",
        "_mutated_target_path",
        "_conditions",
        "_batch_execution_id",
        "_child_execution_id",
        "_execution_authority_hash",
        "_approval_id",
        "_test_contract_hash",
        "_target_pre_sha256",
        "_target_post_sha256",
        "_source_content_sha256",
        "_test_aggregate_status",
        "_required_check_count",
        "_passed_required_check_count",
        "_kx108_pre_gate",
        "_kx108_post_gate",
        "_verified_execution_outcome",
        "_pre_governance_integrity_confidence",
        "_is_predictive_outcome_probability",
        "_anchor_refs",
        "_provenance_store_verified",
        "_hash",
        "_initialized",
    )

    def __init__(
        self,
        *,
        _verifier_token: object = None,
        observation_id: str,
        domain: str,
        task_ref: str,
        executing_mechanism_ref: str,
        mutated_target_path: str,
        conditions: tuple[str, ...],
        batch_execution_id: str,
        child_execution_id: str,
        execution_authority_hash: str,
        approval_id: str,
        test_contract_hash: str,
        target_pre_sha256: str,
        target_post_sha256: str,
        source_content_sha256: str,
        test_aggregate_status: str,
        required_check_count: int,
        passed_required_check_count: int,
        kx108_pre_gate: str,
        kx108_post_gate: str,
        verified_execution_outcome: str,
        pre_governance_integrity_confidence: float,
        is_predictive_outcome_probability: bool,
        anchor_refs: tuple[str, ...],
        provenance_store_verified: bool,
    ) -> None:
        if _verifier_token is not _BUNDLE_VERIFIER_TOKEN:
            raise PermissionError(
                "FORGED_OBSERVATION_OBJECT_REJECTED: RailAVerifiedObservation cannot be "
                "instantiated directly; use load_and_verify_rail_a_observation"
            )
        if is_predictive_outcome_probability is not False:
            raise ValueError("M42_RAIL_A_INVALID_CONFIDENCE_FLAG: is_predictive_outcome_probability must be False")
        if provenance_store_verified is not True:
            raise ValueError("M42_RAIL_A_UNVERIFIED_PROVENANCE: provenance_store_verified must be True")

        super().__setattr__("_observation_id", observation_id)
        super().__setattr__("_domain", domain)
        super().__setattr__("_task_ref", task_ref)
        super().__setattr__("_executing_mechanism_ref", executing_mechanism_ref)
        super().__setattr__("_mutated_target_path", mutated_target_path)
        super().__setattr__("_conditions", tuple(conditions))
        super().__setattr__("_batch_execution_id", batch_execution_id)
        super().__setattr__("_child_execution_id", child_execution_id)
        super().__setattr__("_execution_authority_hash", execution_authority_hash)
        super().__setattr__("_approval_id", approval_id)
        super().__setattr__("_test_contract_hash", test_contract_hash)
        super().__setattr__("_target_pre_sha256", target_pre_sha256)
        super().__setattr__("_target_post_sha256", target_post_sha256)
        super().__setattr__("_source_content_sha256", source_content_sha256)
        super().__setattr__("_test_aggregate_status", test_aggregate_status)
        super().__setattr__("_required_check_count", int(required_check_count))
        super().__setattr__("_passed_required_check_count", int(passed_required_check_count))
        super().__setattr__("_kx108_pre_gate", kx108_pre_gate)
        super().__setattr__("_kx108_post_gate", kx108_post_gate)
        super().__setattr__("_verified_execution_outcome", verified_execution_outcome)
        super().__setattr__("_pre_governance_integrity_confidence", float(pre_governance_integrity_confidence))
        super().__setattr__("_is_predictive_outcome_probability", False)
        super().__setattr__("_anchor_refs", tuple(anchor_refs))
        super().__setattr__("_provenance_store_verified", True)
        super().__setattr__(
            "_hash",
            hash((
                self._observation_id,
                self._domain,
                self._task_ref,
                self._executing_mechanism_ref,
                self._mutated_target_path,
                self._conditions,
                self._batch_execution_id,
                self._child_execution_id,
                self._execution_authority_hash,
                self._approval_id,
                self._test_contract_hash,
                self._target_pre_sha256,
                self._target_post_sha256,
                self._source_content_sha256,
                self._test_aggregate_status,
                self._required_check_count,
                self._passed_required_check_count,
                self._kx108_pre_gate,
                self._kx108_post_gate,
                self._verified_execution_outcome,
                self._pre_governance_integrity_confidence,
                self._is_predictive_outcome_probability,
                self._anchor_refs,
                self._provenance_store_verified,
            )),
        )
        super().__setattr__("_initialized", True)

    @property
    def observation_id(self) -> str:
        return self._observation_id

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def task_ref(self) -> str:
        return self._task_ref

    @property
    def executing_mechanism_ref(self) -> str:
        return self._executing_mechanism_ref

    @property
    def mutated_target_path(self) -> str:
        return self._mutated_target_path

    @property
    def conditions(self) -> tuple[str, ...]:
        return self._conditions

    @property
    def batch_execution_id(self) -> str:
        return self._batch_execution_id

    @property
    def child_execution_id(self) -> str:
        return self._child_execution_id

    @property
    def execution_authority_hash(self) -> str:
        return self._execution_authority_hash

    @property
    def approval_id(self) -> str:
        return self._approval_id

    @property
    def test_contract_hash(self) -> str:
        return self._test_contract_hash

    @property
    def target_pre_sha256(self) -> str:
        return self._target_pre_sha256

    @property
    def target_post_sha256(self) -> str:
        return self._target_post_sha256

    @property
    def source_content_sha256(self) -> str:
        return self._source_content_sha256

    @property
    def test_aggregate_status(self) -> str:
        return self._test_aggregate_status

    @property
    def required_check_count(self) -> int:
        return self._required_check_count

    @property
    def passed_required_check_count(self) -> int:
        return self._passed_required_check_count

    @property
    def kx108_pre_gate(self) -> str:
        return self._kx108_pre_gate

    @property
    def kx108_post_gate(self) -> str:
        return self._kx108_post_gate

    @property
    def verified_execution_outcome(self) -> str:
        return self._verified_execution_outcome

    @property
    def pre_governance_integrity_confidence(self) -> float:
        return self._pre_governance_integrity_confidence

    @property
    def is_predictive_outcome_probability(self) -> bool:
        return self._is_predictive_outcome_probability

    @property
    def anchor_refs(self) -> tuple[str, ...]:
        return self._anchor_refs

    @property
    def provenance_store_verified(self) -> bool:
        return self._provenance_store_verified

    def __setattr__(self, key: str, value: Any) -> None:
        if getattr(self, "_initialized", False):
            raise AttributeError("RailAVerifiedObservation is immutable")
        super().__setattr__(key, value)

    def __delattr__(self, key: str) -> None:
        raise AttributeError("RailAVerifiedObservation is immutable")

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RailAVerifiedObservation):
            return False
        return (
            self._observation_id == other._observation_id
            and self._execution_authority_hash == other._execution_authority_hash
            and self._child_execution_id == other._child_execution_id
            and self._anchor_refs == other._anchor_refs
            and self._verified_execution_outcome == other._verified_execution_outcome
        )


class RailABundleVerificationResult:
    """Résultat immuable de la vérification d'un bundle d'exécution Rail A."""

    __slots__ = (
        "_verified",
        "_observation",
        "_rejection_code",
        "_evidence_refs",
        "_unknowns",
        "_risk_indicators",
        "_initialized",
    )

    def __init__(
        self,
        *,
        _verifier_token: object = None,
        verified: bool,
        observation: RailAVerifiedObservation | None,
        rejection_code: str | None,
        evidence_refs: tuple[str, ...] = (),
        unknowns: tuple[str, ...] = (),
        risk_indicators: tuple[str, ...] = (),
    ) -> None:
        if _verifier_token is not _BUNDLE_VERIFIER_TOKEN:
            raise PermissionError(
                "FORGED_VERIFICATION_RESULT_REJECTED: RailABundleVerificationResult cannot be "
                "instantiated directly; use load_and_verify_rail_a_observation"
            )
        super().__setattr__("_verified", bool(verified))
        super().__setattr__("_observation", observation)
        super().__setattr__("_rejection_code", rejection_code)
        super().__setattr__("_evidence_refs", tuple(evidence_refs))
        super().__setattr__("_unknowns", tuple(unknowns))
        super().__setattr__("_risk_indicators", tuple(risk_indicators))
        super().__setattr__("_initialized", True)

    @property
    def verified(self) -> bool:
        return self._verified

    @property
    def observation(self) -> RailAVerifiedObservation | None:
        return self._observation

    @property
    def rejection_code(self) -> str | None:
        return self._rejection_code

    @property
    def evidence_refs(self) -> tuple[str, ...]:
        return self._evidence_refs

    @property
    def unknowns(self) -> tuple[str, ...]:
        return self._unknowns

    @property
    def risk_indicators(self) -> tuple[str, ...]:
        return self._risk_indicators

    def __setattr__(self, key: str, value: Any) -> None:
        if getattr(self, "_initialized", False):
            raise AttributeError("RailABundleVerificationResult is immutable")
        super().__setattr__(key, value)

    def __delattr__(self, key: str) -> None:
        raise AttributeError("RailABundleVerificationResult is immutable")


def _reject(
    rejection_code: str,
    *,
    evidence_refs: Sequence[str] = (),
    unknowns: Sequence[str] = ("RAIL_A_BUNDLE_UNVERIFIED",),
    extra_risks: Sequence[str] = (),
) -> RailABundleVerificationResult:
    risks: list[str] = [rejection_code]
    for r in extra_risks:
        _append_unique(risks, r)
    return RailABundleVerificationResult(
        _verifier_token=_BUNDLE_VERIFIER_TOKEN,
        verified=False,
        observation=None,
        rejection_code=rejection_code,
        evidence_refs=tuple(evidence_refs),
        unknowns=tuple(unknowns),
        risk_indicators=tuple(risks),
    )


def load_and_verify_rail_a_observation(
    kxpost_decision_record_id: Any,
    *,
    kx108_decision_dir: Path,
    pre_execution_context_dir: Path,
    sealed_receipt_dir: Path,
    sealed_rollback_evidence_dir: Path,
    test_contract_results_dir: Path,
    closure_id: str | None = None,
    execution_closures_dir: Path | None = None,
) -> RailABundleVerificationResult:
    """Charge en lecture seule et vérifie intégralement un bundle C2/D1 à 6 artefacts du Rail A."""
    # 1. Contrôle passif strict de l'identifiant d'entrée (interdiction des dicts/objets auto-déclarés)
    if type(kxpost_decision_record_id) is dict:
        is_ver = dict.get(kxpost_decision_record_id, "is_verified")
        is_auth = dict.get(kxpost_decision_record_id, "is_authenticated")
        if is_ver is True or is_auth is True:
            return _reject(
                "SELF_ATTESTATION_REJECTED",
                extra_risks=("INVALID_RECORD_STRUCTURE_REJECTED",),
            )
        return _reject("INVALID_RECORD_STRUCTURE_REJECTED")

    if type(kxpost_decision_record_id) is not str:
        return _reject(
            "FORGED_OBSERVATION_OBJECT_REJECTED",
            extra_risks=("INVALID_RECORD_STRUCTURE_REJECTED",),
        )

    kxpost_id = kxpost_decision_record_id.strip()
    if not kxpost_id or not _ID_RE.match(kxpost_id):
        return _reject("INVALID_DECISION_RECORD_ID")

    if not kxpost_id.startswith("kxpost-"):
        return _reject("UNSUPPORTED_DECISION_PHASE_OR_LEGACY_RECORD")

    # Validation des répertoires de stores contrôlés
    for store_dir in (
        kx108_decision_dir,
        pre_execution_context_dir,
        sealed_receipt_dir,
        sealed_rollback_evidence_dir,
        test_contract_results_dir,
    ):
        if not isinstance(store_dir, Path) or not store_dir.is_dir():
            return _reject("INVALID_STORE_DIRECTORY")

    # 2. Chargement et vérification canonique de kxpost
    kxpost = DS.load_kx108_decision_record(kxpost_id, store_dir=kx108_decision_dir)
    if kxpost is None:
        return _reject("ARTIFACT_MISSING:kxpost")

    ok_post, err_post = DS.verify_kx108_decision_record(kxpost)
    if not ok_post:
        return _reject(f"ARTIFACT_VERIFICATION_FAILED:kxpost:{err_post}")

    if (
        kxpost.get("decision_phase") != DS.POST_DECISION_PHASE
        or kxpost.get("decision_record_id") != kxpost_id
        or not str(kxpost.get("decision_record_id", "")).startswith("kxpost-")
    ):
        return _reject("UNSUPPORTED_DECISION_PHASE_OR_LEGACY_RECORD")

    kxpre_id = kxpost.get("kx108_pre_decision_record_id")
    sar_id = kxpost.get("sealed_apply_receipt_id")
    sre_id = kxpost.get("sealed_rollback_evidence_id")
    tcr_id = kxpost.get("test_result_id")

    if not _is_nonempty_str(kxpre_id):
        return _reject("UNSUPPORTED_DECISION_PHASE_OR_LEGACY_RECORD")
    if not _is_nonempty_str(sre_id):
        return _reject("ARTIFACT_MISSING:sre")
    if not _is_nonempty_str(sar_id):
        return _reject("ARTIFACT_MISSING:sar")
    if not _is_nonempty_str(tcr_id):
        return _reject("ARTIFACT_MISSING:tcr")

    # 3. Chargement et vérification canonique de kxpre, pec, sre, sar, tcr
    kxpre = DS.load_kx108_decision_record(kxpre_id, store_dir=kx108_decision_dir)
    if kxpre is None:
        return _reject("ARTIFACT_MISSING:kxpre")
    ok_pre, err_pre = DS.verify_kx108_decision_record(kxpre)
    if not ok_pre:
        return _reject(f"ARTIFACT_VERIFICATION_FAILED:kxpre:{err_pre}")

    pec_id = kxpre.get("pre_execution_context_id")
    if not _is_nonempty_str(pec_id):
        return _reject("ARTIFACT_MISSING:pec")
    pec = PEC.load_pre_execution_context_record(pec_id, store_dir=pre_execution_context_dir)
    if pec is None:
        return _reject("ARTIFACT_MISSING:pec")
    ok_pec, err_pec = PEC.verify_pre_execution_context_record(pec)
    if not ok_pec:
        return _reject(f"ARTIFACT_VERIFICATION_FAILED:pec:{err_pec}")

    sre = SEV.load_sealed_rollback_evidence(sre_id, store_dir=sealed_rollback_evidence_dir)
    if sre is None:
        return _reject("ARTIFACT_MISSING:sre")
    ok_sre, err_sre = SEV.verify_sealed_rollback_evidence(sre)
    if not ok_sre:
        return _reject(f"ARTIFACT_VERIFICATION_FAILED:sre:{err_sre}")

    sar = SEV.load_sealed_apply_receipt(sar_id, store_dir=sealed_receipt_dir)
    if sar is None:
        return _reject("ARTIFACT_MISSING:sar")
    ok_sar, err_sar = SEV.verify_sealed_apply_receipt(sar)
    if not ok_sar:
        return _reject(f"ARTIFACT_VERIFICATION_FAILED:sar:{err_sar}")

    tcr = TC.load_test_contract_result(tcr_id, results_dir=test_contract_results_dir)
    if tcr is None:
        return _reject("ARTIFACT_MISSING:tcr")
    ok_tcr, err_tcr = TC.verify_test_contract_result_artifact(tcr)
    if not ok_tcr:
        return _reject(f"ARTIFACT_VERIFICATION_FAILED:tcr:{err_tcr}")

    # 3b. Vérification optionnelle de l'enregistrement de clôture (clo-*), sans jamais utiliser clo.functional_status
    if closure_id is not None:
        if (
            not _is_nonempty_str(closure_id)
            or not isinstance(execution_closures_dir, Path)
            or not execution_closures_dir.is_dir()
        ):
            return _reject("ARTIFACT_MISSING:clo")
        clo = CLO.load_execution_closure_record(closure_id.strip(), store_dir=execution_closures_dir)
        if clo is None:
            return _reject("ARTIFACT_MISSING:clo")
        ok_clo, err_clo = CLO.verify_execution_closure_record(clo)
        if not ok_clo:
            return _reject(f"ARTIFACT_VERIFICATION_FAILED:clo:{err_clo}")
        if (
            clo.get("kx108_decision_record_id") != kxpost["decision_record_id"]
            or clo.get("kx108_decision_record_hash") != kxpost["decision_record_hash"]
            or clo.get("execution_authority_hash") != kxpost["execution_authority_hash"]
            or clo.get("test_result_id") != tcr["result_id"]
            or clo.get("test_result_record_hash") != tcr["result_record_hash"]
        ):
            return _reject("CROSS_LINK_MISMATCH:closure_binding")

    # 4. Contrôles de phases, domaine et autorité (Spec §4.1)
    if (
        kxpre.get("decision_phase") != DS.PRE_DECISION_PHASE
        or not str(kxpre.get("decision_record_id", "")).startswith("kxpre-")
    ):
        return _reject("UNSUPPORTED_DECISION_PHASE_OR_LEGACY_RECORD")

    if kxpre.get("domain") != RAIL_A_DOMAIN or kxpost.get("domain") != RAIL_A_DOMAIN:
        return _reject("CROSS_LINK_MISMATCH:domain")

    if kxpre.get("x108_gate") != "ALLOW":
        return _reject("CROSS_LINK_MISMATCH:kxpre_gate_not_allow")

    if kxpost.get("x108_gate") not in DS.VALID_X108_GATES:
        return _reject("CROSS_LINK_MISMATCH:kxpost_gate_invalid")

    if tcr.get("decision_authority") != "KX108_ONLY":
        return _reject("CROSS_LINK_MISMATCH:tcr_decision_authority")

    # 5. Identité d'exécution uniforme sur (kxpre, sre, sar, tcr, kxpost) (Spec §4.2)
    exec_artifacts = (kxpre, sre, sar, tcr, kxpost)
    batch_execution_id = kxpost.get("batch_execution_id")
    child_execution_id = kxpost.get("child_execution_id")
    execution_authority_hash = kxpost.get("execution_authority_hash")
    approval_id = kxpost.get("approval_id")

    if not _is_nonempty_str(batch_execution_id) or any(
        a.get("batch_execution_id") != batch_execution_id for a in exec_artifacts
    ):
        return _reject("CROSS_LINK_MISMATCH:batch_execution_id")

    if not _is_nonempty_str(child_execution_id) or any(
        a.get("child_execution_id") != child_execution_id for a in exec_artifacts
    ):
        return _reject("CROSS_LINK_MISMATCH:child_execution_id")

    if not _is_sha256_hex(execution_authority_hash) or any(
        a.get("execution_authority_hash") != execution_authority_hash for a in exec_artifacts
    ):
        return _reject("CROSS_LINK_MISMATCH:execution_authority_hash")

    if not _is_nonempty_str(approval_id) or any(
        a.get("approval_id") != approval_id for a in exec_artifacts
    ):
        return _reject("CROSS_LINK_MISMATCH:approval_id")

    # 6. Continuité cryptographique des paires (id, hash 64-hex) (Spec §4.3)
    pec_hash = pec.get("context_record_hash")
    kxpre_hash = kxpre.get("decision_record_hash")
    sre_hash = sre.get("sealed_rollback_evidence_hash")
    sar_hash = sar.get("sealed_apply_receipt_hash")
    tcr_hash = tcr.get("result_record_hash")
    kxpost_hash = kxpost.get("decision_record_hash")

    if not all(_is_sha256_hex(h) for h in (pec_hash, kxpre_hash, sre_hash, sar_hash, tcr_hash, kxpost_hash)):
        return _reject("CROSS_LINK_MISMATCH:non_64hex_record_hash")

    if (
        kxpre.get("pre_execution_context_id") != pec.get("context_id")
        or kxpre.get("pre_execution_context_record_hash") != pec_hash
    ):
        return _reject("CROSS_LINK_MISMATCH:kxpre_to_pec")

    if (
        sre.get("kx108_pre_decision_record_id") != kxpre_id
        or sre.get("kx108_pre_decision_record_hash") != kxpre_hash
    ):
        return _reject("CROSS_LINK_MISMATCH:sre_to_kxpre")

    if (
        sar.get("kx108_pre_decision_record_id") != kxpre_id
        or sar.get("kx108_pre_decision_record_hash") != kxpre_hash
    ):
        return _reject("CROSS_LINK_MISMATCH:sar_to_kxpre")

    if (
        sar.get("sealed_rollback_evidence_id") != sre_id
        or sar.get("sealed_rollback_evidence_hash") != sre_hash
    ):
        return _reject("CROSS_LINK_MISMATCH:sar_to_sre")

    if (
        kxpost.get("kx108_pre_decision_record_id") != kxpre_id
        or kxpost.get("kx108_pre_decision_record_hash") != kxpre_hash
    ):
        return _reject("CROSS_LINK_MISMATCH:kxpost_to_kxpre")

    if (
        kxpost.get("sealed_apply_receipt_id") != sar_id
        or kxpost.get("sealed_apply_receipt_hash") != sar_hash
    ):
        return _reject("CROSS_LINK_MISMATCH:kxpost_to_sar")

    if (
        kxpost.get("sealed_rollback_evidence_id") != sre_id
        or kxpost.get("sealed_rollback_evidence_hash") != sre_hash
    ):
        return _reject("CROSS_LINK_MISMATCH:kxpost_to_sre")

    if (
        kxpost.get("test_result_id") != tcr_id
        or kxpost.get("test_result_record_hash") != tcr_hash
    ):
        return _reject("CROSS_LINK_MISMATCH:kxpost_to_tcr")

    # 7. Continuité du contrat de test (test_contract_hash) (Spec §4.4)
    test_contract_hash = tcr.get("test_contract_hash")
    if (
        not _is_sha256_hex(test_contract_hash)
        or kxpre.get("test_contract_hash") != test_contract_hash
        or kxpost.get("test_contract_hash") != test_contract_hash
    ):
        return _reject("CROSS_LINK_MISMATCH:test_contract_hash")

    manifest = pec.get("manifest")
    if isinstance(manifest, dict) and manifest.get("test_contract_hash") is not None:
        if manifest.get("test_contract_hash") != test_contract_hash:
            return _reject("CROSS_LINK_MISMATCH:pec_manifest_test_contract_hash")

    # 8. Continuité physique de la cible, de la source et de l'isolation (Spec §4.5)
    target_path = pec.get("target_path")
    approved_scope = pec.get("approved_scope")
    if (
        not _is_nonempty_str(target_path)
        or sre.get("target_path") != target_path
        or sar.get("target_path") != target_path
        or not isinstance(approved_scope, list)
        or target_path not in approved_scope
    ):
        return _reject("CROSS_LINK_MISMATCH:target_path_or_scope")

    target_pre_sha256 = pec.get("target_pre_sha256")
    if (
        not _is_sha256_hex(target_pre_sha256)
        or sre.get("pre_write_sha256") != target_pre_sha256
        or sar.get("target_pre_sha256") != target_pre_sha256
    ):
        return _reject("CROSS_LINK_MISMATCH:target_pre_sha256")

    source_sha256 = pec.get("source_sha256")
    if (
        not _is_sha256_hex(source_sha256)
        or sre.get("source_content_sha256") != source_sha256
        or sar.get("source_content_sha256") != source_sha256
        or sar.get("target_post_sha256") != source_sha256
    ):
        return _reject("CROSS_LINK_MISMATCH:source_or_target_post_sha256")

    if (
        pec.get("worktree_isolated") is not True
        or pec.get("branch_isolated") is not True
        or pec.get("protected_scope_status") != "CLEAN"
    ):
        return _reject("CROSS_LINK_MISMATCH:isolation_or_protected_scope")

    # 9. Cohérence interne du TestContractResult (tcr) (Spec §4.6 / RA-06)
    checks = tcr.get("checks")
    check_count = tcr.get("check_count")
    req_check_count = tcr.get("required_check_count")
    if (
        not isinstance(checks, list)
        or not checks
        or type(check_count) is not int
        or len(checks) != check_count
        or type(req_check_count) is not int
        or req_check_count < 1
    ):
        return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")

    required_checks: list[dict[str, Any]] = []
    for chk in checks:
        if type(chk) is not dict:
            return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")
        c_res = chk.get("result")
        if c_res not in (TC.RESULT_PASS, TC.RESULT_FAIL, TC.RESULT_ERROR):
            return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")

        if "expected_exit_code" in chk or "exit_code" in chk:
            if c_res == TC.RESULT_ERROR or "expected_exit_code" not in chk or "exit_code" not in chk:
                return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")
            if chk.get("expected_exit_code") is not None:
                if c_res == TC.RESULT_PASS and chk.get("exit_code") != chk.get("expected_exit_code"):
                    return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")
                if c_res == TC.RESULT_FAIL and chk.get("exit_code") == chk.get("expected_exit_code"):
                    return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")

        if "expected_target_sha256" in chk or "actual_target_sha256" in chk:
            if c_res == TC.RESULT_ERROR or "expected_target_sha256" not in chk or "actual_target_sha256" not in chk:
                return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")
            exp_sha = chk.get("expected_target_sha256")
            act_sha = chk.get("actual_target_sha256")
            if c_res == TC.RESULT_PASS and (act_sha != exp_sha or act_sha != sar["target_post_sha256"]):
                return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")
            if c_res == TC.RESULT_FAIL and act_sha == exp_sha:
                return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")

        if "expected_diff_paths" in chk or "actual_diff_paths" in chk:
            if c_res == TC.RESULT_ERROR or "expected_diff_paths" not in chk or "actual_diff_paths" not in chk:
                return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")
            exp_diff = chk.get("expected_diff_paths")
            act_diff = chk.get("actual_diff_paths")
            if (
                not isinstance(exp_diff, list)
                or not isinstance(act_diff, list)
                or not all(_is_nonempty_str(p) for p in exp_diff)
                or not all(_is_nonempty_str(p) for p in act_diff)
                or exp_diff != sorted(exp_diff)
                or act_diff != sorted(act_diff)
            ):
                return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")
            if c_res == TC.RESULT_PASS and act_diff != exp_diff:
                return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")
            if c_res == TC.RESULT_FAIL and act_diff == exp_diff:
                return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")

        req_flag = chk.get("required", True)
        if type(req_flag) is not bool:
            return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")
        if req_flag is True:
            required_checks.append(chk)

    if len(required_checks) != req_check_count:
        return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")

    if any(c.get("result") == TC.RESULT_ERROR for c in required_checks):
        recomputed_aggregate = TC.AGGREGATE_TEST_EXECUTION_ERROR
    elif any(c.get("result") != TC.RESULT_PASS for c in required_checks):
        recomputed_aggregate = TC.AGGREGATE_REQUIRED_TEST_FAILED
    else:
        recomputed_aggregate = TC.AGGREGATE_ALL_REQUIRED_PASS

    if tcr.get("aggregate_status") != recomputed_aggregate:
        return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")

    kx108_post_gate = kxpost["x108_gate"]
    if recomputed_aggregate != TC.AGGREGATE_ALL_REQUIRED_PASS and kx108_post_gate == "ALLOW":
        return _reject("TEST_RESULT_INTERNAL_INCONSISTENCY")

    # 10. Qualification sémantique de l'observation vérifiée (Spec §5 & §6.1)
    passed_required_count = sum(1 for c in required_checks if c.get("result") == TC.RESULT_PASS)

    if recomputed_aggregate == TC.AGGREGATE_ALL_REQUIRED_PASS and kx108_post_gate == "ALLOW":
        verified_outcome = OUTCOME_PASS
    elif recomputed_aggregate in (TC.AGGREGATE_REQUIRED_TEST_FAILED, TC.AGGREGATE_TEST_EXECUTION_ERROR):
        verified_outcome = OUTCOME_FAILURE
    else:
        verified_outcome = OUTCOME_HOLD_OR_BLOCK

    pre_env = kxpre.get("canonical_envelope")
    raw_pre_conf = pre_env.get("confidence", 0.0) if isinstance(pre_env, dict) else 0.0
    if type(raw_pre_conf) is bool or not isinstance(raw_pre_conf, (int, float)):
        return _reject("CROSS_LINK_MISMATCH:invalid_pre_confidence")
    pre_conf = float(raw_pre_conf)
    if pre_conf < 0.0 or pre_conf > 1.0:
        return _reject("CROSS_LINK_MISMATCH:invalid_pre_confidence_range")

    anchor_refs = (
        f"pec:{pec['context_id']}:sha256:{pec_hash}",
        f"kxpre:{kxpre_id}:sha256:{kxpre_hash}",
        f"sre:{sre_id}:sha256:{sre_hash}",
        f"sar:{sar_id}:sha256:{sar_hash}",
        f"tcr:{tcr_id}:sha256:{tcr_hash}",
        f"kxpost:{kxpost_id}:sha256:{kxpost_hash}",
    )

    obs_digest = hashlib.sha256("|".join(anchor_refs).encode("utf-8")).hexdigest()[:32]
    observation_id = f"b11-railo-{obs_digest}"

    conditions = (
        "worktree_isolated:True",
        "branch_isolated:True",
        "protected_scope_status:CLEAN",
        f"source_kind:{sar.get('source_kind')}",
    )

    obs = RailAVerifiedObservation(
        _verifier_token=_BUNDLE_VERIFIER_TOKEN,
        observation_id=observation_id,
        domain=RAIL_A_DOMAIN,
        task_ref=RAIL_A_TASK_REF,
        executing_mechanism_ref=RAIL_A_EXECUTING_MECHANISM_REF,
        mutated_target_path=target_path,
        conditions=conditions,
        batch_execution_id=batch_execution_id,
        child_execution_id=child_execution_id,
        execution_authority_hash=execution_authority_hash,
        approval_id=approval_id,
        test_contract_hash=test_contract_hash,
        target_pre_sha256=target_pre_sha256,
        target_post_sha256=sar["target_post_sha256"],
        source_content_sha256=source_sha256,
        test_aggregate_status=recomputed_aggregate,
        required_check_count=req_check_count,
        passed_required_check_count=passed_required_count,
        kx108_pre_gate="ALLOW",
        kx108_post_gate=kx108_post_gate,
        verified_execution_outcome=verified_outcome,
        pre_governance_integrity_confidence=pre_conf,
        is_predictive_outcome_probability=False,
        anchor_refs=anchor_refs,
        provenance_store_verified=True,
    )

    return RailABundleVerificationResult(
        _verifier_token=_BUNDLE_VERIFIER_TOKEN,
        verified=True,
        observation=obs,
        rejection_code=None,
        evidence_refs=anchor_refs,
        unknowns=(),
        risk_indicators=(),
    )


def load_and_verify_rail_a_observations_batch(
    kxpost_decision_record_ids: Sequence[Any],
    *,
    kx108_decision_dir: Path,
    pre_execution_context_dir: Path,
    sealed_receipt_dir: Path,
    sealed_rollback_evidence_dir: Path,
    test_contract_results_dir: Path,
) -> tuple[tuple[RailAVerifiedObservation, ...], tuple[str, ...], tuple[str, ...]]:
    """Charge et vérifie un lot d'observations Rail A en rejetant tout doublon d'ID ou d'exécution."""
    if type(kxpost_decision_record_ids) not in (tuple, list):
        return (), ("INVALID_BATCH_CONTAINER",), ("INVALID_CONTAINER_STRUCTURE_REJECTED",)

    observations: list[RailAVerifiedObservation] = []
    unknowns: list[str] = []
    risk_indicators: list[str] = []

    seen_decision_ids: set[str] = set()
    seen_execution_identities: set[tuple[str, str]] = set()
    seen_child_execution_ids: set[str] = set()
    seen_receipt_refs: set[str] = set()

    for raw_id in kxpost_decision_record_ids:
        if type(raw_id) is str and raw_id.strip() in seen_decision_ids:
            _append_unique(risk_indicators, "DUPLICATE_EXECUTION_OBSERVATION_REJECTED")
            continue

        if type(raw_id) is str and raw_id.strip():
            seen_decision_ids.add(raw_id.strip())

        res = load_and_verify_rail_a_observation(
            raw_id,
            kx108_decision_dir=kx108_decision_dir,
            pre_execution_context_dir=pre_execution_context_dir,
            sealed_receipt_dir=sealed_receipt_dir,
            sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
            test_contract_results_dir=test_contract_results_dir,
        )
        if not res.verified or res.observation is None:
            for u in res.unknowns:
                _append_unique(unknowns, u)
            for r in res.risk_indicators:
                _append_unique(risk_indicators, r)
            continue

        obs = res.observation
        exec_identity = (obs.batch_execution_id, obs.child_execution_id)
        sar_ref = next((ref for ref in obs.anchor_refs if ref.startswith("sar:")), "")
        kxpost_ref = next((ref for ref in obs.anchor_refs if ref.startswith("kxpost:")), "")

        if (
            exec_identity in seen_execution_identities
            or obs.child_execution_id in seen_child_execution_ids
            or (sar_ref and sar_ref in seen_receipt_refs)
            or (kxpost_ref and kxpost_ref in seen_decision_ids)
        ):
            _append_unique(risk_indicators, "DUPLICATE_EXECUTION_OBSERVATION_REJECTED")
            continue

        seen_execution_identities.add(exec_identity)
        seen_child_execution_ids.add(obs.child_execution_id)
        if sar_ref:
            seen_receipt_refs.add(sar_ref)
        if kxpost_ref:
            seen_decision_ids.add(kxpost_ref)
        observations.append(obs)

    return tuple(observations), tuple(unknowns), tuple(risk_indicators)


__all__ = [
    "B11_EFFECTS",
    "OUTCOME_FAILURE",
    "OUTCOME_HOLD_OR_BLOCK",
    "OUTCOME_PASS",
    "RAIL_A_DOMAIN",
    "RAIL_A_EXECUTING_MECHANISM_REF",
    "RAIL_A_TASK_REF",
    "RailABundleVerificationResult",
    "RailAVerifiedObservation",
    "load_and_verify_rail_a_observation",
    "load_and_verify_rail_a_observations_batch",
]
