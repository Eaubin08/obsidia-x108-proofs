"""C2.1 deny-only connector entry gate; no grants and no provider transport.

The gate checks that a previously verified external authorization has not been
revoked or superseded when the connector is entered. It cannot authenticate an
organization or confer KX108/WorldAction authority. A live connector must bind
the guard to its own dispatch boundary and supply independently verified proofs.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from periphery.native_ops.common_v0 import canonical_hash

SCHEMA = "V01_CONNECTOR_ENTRY_REVOCATION_GUARD_V0"


@dataclass(frozen=True)
class ConnectorEntryContextV0:
    organization_id: str
    principal_id: str
    delegate_id: str
    connector_id: str
    capability_id: str
    action_request_hash: str
    world_action_decision_hash: str
    ticket_hash: str
    delegation_hash: str
    generation: int
    organization_verified: bool = False
    delegation_verified: bool = False
    ticket_verified: bool = False
    kx108_allow_verified: bool = False

    def fingerprint(self) -> str:
        return canonical_hash(vars(self))


class ConnectorEntryGuardV0:
    """Deny-only, in-memory pre-dispatch check, not an authorization service.

    The lock covers revocation and the pre-dispatch decision. It does NOT cover
    asynchronous or external provider execution. No claim of atomic provider
    revocation or multi-process persistence is made.
    """

    def __init__(self):
        self._lock = RLock()
        self._generation = {}
        self._revoked = set()

    @staticmethod
    def _key(ctx):
        return (ctx.organization_id, ctx.delegate_id, ctx.connector_id,
                ctx.capability_id)

    def revoke(self, *, organization_id, delegate_id, connector_id, capability_id):
        key = (organization_id, delegate_id, connector_id, capability_id)
        if not all(isinstance(x, str) and x for x in key):
            raise ValueError("C21_REVOCATION_SCOPE_INVALID")
        with self._lock:
            self._revoked.add(key)
            self._generation[key] = self._generation.get(key, 0) + 1
            return self._generation[key]

    def inspect_before_dispatch(self, ctx, *, expected_organization_id,
                                expected_connector_id, expected_capability_id):
        with self._lock:
            if not isinstance(ctx, ConnectorEntryContextV0):
                return "BLOCK:C21_CONTEXT_INVALID"
            if not all(isinstance(v, str) and v for v in (
                ctx.organization_id, ctx.principal_id, ctx.delegate_id,
                ctx.connector_id, ctx.capability_id, ctx.action_request_hash,
                ctx.world_action_decision_hash, ctx.ticket_hash,
                ctx.delegation_hash
            )):
                return "BLOCK:C21_IDENTITY_OR_PROOF_ABSENT"
            if (ctx.organization_id != expected_organization_id or
                    ctx.connector_id != expected_connector_id or
                    ctx.capability_id != expected_capability_id):
                return "BLOCK:C21_SCOPE_MISMATCH"
            if not all((
                ctx.organization_verified, ctx.delegation_verified,
                ctx.ticket_verified, ctx.kx108_allow_verified,
            )):
                return "BLOCK:C21_EXTERNAL_ATTESTATION_UNPROVEN"
            key = self._key(ctx)
            if key in self._revoked:
                return "BLOCK:C21_DELEGATION_REVOKED"
            if ctx.generation != self._generation.get(key, 0):
                return "BLOCK:C21_GENERATION_STALE"
            # Boolean attestations are caller-controlled and cannot prove identity,
            # delegation, ticket or KX108 authenticity. No trusted verifier is
            # attached to this prototype: fail closed even if all flags are true.
            return "BLOCK:C21_INDEPENDENT_ATTESTATION_VERIFIER_NOT_BOUND"
