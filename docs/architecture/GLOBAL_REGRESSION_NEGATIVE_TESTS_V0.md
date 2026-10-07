# F24 — Global Regression / Negative Tests V0

Status: IMPLEMENTED / VALIDATION REQUIRED

## Purpose

Harden the complete first-world chain before public freeze.

F24 does not add a new domain or intelligence layer. It revisits known technical debt and adds negative tests around claim boundaries, replayability, source independence, vision provenance and scientific possibility semantics.

## Scope

F12 → F22 remain the functional baseline.

F24 specifically hardens:

### F15 — Physical Evidence Plane

Changes:
- a single source can no longer be marked source-independent;
- a `ReplayablePhysicalEvidenceCandidateV0` now requires explicit `replay_refs`;
- source hashes from situated measurements are bound into `source_hash_refs`.

Rules reinforced:

`one source != independent corroboration`

`replayable != replay reference absent`

`source provenance != source hash binding`

### F16 — Vision / Real Image

The modality bridge now preserves:
- author ref;
- application ref;
- consent ref;
- full visual primitive descriptors:
  - geometry;
  - mask;
  - depth;
  - motion;
  - text;
  - feature refs;
  - primitive evidence refs.

The dynamic import in the world bridge is removed in favor of the explicit canonical bridge import.

Rules reinforced:

`image context must survive projection`

`primitive id alone != primitive evidence`

### F18 — Science / Constraint Engine

Scientific invariants now distinguish formal proof from empirical evidence:
- `proof_refs` may support formally proven invariants;
- `evidence_refs` may support empirically backed invariants;
- a non-assumed invariant requires at least one of the two.

Resolved possibility states are hardened:
- `POSSIBLE` and `IMPOSSIBLE` both require explicit evidence;
- both require explicit model scope;
- `SATISFIED + IMPOSSIBLE` is rejected as internally inconsistent.

Rules reinforced:

`empirical evidence != formal proof`

`POSSIBLE != unsupported guess`

`IMPOSSIBLE != unbounded impossibility`

`model-scoped impossibility != metaphysical impossibility`

## Negative tests

F24 adds tests proving that:
- one physical event cannot establish source independence;
- replayable evidence without replay refs fails closed;
- source hashes are preserved;
- image capture governance and primitive evidence survive projection;
- empirical invariants can be evidence-backed without fake formal proof;
- resolved possibility without evidence fails closed;
- resolved possibility without model scope fails closed;
- SATISFIED and IMPOSSIBLE cannot coexist.

## Authority

No F24 hardening changes:
- KX108_ONLY;
- no decision authority in periphery;
- no ACT authority in periphery;
- observation != truth;
- domain != authority;
- proof/evidence != permission.

## Validation plan

1. targeted F24 tests;
2. complete `tests/periphery`;
3. global repository regression;
4. compare failures against the historical baseline families;
5. freeze only if no new F12→F24 regression is introduced.

## Next phase

F25 — Public Freeze / Release Candidate.

No F25 freeze before F24 validation.
