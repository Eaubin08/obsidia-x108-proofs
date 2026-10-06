# F8 — Governed world decision proof V0

Status: implementation candidate.

F8 does not invent a second proof system. The repository already has canonical decision records, OS3 ticket/replay, execution envelopes and receipts for execution rails. This stage adds the missing proof boundary for the F3-F7 world path itself.

```text
WorldState / DomainState references
        + evidence / provenance
        + proposed action reference
                    |
                    v
            GovernancePayloadV0
                    |
                    v
                 KX108
                    |
                    v
       CanonicalDecisionEnvelope
                    |
                    v
 GovernedWorldDecisionProofV0
```

The proof packet hash-binds:

- world-state and domain-state references;
- domain identity and proposed-action reference;
- evidence and provenance references;
- the real KX108 decision id, trace id, gate and reason;
- a canonical projection of the real CanonicalDecisionEnvelope.

Verification fails on input substitution, envelope mutation or proof mutation.

The packet is audit evidence only:

```text
proof_authority = false
execution_authority = false
decision_authority = KX108_ONLY
```

An ALLOW proof is therefore not an execution permission. Existing downstream ticket, Binder/execution checks, replay and receipts remain mandatory wherever execution is actually requested.
