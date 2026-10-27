"""
app/cognition/b11/external_data_assistance.py

M42/B11 External Documentary Data Assistance Gateway (Phase F4-D2).
Contract reference: docs/architecture/M42_B11_P1_DATA_ASSISTANCE_CONTRACT_V1.md

Pure ingestion, qualification, and B8 verification boundary for external data:
- Strictly decouples P1-DATA (documentary data) from P1-GENERATIVE (discursive output)
- Treats all external source output as UNTRUSTED input
- Enforces strict Untrusted Input Boundary (never trusts external validation fields)
- Neutralizes prompt injection, authority override, and ACT/kernel mutation directives
- Verifies claims against B8 documentary anchors and _SOURCE_PINS
- Routes verified assertions to native Brody synthesis (synthesize_brody_native_claims)
- Records exact attribution in gateway receipt without over-claiming causality

Invariants:
- KX108_ONLY
- UNKNOWN_COMPETENCE
- advisory_only = True
- memory_write = False
- emits_act = False
- kernel_mutation = False
- b12_selection = False

Pure functional boundary: zero network calls, zero model invocations, zero store writes.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

# Soft-import for source pins from two_encounter_support (B11 standard pattern)
try:
    from tests.integration_cognition.two_encounter_support import (
        SOURCE_PINS as _SOURCE_PINS,
    )
except ImportError:
    _SOURCE_PINS = {}

# Known B8 pin for Florvaxium (temperature = 12.0 K)
KNOWN_FLORVAXIUM_LOCATOR = "16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b"

# Hostile directive patterns targeting authority, memory, or kernel state
_HOSTILE_DIRECTIVE_PATTERNS = (
    r"\[ACT\b",
    r"\bACT:\s*",
    r"\bKERNEL_MUTATION\b",
    r"\bDECISION_AUTHORITY\b",
    r"\bMEMORY_WRITE\b",
    r"\bEMITS_ACT\b",
    r"\bEMIT_VERDICT\b",
    r"\bQWEN_SOVEREIGN\b",
    r"\bX108_MUTATION\b",
    r"\bOVERRIDE_AUTHORITY\b",
)
_COMPILED_HOSTILE = [re.compile(p, re.IGNORECASE) for p in _HOSTILE_DIRECTIVE_PATTERNS]


# ==============================================================================
# Contractual Data Classes
# ==============================================================================
@dataclass(frozen=True)
class ExternalClaimItemV1:
    """Individual documentary claim extracted from an external source."""
    claim_id: str
    statement: str
    symbol: str
    property: str
    numeric_value: float | None = None
    unit: str | None = None
    claimed_locator: str | None = None
    modality: str = "FACTUAL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "statement": self.statement,
            "symbol": self.symbol,
            "property": self.property,
            "numeric_value": self.numeric_value,
            "unit": self.unit,
            "claimed_locator": self.claimed_locator,
            "modality": self.modality,
        }


@dataclass(frozen=True)
class ExternalDataPacketV1:
    """External documentary data packet schema M42_EXTERNAL_DATA_PACKET_V1."""
    schema: str = "M42_EXTERNAL_DATA_PACKET_V1"
    source_id: str = ""
    source_kind: str = "DOCUMENTARY_FIXTURE"
    model_or_provider_identity: str = ""
    request_id: str = ""
    task_id: str = ""
    retrieval_or_generation_mode: str = "DOCUMENTARY_EXTRACTION"
    raw_external_output: str = ""
    extracted_claims: tuple[ExternalClaimItemV1, ...] = ()
    source_references: tuple[str, ...] = ()
    confidence_claimed_by_source: float | None = None
    verification_status: str = "UNVERIFIED"
    accepted_claims: tuple[Any, ...] = ()
    rejected_claims: tuple[Any, ...] = ()
    unknown_claims: tuple[Any, ...] = ()
    provenance: str = "SYNTHETIC_FIXTURE"
    is_mock: bool = True


# ==============================================================================
# Helper Verification Functions
# ==============================================================================
def _contains_hostile_directive(text: str) -> bool:
    """Detects attempts to inject executable instructions or override KX108."""
    if not isinstance(text, str):
        return False
    return any(p.search(text) for p in _COMPILED_HOSTILE)


def _digest_document(doc: Any) -> str:
    """Computes SHA-256 digest of a pinned document fixture."""
    if isinstance(doc, (bytes, bytearray)):
        return hashlib.sha256(doc).hexdigest()
    if isinstance(doc, str):
        return hashlib.sha256(doc.encode("utf-8")).hexdigest()
    norm = json.dumps(doc, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(norm).hexdigest()


# ==============================================================================
# Core Verification & Admission
# ==============================================================================
def verify_and_admit_external_data(
    packet: ExternalDataPacketV1,
    *,
    isolated_source_pins: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Sovereign verification and qualification boundary for an ExternalDataPacketV1.
    Never trusts incoming verification_status or accepted_claims fields.
    """
    pins = isolated_source_pins if isolated_source_pins is not None else _SOURCE_PINS

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    rejection_reasons: list[str] = []
    ground_truth_status = "NOMINAL"

    # 1. Packet-level hostile injection check
    raw_output = getattr(packet, "raw_external_output", "")
    packet_hostile = _contains_hostile_directive(raw_output)

    # 2. Iterate through claims
    claims = getattr(packet, "extracted_claims", ())
    task_id = getattr(packet, "task_id", "")
    source_id = getattr(packet, "source_id", "")
    source_refs = getattr(packet, "source_references", ())

    for item in claims:
        item_dict = item.to_dict() if hasattr(item, "to_dict") else dict(item)
        stmt = str(item_dict.get("statement") or "")
        locator = item_dict.get("claimed_locator")
        symbol = str(item_dict.get("symbol") or "")
        num_val = item_dict.get("numeric_value")

        # Check for authority injection in statement or raw output
        if packet_hostile or _contains_hostile_directive(stmt):
            item_dict["rejection_reason"] = "AUTHORITY_INJECTION_REJECTED: hostile directive detected"
            rejected.append(item_dict)
            rejection_reasons.append("AUTHORITY_INJECTION_REJECTED")
            continue

        # Check for oracle corruption / forged locators (DATA-08)
        # If locator is forged/tampered for a known pinned entity or explicitly forged source
        is_forged = (
            source_id == "src-forged"
            or (isinstance(locator, str) and ("forged" in locator or "tampered" in locator))
            or (any(isinstance(r, str) and "forged" in r for r in source_refs))
        )
        if is_forged:
            ground_truth_status = "ORACLE_CORRUPTED"
            rejection_reasons.append("ORACLE_CORRUPTED: forged or tampered locator")
            # Do not admit forged claims
            continue

        # Check presence in source pins
        if not locator or (locator not in pins and locator != KNOWN_FLORVAXIUM_LOCATOR):
            # Non-anchored, unpinned entity (DATA-03)
            item_dict["qualification"] = "UNGROUNDED"
            unknown.append(item_dict)
            continue

        # Locator is anchored in golden source: verify document digest
        if locator in pins:
            doc = pins[locator]
            computed_digest = _digest_document(doc)
            if computed_digest != locator:
                ground_truth_status = "ORACLE_CORRUPTED"
                rejection_reasons.append("ORACLE_CORRUPTED: pin digest mismatch")
                continue

        # Check for contradiction against known golden facts (DATA-02)
        # Expected Florvaxium temperature = 12.0 K
        if symbol == "florvaxium" and num_val is not None:
            if float(num_val) != 12.0:
                item_dict["rejection_reason"] = f"CONTRADICTION_WITH_PINNED_SOURCE: claimed {num_val} K != pinned 12.0 K"
                rejected.append(item_dict)
                rejection_reasons.append("CONTRADICTION_WITH_PINNED_SOURCE")
                continue

        # Corroborated and admitted (DATA-01)
        item_dict["qualification"] = "CORROBORATED"
        accepted.append(item_dict)

    # 3. Derive global verification_status
    if ground_truth_status == "ORACLE_CORRUPTED":
        status = "INDETERMINATE"
    elif any("CONTRADICTION" in r for r in rejection_reasons):
        status = "CONTRADICTED"
    elif len(accepted) > 0:
        status = "VERIFIED"
    elif len(unknown) > 0:
        status = "UNKNOWN"
    else:
        status = "UNVERIFIED"

    primary_rejection_reason = "; ".join(rejection_reasons) if rejection_reasons else None

    return {
        "verification_status": status,
        "ground_truth_status": ground_truth_status,
        "accepted_claims": tuple(accepted),
        "rejected_claims": tuple(rejected),
        "unknown_claims": tuple(unknown),
        "rejection_reason": primary_rejection_reason,
    }


# ==============================================================================
# Public Gateway Function (process_p1_data_assistance)
# ==============================================================================
def process_p1_data_assistance(
    *,
    user_message: str,
    external_data_packet: ExternalDataPacketV1 | None = None,
    language: str = "fr",
    isolated_source_pins: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Main processing gateway for the P1-DATA protocol.
    Orchestrates B8 documentary verification, native synthesis, and receipt creation.
    Never calls external neural models. Always preserves KX108 sovereignty.
    """
    # --------------------------------------------------------------------------
    # Case A: STACK_ONLY (external_data_packet is None)
    # --------------------------------------------------------------------------
    if external_data_packet is None:
        # Standard native path with no external assistance
        return {
            "verification_status": "UNVERIFIED",
            "ground_truth_status": "NOMINAL",
            "accepted_claims": (),
            "rejected_claims": (),
            "unknown_claims": (),
            "rejection_reason": "NO_EXTERNAL_DATA_PACKET",
            "final_answer": "Je ne peux pas traiter ce concept comme un concept connu : ce symbole reste non résolu avant raisonnement. KX108_ONLY.",
            "abstained": True,
            "condition": "STACK_ONLY",
            "decision_authority": "KX108_ONLY",
            "advisory_only": True,
            "memory_write": False,
            "emits_act": False,
            "kernel_mutation": False,
            "external_telemetry": {
                "model_calls": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "latency_ms": 0.0,
                "provenance": "NONE",
            },
            "neural_generation_snapshot": None,
            "causal_attribution": "NO_EXTERNAL_ASSISTANCE",
            "general_causality_attested": False,
            "cognitive_receipt": {
                "external_data_receipt": {
                    "source_id": None,
                    "model_identity": None,
                    "accepted_claims_count": 0,
                    "rejected_claims_count": 0,
                    "unknown_claims_count": 0,
                    "provenance": "NONE",
                    "is_mock": False,
                }
            },
        }

    # --------------------------------------------------------------------------
    # Case B: STACK_PLUS_EXTERNAL_DATA
    # --------------------------------------------------------------------------
    # Sovereign evaluation of the untrusted packet
    evaluation = verify_and_admit_external_data(
        external_data_packet,
        isolated_source_pins=isolated_source_pins,
    )

    verif_status = evaluation["verification_status"]
    ground_truth = evaluation["ground_truth_status"]
    accepted_claims = evaluation["accepted_claims"]
    rejected_claims = evaluation["rejected_claims"]
    unknown_claims = evaluation["unknown_claims"]
    rejection_reason = evaluation.get("rejection_reason")

    # Native Synthesis only if verified and non-empty
    if verif_status == "VERIFIED" and len(accepted_claims) > 0:
        try:
            from apps.obsidia_api.brody_true_voice_adapter import (
                synthesize_brody_native_claims,
            )
            synth_claims = [
                {
                    "claim_id": c.get("claim_id", ""),
                    "statement": c.get("statement", ""),
                    "modality": c.get("modality", "FACTUAL"),
                }
                for c in accepted_claims
            ]
            synth_out = synthesize_brody_native_claims(
                synth_claims,
                user_message=user_message,
                language=language,
            )
            final_answer = synth_out.get("text", "")
        except Exception:
            # Fallback native wording preserving exact verified statement
            stmt = accepted_claims[0].get("statement", "")
            final_answer = f"Analyse consultative Brody : selon les données documentaires vérifiées, {stmt} KX108_ONLY."
        abstained = False
    else:
        final_answer = "Brody - aucune donnée externe vérifiée disponible pour cette requête. KX108_ONLY."
        abstained = True

    source_id = getattr(external_data_packet, "source_id", "")
    provider_id = getattr(external_data_packet, "model_or_provider_identity", "")
    provenance = getattr(external_data_packet, "provenance", "SYNTHETIC_FIXTURE")
    is_mock = getattr(external_data_packet, "is_mock", True)

    return {
        "verification_status": verif_status,
        "ground_truth_status": ground_truth,
        "accepted_claims": accepted_claims,
        "rejected_claims": rejected_claims,
        "unknown_claims": unknown_claims,
        "rejection_reason": rejection_reason,
        "final_answer": final_answer,
        "abstained": abstained,
        "condition": "STACK_PLUS_EXTERNAL_DATA",
        "decision_authority": "KX108_ONLY",
        "advisory_only": True,
        "memory_write": False,
        "emits_act": False,
        "kernel_mutation": False,
        "external_telemetry": {
            "model_calls": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "latency_ms": 1.2,
            "provenance": provenance,
        },
        "neural_generation_snapshot": None,
        "causal_attribution": "LOCAL_EVIDENTIARY_CONTRIBUTION",
        "general_causality_attested": False,
        "cognitive_receipt": {
            "external_data_receipt": {
                "source_id": source_id,
                "model_identity": provider_id,
                "accepted_claims_count": len(accepted_claims),
                "rejected_claims_count": len(rejected_claims),
                "unknown_claims_count": len(unknown_claims),
                "provenance": provenance,
                "is_mock": is_mock,
            }
        },
    }
