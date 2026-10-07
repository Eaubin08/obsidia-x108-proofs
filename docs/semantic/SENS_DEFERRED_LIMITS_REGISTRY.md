# SENS_DEFERRED_LIMITS_REGISTRY

Status: FROZEN — 2026-10-07
Frozen at HEAD: 9d35289b (B3-G CLOSED / PASS_WITH_DEFERRED, parser suite 2445 passed / 0 failed,
blocking defects 0).

## Doctrine

The entries below are NOT hidden blockers. They are explicitly known semantic limits, each
independently verified (B3-G final confirmation audit) to satisfy:

    FULL INPUT CONTENT = STRUCTURED CONTENT + EXPLICITLY UNRESOLVED CONTENT

and:

- NO FALSE AUTHORIZED ACTION
- NO FALSE STRONG RELATION
- NO FALSE PROVENANCE ASSERTED AS FACT
- NO SILENT CONTENT LOSS
- FAIL-CLOSED (frame and semantic closure stay open where the meaning is open)

This registry does NOT authorize adding arbitrary future limitations. A new deferred
semantic limit may be registered only if it is independently proven to satisfy the same
closure doctrine.

Forbidden deferred state: **FALSE STRUCTURE + OPEN FLAG**. A false request, false
participant, false relation, false provenance, silent loss or zero representation is a
BLOCKER, never a deferred limit, whatever flag accompanies it.

Downstream note (verified): `requested_world_actions` can only ADD governance
(`app/ir/unified_ir.py`); the parser grants no authority and never calls KX108.

---

## D1 — SENS-D1-COORDINATED-ANTECEDENT-RELATIVE-SUBJECT (formerly KNOWN_LIMIT_B)

- Canonical trigger: "Paul et Nadia qui lancent P échouent."
- Observed limitation: the subject of the relative predicate stays unresolved
  (`subject_unresolved:u1`).
- Conservation: the main predicate "échouent" is reported as
  `unanalyzed_predicative_content:…:main_predicate_after_relative_of=u1`.
- Safety: FALSE_ACTION=NO, FALSE_RELATION=NO, FALSE_PROVENANCE=NO, CONTENT_CONSERVED=YES,
  FAIL_CLOSED=YES, FRAME=OPEN.
- Future resolution candidate: Cognition / context (coordinated antecedent resolution).
- Status: FROZEN_DEFERRED

## D2 — SENS-D2-REDUNDANT-MAIN-PREDICATE-UNRESOLVED (formerly DEFERRED_C2)

- Trigger family: relatives between commas / sibling relatives where the real main
  predicate is already structurally safe, but an additional `main_predicate_unresolved`
  marker may remain.
- Observed limitation: excessive conservatism (redundant unresolved marker).
- Safety: CONTENT_CONSERVED=YES, FALSE_ACTION=NO, FALSE_RELATION=NO, FALSE_PROVENANCE=NO,
  FAIL_CLOSED=YES. No semantic certainty is falsely added.
- Future resolution candidate: later semantic refinement, only if useful.
- Status: FROZEN_DEFERRED

## D3 — SENS-D3-RESUMPTIVE-PRONOUN-COREFERENCE (formerly DEFERRED_C4)

- Canonical witnesses: "Le fichier que Marie l'ouvre disparaît.",
  "Le script que Paul lance, il échoue."
- Observed limitation: the resumptive pronoun / coreference is not resolved; the phrase or
  the relevant portion stays `unanalyzed_predicative_content` (explicitly unresolved).
- Safety: CONTENT_CONSERVED=YES, FALSE_ACTION=NO, FALSE_RELATION=NO, FALSE_PROVENANCE=NO,
  FAIL_CLOSED=YES.
- Future resolution candidate: Cognition / context / memory (coreference resolution).
- Status: FROZEN_DEFERRED

## D4 — SENS-D4-UNRESOLVED-PROTASIS-CONSEQUENT-LINK

- Canonical trigger: "Si le script qui teste P échoue, lance R." (including the verified
  source variants "Si, selon Marie, …", "Si, apparemment, …", "Si, d'après les logs, …").
- Observed limitation: the unknown protasis main predicate is explicitly named
  (`conditional_protasis`), the frame stays open; when the protasis has no PredicateUnit,
  no explicit CONDITIONS relation to the consequent is available and the consequent still
  carries REQUESTED locally.
- Safety finding: this is NOT a closed unconditional semantic interpretation: frame closure
  and semantic closure stay false; downstream stays fail-closed (governance only added).
- Safety: CONTENT_CONSERVED=YES, FALSE_STRONG_RELATION=NO, SILENT_LOSS=NO, FRAME=OPEN,
  FAIL_CLOSED=YES.
- Known limitation: CONSEQUENT_SEMANTICALLY_GATED_BY_RELATION=NO (the marker does not name
  the consequent).
- Future resolution candidate: SENS lexicon for the missing protasis predicate and/or
  Cognition for explicit condition→consequence reconstruction.
- Status: FROZEN_DEFERRED

## D5 — SENS-D5-SOURCE-SCOPE-BEFORE-CONDITIONAL

- Canonical trigger: "Selon Marie, si le script qui teste P échoue, lance R."
- Observed limitation: the source is conserved in unresolved metadata, currently as
  `detached_source_of=u2`; its exact scope over the conditional structure is not
  explicitly disambiguated (the ambiguity is not named).
- The attachment is NOT promoted into unit evidentiality (u2 epistemic stays
  NOT_APPLICABLE); no false provenance is asserted as canonical truth; frame stays open.
- Safety: CONTENT_CONSERVED=YES, FALSE_ACTION=NO, FALSE_RELATION=NO, FALSE_PROVENANCE=NO,
  SILENT_LOSS=NO, FAIL_CLOSED=YES.
- Future resolution candidate: Cognition / context (source scope over the whole
  conditional structure).
- Status: FROZEN_DEFERRED
