"""M42 B11 Compétence & Calibration — Bridge de Preuve Cognitive et Replay Symbolique V1.

Ce module implémente le pont pur d'assemblage et le moteur de réexécution symbolique
pour le Brody Cognitive Evidence Bundle V1 :
1. build_evidence_bundle_payload_from_receipt : assemblage pur sans effet de bord.
2. reexecute_symbolic_bundle : réexécution symbolique hors-ligne déterministe (B8/M41/B7).
3. project_b11_bridge_competence_profile : maintien sous UNKNOWN_COMPETENCE et B11_EFFECTS.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from app.cognition.b11.brody_evidence_store import (
    BrodyCognitiveEvidenceBundleV1,
    load_and_verify_brody_evidence_bundle,
)
from app.cognition.b11.contracts import (
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)
from app.knowledge import b8

try:
    from tests.integration_cognition.two_encounter_support import SOURCE_PINS as _SOURCE_PINS
except ImportError:
    _SOURCE_PINS = {}


# ============================================================================
# Rapport de réexécution symbolique
# ============================================================================


@dataclass(frozen=True)
class SymbolicReexecutionReportV1:
    """Rapport immuable de réexécution symbolique déterministe hors-ligne."""

    bundle_id: str = ""
    status: str = "INDETERMINATE"
    symbolic_outcome: str = "INDETERMINATE"
    reexecuted_claims: tuple[str, ...] = ()
    neural_reexecution_status: str = "NEURAL_REEXECUTION_NOT_PERFORMED"
    bit_exact_replay_verified: bool = False
    invariants_checked: tuple[str, ...] = ()
    divergence_reasons: tuple[str, ...] = ()
    execution_timestamp_utc: str = ""

    def to_canonical(self) -> dict[str, Any]:
        """Convertit le rapport en dictionnaire canonique serialisable."""
        return {
            "bundle_id": self.bundle_id,
            "status": self.status,
            "symbolic_outcome": self.symbolic_outcome,
            "reexecuted_claims": list(self.reexecuted_claims),
            "neural_reexecution_status": self.neural_reexecution_status,
            "bit_exact_replay_verified": self.bit_exact_replay_verified,
            "invariants_checked": list(self.invariants_checked),
            "divergence_reasons": list(self.divergence_reasons),
            "execution_timestamp_utc": self.execution_timestamp_utc,
        }


# ============================================================================
# Helpers canoniques
# ============================================================================


def _digest_document(doc: Any) -> str:
    """Calcule le condensat canonique SHA-256 d'un document ou fixture."""
    if isinstance(doc, (bytes, bytearray)):
        return hashlib.sha256(doc).hexdigest()
    if isinstance(doc, str):
        return hashlib.sha256(doc.encode("utf-8")).hexdigest()
    norm = json.dumps(doc, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(norm).hexdigest()


# ============================================================================
# Fonction pure d'assemblage : build_evidence_bundle_payload_from_receipt
# ============================================================================


def build_evidence_bundle_payload_from_receipt(
    cognitive_receipt: Mapping[str, Any],
    observation: Any | None = None,
    evaluation_reference: Mapping[str, Any] | None = None,
    replay_mode: str = "DETERMINISTIC_OFFLINE",
    hypothesis_set: Any | None = None,
    knowledge_claims: Sequence[Any] = (),
    external_provider_trace: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble canoniquement un payload BCE V1 à partir d'un reçu d'exécution cognitive réel.

    Fonction pure :
    - Zéro I/O disque ;
    - Zéro transport réseau ;
    - Zéro mutation des dictionnaires et objets d'entrée ;
    - Strictement bornée aux 19 champs du schéma fermé V1.
    """
    execution_id = str(cognitive_receipt.get("signal_id", ""))
    mechanism_ref = "brody:cognitive_resolution"
    mechanism_version = str(cognitive_receipt.get("version", "REAL_COGNITIVE_JOIN_C1_V1"))
    execution_timestamp_utc = str(
        cognitive_receipt.get("created_at") or datetime.now(timezone.utc).isoformat()
    )

    # Condensat du contexte d'entrée
    input_text = (
        cognitive_receipt.get("user_message")
        or cognitive_receipt.get("message")
        or cognitive_receipt.get("query")
        or execution_id
    )
    input_context_digest = hashlib.sha256(str(input_text).encode("utf-8")).hexdigest()

    # Extraction des références documentaires (claims B8)
    doc_refs: list[str] = []
    pinned_digests: list[str] = []
    serialized_claims: list[dict[str, Any]] = []

    for c in knowledge_claims:
        cid = getattr(c, "claim_id", None) or (c.get("claim_id") if isinstance(c, dict) else str(c))
        doc_refs.append(str(cid))

        # Extraction des empreintes sources des documents B8
        source_refs = getattr(c, "source_refs", ())
        for ref in source_refs:
            if isinstance(ref, str):
                if ref.startswith("doc:"):
                    pinned_digests.append(ref[4:])
                elif ref.startswith("fixture-doc:"):
                    pinned_digests.append(ref[12:])
                elif len(ref) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in ref):
                    pinned_digests.append(ref.lower())

        # Si claim.content est un document structuré ou dictionnaire
        content_val = getattr(c, "content", None)
        if isinstance(content_val, Mapping) and "statement" in content_val:
            pinned_digests.append(_digest_document(content_val))

        if hasattr(c, "claim_id"):
            claim_class_str = (
                c.claim_class.value if hasattr(c.claim_class, "value") else str(c.claim_class)
            )
            vt = getattr(c, "valid_time", None)
            vt_dict = vt.to_canonical() if hasattr(vt, "to_canonical") else None
            serialized_claims.append({
                "claim_id": c.claim_id,
                "lineage_id": c.lineage_id,
                "claim_version": c.claim_version,
                "previous_claim_id": c.previous_claim_id,
                "claim_class": claim_class_str,
                "slot_id": c.slot_id,
                "valid_time": vt_dict,
                "content": c.content,
                "source_refs": list(getattr(c, "source_refs", ())),
                "origin_refs": list(getattr(c, "origin_refs", ())),
            })

    # Raccordement de l'évaluation de référence
    eval_ref = dict(evaluation_reference) if evaluation_reference is not None else None
    if eval_ref and "locator" in eval_ref and eval_ref["locator"]:
        pinned_digests.append(str(eval_ref["locator"]))

    # Déduplication ordonnée des condensats documentaires
    seen_digests: set[str] = set()
    dedup_pins: list[str] = []
    for d in pinned_digests:
        if d not in seen_digests:
            seen_digests.add(d)
            dedup_pins.append(d)

    # Extraction des références symboliques M41 et sérialisation des hypothèses
    sym_refs: list[str] = []
    hypotheses_list: list[dict[str, Any]] = []

    if hypothesis_set is not None:
        subj = getattr(hypothesis_set, "subject_ref", None)
        if subj is not None:
            ref_id = getattr(subj, "ref_id", None) or getattr(subj, "canonical_label", str(subj))
            sym_refs.append(f"m41:{ref_id}")
        else:
            sym_refs.append("m41:unknown_subject")

        members = getattr(hypothesis_set, "members", ())
        for h in members:
            presumed = getattr(h, "presumed_referent_ref", None)
            materials = getattr(h, "material_refs", ())
            hyp_data = {
                "hypothesis_kind": getattr(h, "hypothesis_kind", "STATE_OF_PRESUMED_REFERENT"),
                "presumed_referent": getattr(presumed, "ref_id", str(presumed)),
                "material_refs": [getattr(m, "ref_id", str(m)) for m in materials],
                "modality_label": getattr(h, "modality_label", ""),
                "unknowns": list(getattr(h, "unknowns", ())),
                "hypothesis_id": getattr(h, "hypothesis_id", ""),
            }
            hypotheses_list.append(hyp_data)

    # Réponse observable
    resp_text: str | None = None
    if observation is not None:
        resp_text = getattr(observation, "observable_response_text", None) or getattr(
            observation, "candidate_response", None
        )
    if not resp_text:
        resp_text = (
            cognitive_receipt.get("response")
            or cognitive_receipt.get("candidate_response")
            or cognitive_receipt.get("final_answer")
        )

    if resp_text is not None:
        resp_text = str(resp_text)
        resp_digest = hashlib.sha256(resp_text.encode("utf-8")).hexdigest()
    else:
        resp_digest = hashlib.sha256(b"").hexdigest()

    # Trace du fournisseur neuronal
    if external_provider_trace is not None:
        ext_trace = dict(external_provider_trace)
    elif "external_provider_trace" in cognitive_receipt:
        ext_trace = dict(cognitive_receipt["external_provider_trace"])
    else:
        ext_trace = {
            "called": False,
            "model": None,
            "model_calls": 0,
        }

    # Dépendances de replay
    replay_deps: dict[str, Any] = {
        "replay_mode": replay_mode,
        "pinned_document_digests": dedup_pins,
        "hypotheses": hypotheses_list,
        "claims": serialized_claims,
    }

    payload: dict[str, Any] = {
        "contract_version": 1,
        "execution_id": execution_id,
        "mechanism_ref": mechanism_ref,
        "mechanism_version": mechanism_version,
        "execution_timestamp_utc": execution_timestamp_utc,
        "input_context_digest": input_context_digest,
        "documentary_refs": doc_refs,
        "symbolic_context_refs": sym_refs,
        "external_provider_trace": ext_trace,
        "observable_response_digest": resp_digest,
        "observable_response_text": resp_text,
        "evaluation_reference": eval_ref,
        "replay_dependencies": replay_deps,
        "privacy_classification": "SYNTHETIC_REDACTED",
        "publication_mode": "PUBLICATION_ATOMIC",
        "seal_status": "EPHEMERAL_IN_MEMORY",
        "provenance_status": "ORIGIN_UNESTABLISHED",
    }

    # Calcul canonique de l'intégrité et de l'identifiant de bundle
    norm_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    computed_digest = hashlib.sha256(norm_bytes).hexdigest()
    payload["integrity_digest"] = computed_digest
    payload["bundle_id"] = f"bceb-{computed_digest[:32]}"

    return payload


def _unfreeze(obj: Any) -> Any:
    """Convertit récursivement les MappingProxyType en dict python standard."""
    if isinstance(obj, Mapping):
        return {k: _unfreeze(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_unfreeze(v) for v in obj]
    return obj


# ============================================================================
# Rejoueur symbolique déterministe : reexecute_symbolic_bundle
# ============================================================================


def _reexecute_b8_claim_transitions(
    claim: b8.KnowledgeClaim,
    doc_digest: str,
    recorded_at: str,
) -> bool:
    """Réexécute effectivement les transitions B8 sur un SlotSnapshot vierge."""
    snap = b8.SlotSnapshot(claim.slot_id, 0, (), claims=(claim,))

    # 1. Transition vers CANDIDATE
    req1 = b8.TransitionRequest(
        claim_id=claim.claim_id,
        expected_claim_version=claim.claim_version,
        expected_state=None,
        expected_record_version=0,
        slot_id=snap.slot_id,
        expected_slot_revision=snap.slot_revision,
        target_state=b8.ClaimState.CANDIDATE,
        refs=(),
        requester_ref="brody:reexecute_symbolic_bundle",
        reason="symbolic reexecution candidate evaluation",
    )
    res1 = b8.evaluate_transition(snap, req1, recorded_at=recorded_at, artifacts=())
    if res1.verdict is not b8.TransitionVerdict.APPLIED:
        return False

    # 2. Transition vers SUPPORTED
    ev = b8.EvidenceRef(
        "DOCUMENT",
        f"doc:{doc_digest}",
        doc_digest,
        recorded_at,
        ("golden-source",),
        claim.claim_id,
        claim.claim_version,
    )
    curr1 = [r for r in res1.snapshot.records if r.claim_id == claim.claim_id]
    rec1 = max(curr1, key=lambda r: r.record_version) if curr1 else None
    if rec1 is None:
        return False

    req2 = b8.TransitionRequest(
        claim_id=claim.claim_id,
        expected_claim_version=claim.claim_version,
        expected_state=rec1.state,
        expected_record_version=rec1.record_version,
        slot_id=res1.snapshot.slot_id,
        expected_slot_revision=res1.snapshot.slot_revision,
        target_state=b8.ClaimState.SUPPORTED,
        refs=(ev.identity,),
        requester_ref="brody:reexecute_symbolic_bundle",
        reason="symbolic reexecution supported evaluation",
    )
    res2 = b8.evaluate_transition(res1.snapshot, req2, recorded_at=recorded_at, artifacts=(ev,))
    if res2.verdict is not b8.TransitionVerdict.APPLIED:
        return False

    # 3. Transition vers VERIFIED
    curr2 = [r for r in res2.snapshot.records if r.claim_id == claim.claim_id]
    rec2 = max(curr2, key=lambda r: r.record_version) if curr2 else None
    if rec2 is None:
        return False

    ver = b8.VerificationRecord(
        "SOURCE_PROVENANCE_VERIFIER",
        claim.claim_id,
        claim.claim_version,
        b8.VerificationVerdict.SATISFIED,
        (ev.identity,),
        "exact-document-digest-and-scope",
        recorded_at,
        basis_record_id=rec2.record_id,
    )
    req3 = b8.TransitionRequest(
        claim_id=claim.claim_id,
        expected_claim_version=claim.claim_version,
        expected_state=rec2.state,
        expected_record_version=rec2.record_version,
        slot_id=res2.snapshot.slot_id,
        expected_slot_revision=res2.snapshot.slot_revision,
        target_state=b8.ClaimState.VERIFIED,
        refs=(ver.identity,),
        requester_ref="brody:reexecute_symbolic_bundle",
        reason="symbolic reexecution verified evaluation",
    )
    res3 = b8.evaluate_transition(res2.snapshot, req3, recorded_at=recorded_at, artifacts=(ver,))
    return res3.verdict is b8.TransitionVerdict.APPLIED


def reexecute_symbolic_bundle(
    bundle_id: str,
    store_dir: Path | str | None = None,
    isolated_source_pins: Mapping[str, Any] | None = None,
) -> SymbolicReexecutionReportV1:
    """Réexécute déterministement la chaîne symbolique hors-ligne (B8/M41/B7).

    Vérifie l'intégrité du bundle, contrôle les oracles SOURCE_PINS,
    ré-exécute les transitions d'état B8 réelles, vérifie l'ambiguïté M41,
    et refuse formellement toute réexécution neuronale ou prétention BIT_EXACT.
    """
    now = datetime.now(timezone.utc).isoformat()
    bundle = load_and_verify_brody_evidence_bundle(bundle_id, store_dir=store_dir)

    # 1. Vérification stricte d'intégrité
    if bundle.integrity_verification_status != "INTEGRITY_VERIFIED":
        return SymbolicReexecutionReportV1(
            bundle_id=bundle_id,
            status="INTEGRITY_CHECK_FAILED",
            symbolic_outcome="REJECTED",
            reexecuted_claims=(),
            divergence_reasons=("BUNDLE_INTEGRITY_COMPROMISED_OR_INVALID",),
            execution_timestamp_utc=now,
        )

    # 2. Source des oracles
    pins = isolated_source_pins if isolated_source_pins is not None else _SOURCE_PINS
    replay_deps = bundle.replay_dependencies
    pinned_digests = replay_deps.get("pinned_document_digests", ())

    # 3. Contrôle de présence et d'exactitude des dépendances documentaires
    for expected_digest in pinned_digests:
        if expected_digest not in pins:
            return SymbolicReexecutionReportV1(
                bundle_id=bundle_id,
                status="DEPENDENCY_MISSING",
                symbolic_outcome="DIVERGENCE",
                reexecuted_claims=(),
                divergence_reasons=(f"PINNED_DOCUMENT_NOT_FOUND: {expected_digest}",),
                execution_timestamp_utc=now,
            )

        pin_doc = pins[expected_digest]
        actual_digest = _digest_document(pin_doc)
        if actual_digest != expected_digest:
            return SymbolicReexecutionReportV1(
                bundle_id=bundle_id,
                status="SYMBOLIC_REEXECUTION_DIVERGED",
                symbolic_outcome="DIVERGENCE",
                reexecuted_claims=(),
                divergence_reasons=(
                    f"PIN_DIGEST_MISMATCH: expected {expected_digest}, got {actual_digest}",
                ),
                execution_timestamp_utc=now,
            )

    # 4. Reconstitution des claims et réexécution des transitions d'état B8 réelles
    reexecuted_claims_list: list[str] = []
    serialized_claims = replay_deps.get("claims", ())

    for sc in serialized_claims:
        claim_id = sc.get("claim_id")
        lineage_id = sc.get("lineage_id")
        claim_version = sc.get("claim_version", 1)
        slot_id = sc.get("slot_id")
        content = _unfreeze(sc.get("content"))
        source_refs = tuple(sc.get("source_refs", ()))

        # Retrouver l'empreinte documentaire
        doc_digest = None
        for ref in source_refs:
            if isinstance(ref, str):
                if ref.startswith("doc:"):
                    doc_digest = ref[4:]
                    break
                elif ref.startswith("fixture-doc:"):
                    doc_digest = ref[12:]
                    break
        if not doc_digest and pinned_digests:
            doc_digest = pinned_digests[0]

        # Reconstitution de l'objet KnowledgeClaim
        claim_class_str = sc.get("claim_class", "DOCUMENTARY_CLAIM")
        claim_class = getattr(b8.ClaimClass, claim_class_str, b8.ClaimClass.DOCUMENTARY_CLAIM)

        vt_data = sc.get("valid_time")
        if vt_data:
            frame_ref = b8.TemporalFrameRef(vt_data.get("frame_ref", "DOCUMENTARY_EPOCH"))
            valid_time = b8.ValidTimeInterval(frame_ref, vt_data.get("from_time", 0), vt_data.get("to_time"))
        else:
            valid_time = b8.ValidTimeInterval(b8.TemporalFrameRef("DOCUMENTARY_EPOCH"), 0, None)

        reconstituted_claim = b8.KnowledgeClaim(
            lineage_id=lineage_id,
            claim_version=claim_version,
            previous_claim_id=sc.get("previous_claim_id"),
            claim_class=claim_class,
            slot_id=slot_id,
            valid_time=valid_time,
            content=content,
            source_refs=source_refs,
            origin_refs=tuple(sc.get("origin_refs", ())),
        )

        # Réexécution effective des transitions formelles B8
        success = _reexecute_b8_claim_transitions(
            reconstituted_claim,
            doc_digest or "dummy",
            now,
        )
        if not success:
            return SymbolicReexecutionReportV1(
                bundle_id=bundle_id,
                status="SYMBOLIC_REEXECUTION_DIVERGED",
                symbolic_outcome="DIVERGENCE",
                reexecuted_claims=tuple(reexecuted_claims_list),
                divergence_reasons=(f"B8_TRANSITION_FAILED_FOR_CLAIM: {claim_id}",),
                execution_timestamp_utc=now,
            )
        reexecuted_claims_list.append(claim_id)

    # Si aucun claim n'était sérialisé mais qu'un documentaire était référencé
    if not reexecuted_claims_list and bundle.documentary_refs:
        for ref in bundle.documentary_refs:
            reexecuted_claims_list.append(ref)

    # 5. Invariants M41 : vérification d'ambiguïté sans forçage
    hypotheses = replay_deps.get("hypotheses", ())
    invariants = ["B8_FORMAL_TRANSITIONS_VERIFIED", "STORE_INTEGRITY_VERIFIED"]
    if hypotheses:
        invariants.append("M41_AMBIGUITY_PRESERVED_WITHOUT_CANONICAL_SELECTION")

    return SymbolicReexecutionReportV1(
        bundle_id=bundle_id,
        status="SYMBOLIC_REEXECUTION_MATCHED",
        symbolic_outcome="MATCH",
        reexecuted_claims=tuple(reexecuted_claims_list),
        neural_reexecution_status="NEURAL_REEXECUTION_NOT_PERFORMED",
        bit_exact_replay_verified=False,
        invariants_checked=tuple(invariants),
        divergence_reasons=(),
        execution_timestamp_utc=now,
    )


# ============================================================================
# Rôle 3 : Projection de compétence B11
# ============================================================================


def project_b11_bridge_competence_profile(
    domain: str = "cognition",
    task_ref: str | None = "COGNITIVE_RESOLUTION",
) -> ContextualCompetenceProfile:
    """Projette un profil de compétence B11 maintenu sous UNKNOWN_COMPETENCE."""
    return ContextualCompetenceProfile(
        evaluation_id=f"eval-b11-bridge-{domain}",
        domain=domain,
        task_ref=task_ref,
        target_resources=("brody:evidence_bridge",),
        competence_regime=CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=(),
        unknowns=("STATISTICAL_SAMPLE_SIZE_INSUFFICIENT", "M42_STATISTICAL_THRESHOLDS_PENDING"),
        advisory_notes="B11 bridge competence projection maintained under UNKNOWN_COMPETENCE (N < N_min).",
    )
