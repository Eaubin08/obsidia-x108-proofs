"""Adaptateur de preuves Studio E11/V1/V2 vers le faisceau BCE V1.

Composant de frontire pur :
- Normalise les reus d'excution Studio (V1 et V2 opt-in).
- Drive canoniquement le payload  19 champs conforme  BrodyCognitiveEvidenceBundleV1.
- Maintient l'tanchit B6 / M41 sans fabriquer d'hypothses artificielles.
- Zro I/O disque, zro transport rseau, immutabilit des structures d'entre.
- Autorite exclusive : KX108_ONLY.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping


# Constantes de frontire et schma ferm BCE V1
_BCE_CONTRACT_VERSION: int = 1
_ALLOWED_PROVENANCE_STATUS: str = "STUDIO_E11_ADAPTED"
_UNSEALED_PAYLOAD_STATUS: str = "UNSEALED_ADAPTER_PAYLOAD"
_DRAFT_PUBLICATION_MODE: str = "DRAFT_ONLY"
_AUDIT_PRIVACY_CLASSIFICATION: str = "INTERNAL_AUDIT_ONLY"

# Cls contractuelles fermes autorises par CognitiveEvidencePublisher
_BCE_V1_REQUIRED_KEYS = frozenset({
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


def adapt_studio_receipt_to_bundle_payload(
    studio_payload: Mapping[str, Any],
    evaluation_reference: Mapping[str, Any] | None = None,
    replay_mode: str = "DETERMINISTIC_OFFLINE",
) -> dict[str, Any]:
    """Transforme purement un reu d'excution Studio E11/V1/V2 en payload canonique BCE V1 (19 champs).

    Fonction pure :
    - Zro I/O disque ;
    - Zro requte rseau ;
    - Zro mutation des arguments d'entre ;
    - Fail-closed : lve ValueError si les invariants Studio ou d'autorit sont viols.
    """
    if not isinstance(studio_payload, Mapping):
        raise ValueError("INVALID_STUDIO_PAYLOAD: payload must be a mapping")

    # 1. Contrle d'autorit et d'invariants souverains KX108 (fail-closed F3-06)
    authority = studio_payload.get("decision_authority")
    if authority != "KX108_ONLY":
        raise ValueError(
            f"GOVERNANCE_INVARIANT_VIOLATION: authority must be 'KX108_ONLY', got {authority!r}"
        )

    for false_invariant in (
        "emits_act",
        "memory_write",
        "kernel_mutation",
        "x108_mutation",
        "allowed_to_act",
        "allowed_to_decide",
    ):
        if studio_payload.get(false_invariant) is True:
            raise ValueError(
                f"GOVERNANCE_INVARIANT_VIOLATION: {false_invariant} must be False"
            )

    # Vrification des refus ou blocages en amont
    refusal_values = [
        studio_payload.get("status"),
        studio_payload.get("gate_verdict"),
    ]
    receipt_hint = studio_payload.get("cognitive_runtime_receipt")
    if isinstance(receipt_hint, Mapping):
        refusal_values.append(receipt_hint.get("status"))
        refusal_values.append(receipt_hint.get("completeness"))
        ticket = receipt_hint.get("decision_ticket_dry_run")
        if isinstance(ticket, Mapping):
            refusal_values.append(ticket.get("decision"))

    for val in refusal_values:
        if isinstance(val, str) and val in {
            "BLOCK",
            "BLOCKED",
            "BLOCKED_READONLY",
            "X108_FAIL_CLOSED",
            "ROGUE_AUTHORITY",
        }:
            raise ValueError(f"UPSTREAM_GOVERNANCE_REFUSAL: blocked value {val!r}")

    # 2. Dtection de l'enveloppe cognitive et d'excution
    receipt: Mapping[str, Any]
    if isinstance(receipt_hint, Mapping) and receipt_hint:
        receipt = receipt_hint
    else:
        receipt = studio_payload

    execution_id = str(
        receipt.get("signal_id")
        or studio_payload.get("signal_id")
        or studio_payload.get("experiment_id")
        or "sig-studio-unidentified"
    )

    execution_timestamp_utc = str(
        receipt.get("created_at")
        or studio_payload.get("timestamp")
        or datetime.now(timezone.utc).isoformat()
    )

    receipt_version = str(
        receipt.get("version")
        or studio_payload.get("final_answer_source")
        or "REAL_COGNITIVE_JOIN_C1_V1"
    )

    # 3. Dtection de la variante ditoriale Studio V1 vs V2 opt-in (F3-02)
    editorial_art = studio_payload.get("editorial_artifact")
    is_v2 = (
        studio_payload.get("editorial_version_requested") == "V2"
        or (isinstance(editorial_art, Mapping) and editorial_art.get("editorial_version") == "V2")
        or "V2" in str(studio_payload.get("final_answer_source", ""))
        or (isinstance(editorial_art, Mapping) and "V2" in str(editorial_art.get("schema", "")))
    )

    mechanism_version = f"{receipt_version}:V2" if is_v2 and "V2" not in receipt_version else receipt_version
    mechanism_ref = "brody:studio_editorial_v2" if is_v2 else "brody:studio_editorial"

    # 4. Extraction du texte observable et condensat d'entre
    observable_response_text: str
    if isinstance(editorial_art, Mapping):
        draft = editorial_art.get("draft")
        realization = editorial_art.get("realization")
        if isinstance(draft, Mapping) and "text" in draft:
            observable_response_text = str(draft["text"])
        elif isinstance(realization, Mapping) and "text" in realization:
            observable_response_text = str(realization["text"])
        else:
            observable_response_text = str(studio_payload.get("response", ""))
    else:
        observable_response_text = str(
            studio_payload.get("response") or studio_payload.get("final_answer") or ""
        )

    observable_response_digest = hashlib.sha256(
        observable_response_text.encode("utf-8")
    ).hexdigest()

    # Extraction du contexte d'entre (pre-reasoning)
    pre_reasoning = studio_payload.get("pre_reasoning_snapshot")
    if isinstance(pre_reasoning, Mapping) and "user_message" in pre_reasoning:
        input_text = str(pre_reasoning["user_message"])
    else:
        input_text = str(
            studio_payload.get("memory_query")
            or studio_payload.get("message")
            or execution_id
        )

    input_context_digest = hashlib.sha256(input_text.encode("utf-8")).hexdigest()

    # 5. Extraction des rfrences documentaires et contextuelles
    doc_refs: list[str] = []
    if isinstance(studio_payload.get("source_file_refs"), (list, tuple)):
        doc_refs.extend(str(r) for r in studio_payload["source_file_refs"])
    if isinstance(studio_payload.get("source_pack_entries_used"), (list, tuple)):
        doc_refs.extend(str(r) for r in studio_payload["source_pack_entries_used"])

    sym_refs: list[str] = []
    if isinstance(pre_reasoning, Mapping):
        for unk in pre_reasoning.get("unresolved_unknowns", ()):
            sym_refs.append(f"unknown:{unk}")
    shadow_mem = receipt.get("cognition_shadow_memory")
    if isinstance(shadow_mem, Mapping) and isinstance(shadow_mem.get("entries"), (list, tuple)):
        for e in shadow_mem["entries"]:
            if isinstance(e, Mapping) and "state_id" in e:
                sym_refs.append(str(e["state_id"]))

    # 6. Trace neuronale non causale
    ext_trace_raw = receipt.get("local_model_evidence_snapshot") or studio_payload.get(
        "local_model_evidence_snapshot", {}
    )
    called = bool(
        isinstance(ext_trace_raw, Mapping) and ext_trace_raw.get("model_call_used", False)
    )
    ext_trace = {
        "called": called,
        "causal_contribution_verified": False,
        "provider": "OFFLINE_NEURAL_SNAPSHOT",
        "snapshot_status": (
            ext_trace_raw.get("status", "NOT_OBSERVED")
            if isinstance(ext_trace_raw, Mapping)
            else "NOT_OBSERVED"
        ),
    }

    # 7. Dpendances de replay (F3-08 : aucune promotion B6 -> M41 artificielle)
    replay_dependencies: dict[str, Any] = {
        "replay_mode": replay_mode,
        "source": "STUDIO_E11_OFFLINE",
        "b6_context_status": (
            shadow_mem.get("b6_context_status", "NOT_OBSERVED")
            if isinstance(shadow_mem, Mapping)
            else "NOT_OBSERVED"
        ),
        "M41_COEXISTING_HYPOTHESES": [],  # Jamais d'hypothses M41 fabriques
    }

    # 8. Assemblage du payload non scell  19 champs
    payload: dict[str, Any] = {
        "contract_version": _BCE_CONTRACT_VERSION,
        "execution_id": execution_id,
        "mechanism_ref": mechanism_ref,
        "mechanism_version": mechanism_version,
        "execution_timestamp_utc": execution_timestamp_utc,
        "input_context_digest": input_context_digest,
        "documentary_refs": tuple(sorted(set(doc_refs))),
        "symbolic_context_refs": tuple(sorted(set(sym_refs))),
        "external_provider_trace": ext_trace,
        "observable_response_digest": observable_response_digest,
        "observable_response_text": observable_response_text,
        "evaluation_reference": copy.deepcopy(dict(evaluation_reference or {})),
        "replay_dependencies": replay_dependencies,
        "privacy_classification": _AUDIT_PRIVACY_CLASSIFICATION,
        "publication_mode": _DRAFT_PUBLICATION_MODE,
        "seal_status": _UNSEALED_PAYLOAD_STATUS,
        "provenance_status": _ALLOWED_PROVENANCE_STATUS,
    }

    # 9. Drivation de l'intgrit et du bundle_id selon la rgle canonique BCE
    data_for_hash = {
        k: v for k, v in payload.items() if k not in ("integrity_digest", "bundle_id")
    }
    norm_bytes = json.dumps(
        data_for_hash, sort_keys=True, ensure_ascii=False
    ).encode("utf-8")
    computed_digest = hashlib.sha256(norm_bytes).hexdigest()
    computed_bundle_id = f"bceb-{computed_digest[:32]}"

    payload["integrity_digest"] = computed_digest
    payload["bundle_id"] = computed_bundle_id

    # Vrification d'intgrit formelle du schma ferm
    extra = set(payload.keys()) - _BCE_V1_REQUIRED_KEYS
    missing = _BCE_V1_REQUIRED_KEYS - set(payload.keys())
    if extra or missing:
        raise ValueError(
            f"BCE_SCHEMA_VIOLATION: extra={sorted(extra)}, missing={sorted(missing)}"
        )

    return payload
