# B7 V1 Amendment — Structured Referent Only (2026-10-07)

```
STATUS=HUMAN_DOCTRINE_DECISION / B7_V1_AMENDMENT
DECISION=STRUCTURED_REFERENT_ONLY (human option A)
AMENDS=docs/architecture/B7_COGNITIVE_ROLE_SPEC_V1.md §13 check 7 and
       docs/architecture/B7_RUNTIME_DETERMINISM_CONTRACT_V1.md (gate admissibility)
SUPERSEDES=every previous B7 textual referent fallback rule (substring, whole-word, determiner,
           proper-name, SENS-lexicon-assisted)
REASON=each textual heuristic reopened a class of false semantic ACCEPT (B7-G, B7-I, loop audit
       of e416edf6: "le mange", "le script est", ...); no safe textual referent boundary exists
       without a parser. UNRESOLVED > FALSE_ACCEPT.
```

## Laws

- **R1** Raw text may be context or evidence, but it never establishes referent admissibility
  (RAW_TEXT != REFERENT_AUTHORITY).
- **R2** When a structured referent set exists in the origin state, a candidate referent must be
  exactly one of its members (canonical normalization only: Unicode NFC, casefold, word tokens).
- **R3** When no structured referent exists, a candidate referent can never become an ACCEPTed
  referent.
- **R4** Lexicon lookup cannot authorize a raw referent.
- **R5** No parser, NLP or LLM fallback.
- **R6** Absence of an admissible referent yields STILL_UNRESOLVED or REJECT, never a guessed ACCEPT.
- **R7** Any future improvement belongs upstream, in explicit SENS / B6 structure.
- **R8** B7 consumes future structure mechanically and never recreates it.

## Scope

- Referent claims: `antecedent`, `participants`, `sources` of a proposed resolution.
- Structured referents (unchanged extraction): unit subjects, unit object texts (excluding the objects
  of the unit carrying the mention being resolved — the anaphor itself) and coordination member
  texts of `payload.semantic_frame`.
- Not referents (unchanged): linguistic temporal cues (`anchor`, `times`) keep their exact
  token-bounded check and can never establish physical chronology; relation endpoints keep the
  structured unit-id check.
- Unchanged: D-B7-2 exact uncertainty conservation, authority rejection, every other gate check.

## Consequence (accepted)

Sentences whose antecedent SENS does not structure (e.g. copula "Le script est prêt. Lance-le.")
can no longer be resolved by B7: they stay unresolved until SENS / B6 provides structure.
Tests whose ACCEPT relied only on raw text are requalified explicitly (contract amendment, not
weakening).

## Extension — STRUCTURED_TEMPORAL_REFERENCE_ONLY (2026-10-07, same human option-A doctrine)

Found by the B7-L closure audit: textual temporal cues let any raw word pass as a time
(`times: ["script"]`, `anchor: "le script est"`). The textual exception of the "Scope" section above is
withdrawn:

- **T1** `times` and `anchor` become validated content only when exactly supported by the origin
  `semantic_frame.deixis` (SENS runtime shape: list of strings, e.g. `["hier"]`; canonical
  normalization only).
- **T2** Raw-text occurrence is insufficient.
- **T3** No admissible structured temporal / deictic value → REJECT (or STILL_UNRESOLVED where the
  candidate contract says so).
- **T4** B7 never derives temporal structure itself.
- **T5** Physical chronology stays NOT established.

Companion rules (same audit):

- **D1** `quoted_text`, `characterization`, `hypothesis` are strings only; they are descriptive,
  never semantic claims.
- **D2** The derived working state separates `validated` (only gate-validated proposed_resolution
  fields) from `unverified_descriptive` (descriptive strings, evidence_refs, context_refs,
  assumptions, confidence), explicitly marked not truth, not authority, not durable knowledge;
  lineage metadata stays separate from both.

This extends the human option-A doctrine; it does not reopen SENS.
