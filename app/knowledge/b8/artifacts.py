"""Typed immutable B8 objects consumed by the gate (spec §3, §4): claims, evidence, verification, attestation.

Every identity is a full SHA-256 over canonical JSON of every listed field (§3). Requests carry these
identities; the gate re-hashes the supplied objects (§9.1).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from app.knowledge.b8.contracts import AttestationKind, ClaimClass, VerificationVerdict
from app.knowledge.b8.serialization import full_identity
from app.knowledge.b8.temporal import ValidTimeInterval


def canonical_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "to_canonical"):
        return value.to_canonical()
    if isinstance(value, (tuple, list)):
        return [canonical_value(v) for v in value]
    if isinstance(value, dict):
        return {k: canonical_value(v) for k, v in value.items()}
    return value


class _Canonical:
    _prefix = ""
    _fields: tuple = ()

    def to_canonical(self) -> dict:
        return {f: canonical_value(getattr(self, f)) for f in self._fields}

    @property
    def identity(self) -> str:
        return full_identity(self._prefix, self.to_canonical())


@dataclass(frozen=True)
class KnowledgeClaim(_Canonical):
    lineage_id: str
    claim_version: int
    previous_claim_id: Optional[str]
    claim_class: ClaimClass
    slot_id: str
    valid_time: ValidTimeInterval
    content: Any
    source_refs: tuple = ()
    origin_refs: tuple = ()

    _prefix = "b8claim_"
    _fields = ("lineage_id", "claim_version", "previous_claim_id", "claim_class", "slot_id", "valid_time", "content")

    @property
    def claim_id(self) -> str:
        return self.identity


@dataclass(frozen=True)
class EvidenceRef(_Canonical):
    kind: str
    source_ref: str
    content_digest: str
    captured_at: Any
    provenance_refs: tuple
    claim_id: str
    claim_version: int
    confidence: Optional[float] = None  # descriptive only, never a precondition

    _prefix = "b8ev_"
    _fields = ("kind", "source_ref", "content_digest", "captured_at", "provenance_refs", "claim_id",
               "claim_version", "confidence")

    @property
    def complete_provenance(self) -> bool:
        return (bool(self.provenance_refs) and all(isinstance(p, str) and p.strip() for p in self.provenance_refs)
                and isinstance(self.source_ref, str) and bool(self.source_ref.strip())
                and isinstance(self.content_digest, str) and bool(self.content_digest.strip()))


@dataclass(frozen=True)
class VerificationRecord(_Canonical):
    verifier_family: str
    claim_id: str
    claim_version: int
    verdict: VerificationVerdict
    evidence_refs: tuple
    method_ref: str
    produced_at: Any
    basis_record_id: Optional[str] = None

    _prefix = "b8ver_"
    _fields = ("verifier_family", "claim_id", "claim_version", "verdict", "evidence_refs", "method_ref", "produced_at", "basis_record_id")


@dataclass(frozen=True)
class HumanAttestation(_Canonical):
    attestation_id: str
    actor_id: str
    identity_source: str
    auth_context_ref: str
    issued_at: Any
    claim_id: str
    claim_version: int
    attestation_kind: AttestationKind
    scope: Any
    proof_ref: Optional[str] = None

    _prefix = "b8att_"
    _fields = ("attestation_id", "actor_id", "identity_source", "auth_context_ref", "issued_at", "claim_id",
               "claim_version", "attestation_kind", "scope", "proof_ref")

    def admissible(self, trusted_identity_sources) -> bool:
        """§7: identity from an injected trusted boundary, recorded by auth_context_ref (no lookup, no IAM)."""
        return (self.identity_source in trusted_identity_sources
                and isinstance(self.auth_context_ref, str) and bool(self.auth_context_ref.strip()))
