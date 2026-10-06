# F7 — Governed world -> KX108 V0

Status: implementation candidate.

F3-F6 established a conservative path from situated observations through MMonde and domain translation. F7 closes the governance boundary without moving world semantics into the kernel.

```text
WorldStateV0
  -> DomainStateRefV0
  -> GovernancePayloadV0
  -> DomainAggregate (non-sovereign transport)
  -> GuardX108
  -> CanonicalDecisionEnvelope
```

Authority invariant:

```text
WORLD != DECISION
DOMAIN != DECISION
PROPOSAL != PERMISSION
ALLOW from world/domain = impossible
GuardX108 = sovereign gate
KX108_ONLY
```

The adapter transports only domain identity, confidence supplied at the governance boundary, unknowns, contradictions, risks, evidence/provenance references and an optional proposed-action reference. It forces the pre-Guard market verdict to HOLD. A clean input can therefore receive ALLOW only because GuardX108 creates it.

Unsupported domains fail before GuardX108. Unknowns and low confidence can produce HOLD through GuardX108; contradiction thresholds can produce BLOCK through GuardX108. An ALLOW envelope remains subject to the existing downstream ticket/Binder/execution/receipt chain; F7 does not grant execution authority.

F7 does not add domain laws to KX108, does not make MMonde authoritative, does not let multimodal or GPS evidence self-authorize, and does not bypass the existing canonical decision envelope.
