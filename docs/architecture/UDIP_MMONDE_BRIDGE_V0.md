# UDIP V0 — MMonde / Domain / Governance bridge

Status: F4 implementation candidate for the first Obsidia release.

This bridge materializes the smallest runtime boundary already required by UDIP V0:

```text
WorldStateV0
  -> DomainStateRefV0
  -> GovernancePayloadV0
  -> KX108 authority boundary
```

Constitutional invariants:

- DOMAIN != AUTHORITY.
- DOMAIN SIGNAL != DECISION.
- PROPOSAL != ACTION.
- SOURCE != TRUST.
- SOURCE PROVENANCE != REALITY AUTHENTICITY.
- GovernancePayload transports, structures, conserves and references; it does not decide.
- KX108 remains the sole ACT / HOLD / BLOCK authority.
- Binder permission is not created by this bridge.
- Domain-specific laws and semantics stay inside Domain Packs.
- MMonde remains representation-only and does not become a Domain Pack.

The MMonde -> Domain boundary conserves world-state identity, validity time, unknowns, contradictions, risk flags, evidence references and provenance/source references. It does not infer domain truth or silently complete missing semantics.

The Domain -> Governance boundary may carry a proposal reference but cannot contain a decision, Binder permission or action authority.

This V0 deliberately does not define business actions, a universal DomainState schema, Binder internals, execution adapters, physical authenticity, or a universal receipt/proof model. Those remain separate contracts or later forge stages.
