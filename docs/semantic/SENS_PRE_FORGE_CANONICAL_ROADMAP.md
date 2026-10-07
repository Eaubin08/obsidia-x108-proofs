# SENS / PRE-FORGE — Canonical Roadmap (blocks 20 → 27)

RECOVERED_CANONICAL_MAPPING_DATE=2026-10-07

PROJECT_DECISION_HISTORY=mapping fixed in late-September 2026 SENS/PRE-FORGE work (project
tickets) and reused during final closure. Before this commit the repository named only
blocks 25 ("master block 25", ReviewJoin V1) and 26 ("master block 26", Semantic Closure);
blocks 20–24 and 27 were NOT previously recorded in Git. This document freezes the mapping.

This map is authoritative for the current SENS/PRE-FORGE closure. Older historical Obsidia
roadmaps, phase numbers (P-, F-, palier numbering) or legacy block numbers must NOT override
or be mixed with it.

## Director invariant (20 → 26)

ONE OBJECT + MANY INDEPENDENT PROJECTIONS + TYPED RELATIONS + NO SILENT PROMOTION.

One content object may independently carry scope, perspective, linguistic commitment,
occurrence, epistemic status, temporal position, causal position, provenance, evidence and
unknown / unresolved state. These axes are never collapsed into one truth value.

## Dependency order

20 → 21 → 22 → 23 → 24 → 25 → 26 → 27. Block 24 is the immediate semantic foundation of 25;
26 consumes 20–25; 27 starts only after SENS CLOSED.

## 20 — COORDINATION

Purpose: preserve coordinated semantic branches without silent loss, false fusion or
unsupported shared structure.

- every meaningful coordinated branch survives ("A et B", "A ou B", "A puis B", "et que",
  "et qui", sibling relatives);
- predicate coordination != noun-phrase coordination;
- a shared subject is propagated only where structurally justified;
- no coordination creates a false request / action;
- unresolved ownership / subject stays explicit.

Invariants: COORDINATION != FUSION; ALL BRANCHES CONSERVED.

## 21 — EPISTEMIC PROJECTION

Purpose: keep epistemic status independent from truth, occurrence and authority
(OBSERVED, REPORTED, BELIEVED, LEARNED, KNOWN, plus explicit unresolved / unknown states).

Invariants: REPORTED != TRUE; BELIEVED != TRUE; OBSERVED != AUTHORIZED;
KNOWN != EXECUTABLE; source / provenance conserved. No silent promotion claim → fact,
report → observation, belief → knowledge, knowledge → authority.

## 22 — TEMPORAL PROJECTION

Purpose: preserve temporal position without collapsing different times (event, observation,
report, knowledge time where the semantic model supports them; tense_aspect, realized,
deixis, PRECEDES, temporal context).

Invariants: EVENT_TIME != REPORT_TIME; REPORT_TIME != KNOWLEDGE_TIME;
BEFORE/AFTER != CAUSALITY; missing time stays missing / unknown, never invented.
SENS projection only (no MMonde TimeEnvelope here).

## 23 — CAUSAL PROJECTION

Purpose: prevent temporal order, correlation or linguistic implication from becoming proven
causality.

Invariants: PRECEDES != CAUSES; CORRELATED != CAUSAL; CLAIMED_CAUSE != VERIFIED_CAUSE;
"parce que / donc / car" is a claimed linguistic relation, never world causal proof; no causal
relation creates authority. (F12/F13 physical causality contracts are out of SENS scope.)

## 24 — CONTRADICTION / UNKNOWN / UNRESOLVED

Purpose: preserve unresolved meaning and contradictions without silently selecting a winner.

Invariants: UNKNOWN != FALSE; UNRESOLVED != ABSENT; CONTRADICTION != AUTOMATIC RESOLUTION;
OPEN != SAFE FALSE STRUCTURE. Contradictory branches, unknown content and unresolved
references stay represented; semantic closure stays open / blocked when required.

## 25 — REVIEWJOIN V1 (existing master block 25)

Purpose: gather views without becoming a resolution authority; keeps perspectives,
provenance, evidence, unknowns, unresolved states and contradictions.
Invariant: JOIN != RESOLVE (no vote, average, truth scalar, winner or decision authority).
Implementation: `app/semantic/lattice/review_join_v1.py`; tests
`tests/test_review_join_v1.py`, `tests/test_cert_reviewjoin_v1.py`.

## 26 — SEMANTIC CLOSURE (existing master block 26)

Purpose: distinguish semantic completeness from mere output existence.
Invariant: OUTPUT_EXISTS != SEMANTIC_CLOSURE; closed only when no semantic blocker remains.
Implementation: `app/semantic/lattice/semantic_closure.py`; tests
`tests/test_cert_semantic_closure.py`, `tests/test_semantic_closure_events.py`,
`tests/test_semantic_closure_ambiguity.py`.

## 27 — B6 RUNTIME WIRING

Starts only after SENS CLOSED. State-explicit harness seam only; it must not be overloaded
with full Cognition / JEV behaviour. Constitutional boundaries retained: KX108_ONLY,
memory_write=False, emits_act=False, kernel_mutation=False.

## Related frozen material

- Deferred limits: `docs/semantic/SENS_DEFERRED_LIMITS_REGISTRY.md` (D1–D5, FROZEN_DEFERRED).
