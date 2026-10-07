# B7 — Runtime Determinism Contract (V1)

```
STATUS=B7_RUNTIME_CONTRACT_V1 / FROZEN_FOR_IMPLEMENTATION / NO_RUNTIME_CODE
FROZEN_ON=2026-10-07
BASE_HEAD=1767238c
SPECIALIZES=docs/architecture/B7_COGNITIVE_ROLE_SPEC_V1.md (CLOSED, e7e74f01; closure 1767238c)
DECISION_AUTHORITY=KX108_ONLY
```

This annex specializes the CLOSED B7 architecture for deterministic runtime implementation. It
closes the precision items D1–D3 of the B7 spec closure and records items 4–6 for the RED tests.
It does not alter any constitutional decision, role right or boundary of the spec.

Global rules: FREE_TEXT_ROUTING=FORBIDDEN · LLM_CLASSIFICATION=FORBIDDEN · every vocabulary below is
a closed enum; an unknown value is rejected (fail closed), never coerced.

## 1. `candidate_status` (D1) — cognitive lifecycle only

| value | meaning |
|---|---|
| `PROPOSED` | typed proposal emitted by a proposing role (RESOLVER / BUILDER_PROPOSER), not yet normalized by TRANSLATOR |
| `READY_FOR_VALIDATION` | normalized by TRANSLATOR against this contract; the only status the gate examines |

Justification of the second value: it makes the TRANSLATOR step mandatory and testable — a candidate
reaching the gate with `PROPOSED` is REJECTED (bypass of translation). No other value is needed:
candidates are immutable (a new object, not a mutation, carries `READY_FOR_VALIDATION`), and the
outcome of validation is NOT a candidate status.

`candidate_status` is not truth, authority, a validation verdict or a KX108 decision. Forbidden as
values (and anywhere in the vocabulary): ALLOW, HOLD, BLOCK, ACT, EXECUTE, DECIDE, AUTHORIZED,
APPROVED, ACCEPTED, VALID, TRUE.

Validation verdicts stay separate (`CognitiveValidationVerdict`): `ACCEPT_AS_STRUCTURED_CONTEXT`,
`REJECT`, `STILL_UNRESOLVED`.

## 2. `required_candidate_kind` (D2) — shape of the requested answer, never its truth

Exactly 1:1 with `UnresolvedKind` (a 1:1 map is sufficient: each kind asks for one answer shape):

| UnresolvedKind | required_candidate_kind | ACCEPT reachable in V1 |
|---|---|---|
| COREFERENCE | REFERENCE_BINDING | yes (after all gate checks) |
| SOURCE_SCOPE | SOURCE_SCOPE_INTERPRETATION | yes |
| CONDITIONAL_ATTACHMENT | CONDITIONAL_ATTACHMENT_INTERPRETATION | yes |
| TEMPORAL_REFERENCE | TEMPORAL_REFERENCE_INTERPRETATION | yes, linguistic only (§6) |
| DEIXIS | DEICTIC_BINDING | yes |
| ENTITY_IDENTITY | ENTITY_BINDING | yes |
| CONTRADICTION | CONTRADICTION_ANALYSIS | yes as analysis context only; the contradiction stays represented, no winner |
| UNKNOWN_TERM_OR_PREDICATE | TERM_OR_PREDICATE_INTERPRETATION | yes (no lexicon mutation) |
| DOMAIN_SPECIFIC_AMBIGUITY | DOMAIN_INTERPRETATION | yes |
| WORLD_OR_PHYSICAL_REFERENCE | WORLD_REFERENCE_HYPOTHESIS | NO without admissible world / domain evidence → STILL_UNRESOLVED |
| OTHER_EXPLICIT_UNRESOLVED | CHARACTERIZATION_ONLY | NEVER (fail-closed until a type-specific validator exists) |

A candidate whose kind differs from the request's `required_candidate_kind` is REJECTED.

## 3. `forbidden_operations` (D2) — structural restrictions, never a decision

Closed vocabulary: `DECIDE`, `ACT`, `SELF_AUTHORIZE`, `WRITE_DURABLE_MEMORY`, `WRITE_WORKING_STATE`,
`MUTATE_KERNEL`, `MUTATE_ORIGIN_STATE`, `PROMOTE_TO_KNOWLEDGE`, `BYPASS_VALIDATION`,
`SELECT_WINNER`, `PROPOSE_RESOLUTION`, `ESTABLISH_WORLD_FACT`, `ESTABLISH_PHYSICAL_CHRONOLOGY`.

Canonical default set (every request): `DECIDE`, `ACT`, `SELF_AUTHORIZE`, `WRITE_DURABLE_MEMORY`,
`WRITE_WORKING_STATE`, `MUTATE_KERNEL`, `MUTATE_ORIGIN_STATE`, `PROMOTE_TO_KNOWLEDGE`,
`BYPASS_VALIDATION`. (`WRITE_WORKING_STATE` binds roles and providers; the gate's creation of a NEW
entry is not an operation of the cognitive path.)

Additional restrictions by kind (justified by the spec):

| kind | added |
|---|---|
| CONTRADICTION | SELECT_WINNER |
| TEMPORAL_REFERENCE | ESTABLISH_PHYSICAL_CHRONOLOGY |
| WORLD_OR_PHYSICAL_REFERENCE | ESTABLISH_WORLD_FACT, ESTABLISH_PHYSICAL_CHRONOLOGY |
| OTHER_EXPLICIT_UNRESOLVED | PROPOSE_RESOLUTION |

The field lists what the cognitive path is structurally forbidden to do. It is not a KX108 verdict;
ALLOW / HOLD / BLOCK never appear in it.

## 4. Inventory of explicit SENS / B6 unresolved markers (D3, read at 1767238c)

All markers are reachable from a B6 `SENS_FRAME` StateEntry (`app/harness/state_explicit/sens_adapter.py`):
`payload.missing`, `payload.ambiguities`, `payload.unresolved_references`, `payload.contradictions`,
`payload.semantic_closure.reasons`, `payload.semantic_frame.oblique_arguments[*].role`, and the entry
`status` (`KNOWN | OPEN | UNKNOWN | ERROR`).

| source | exact shape | examples |
|---|---|---|
| `unresolved_references` | `"<unit>:<token>"` | `u1:le` |
| `contradictions` | `"<PRED>(<obj>):requested_and_forbidden:<u>/<u>"` | `EXECUTE(p):requested_and_forbidden:u1/u2` |
| `ambiguities` | `"<prefix>:<ids…>"`; prefixes found: `ambiguous_antecedent`, `subject_unresolved`, `coordinated_subject_unrepresented`, `coordination_attachment_ambiguous`, `condition_scope_ambiguous`, `exception_condition_open`, `temporal_scope_ambiguous`, `temporal_subordinate_open`, `occurrence_conflict_open`, `complement_governor_lost`, `complement_structure_lost`, `complement_under_unresolved_governor`, `unresolved_complement_governance`, `infinitive_under_unrecognized_governor`, `bare_ne`, `negated_scope_open`, `know_how_scope_open`, `negated_speech_act_open`, `deontic_scope_open`, `modal_past_occurrence_open`, `question_or_request`, `desire_or_request`, `ability_permission_or_request` | `subject_unresolved:u1`, `occurrence_conflict_open:u1:u2` |
| `missing` | `"unanalyzed_predicative_content:<start>-<end>:<link>[…]"`; links found: `root`, `main_predicate_after_relative_of=<u>`, `main_predicate_unresolved`, `conditional_protasis`, `conditional_protasis_of…`, `conditional_consequent_of=<u>`, `detached_source_of=<u or unresolved…>`, `embedded_under=<u>`, `embedded_under_unresolved_governor`, `governed_by…`, `temporal_subordinate`, `exception_condition`, `wh_complement`, `unattached…` | `…:26-35:root`, `…:0-11:detached_source_of=u2` |
| `semantic_closure.reasons` | `frame:<frame blocker>` (duplicates the frame fields above), `event_reference:<status>:<reason>:<pred>`, `meta_target:<status>:<reason>:<pred>`, `index_conflict:<reason>:<pred>`, `no_predicate_unit` | `frame:unresolved_reference:u1:le` |
| `semantic_frame.oblique_arguments` | `role == "UNRESOLVED"` (frame blocker `oblique_role_unresolved:<id>`) | — |
| frozen D1–D5 | D1 `subject_unresolved:u1` + `missing …main_predicate_after_relative_of=u1`; D2 `missing …main_predicate_unresolved`; D3 `missing …:root` only; D4 `missing …:conditional_protasis`; D5 `missing …:detached_source_of=u2` | — |

Not unresolved markers (never trigger a request): `deixis` (e.g. `maintenant`, `ici` — present data,
the frame can be closed), `constraints` (e.g. `NO_EXECUTE(p)`), `evidence_needs` (truth-value needs,
never block closure by SENS doctrine), `presupposed_referents`, orthography flags.

## 5. Mechanical marker → UnresolvedKind table (D3)

Rules depend only on the exact field and the marker prefix / link token (text before the first `:`
for ambiguities; the link token after `<start>-<end>:` for missing, up to `=` or `:`). No user text
is read. First matching row wins; rows are disjoint.

| # | field | match | UnresolvedKind |
|---|---|---|---|
| M1 | `unresolved_references` | any | COREFERENCE |
| M2 | `ambiguities` | `ambiguous_antecedent` | COREFERENCE |
| M3 | `semantic_closure.reasons` | `event_reference:` | COREFERENCE |
| M4 | `missing` | link `detached_source_of` | SOURCE_SCOPE |
| M5 | `ambiguities` | `condition_scope_ambiguous`, `exception_condition_open` | CONDITIONAL_ATTACHMENT |
| M6 | `ambiguities` | `temporal_scope_ambiguous`, `temporal_subordinate_open` | TEMPORAL_REFERENCE |
| M7 | `contradictions` | any | CONTRADICTION |
| M8 | `ambiguities` | `occurrence_conflict_open` | CONTRADICTION |
| M9 | `ambiguities` | `infinitive_under_unrecognized_governor`, `complement_under_unresolved_governor`, `unresolved_complement_governance` | UNKNOWN_TERM_OR_PREDICATE |
| M10 | any explicit unresolved marker not matched above (all other ambiguity prefixes; all other `missing` links incl. `root`, `conditional_protasis`, `main_predicate_*`, `temporal_subordinate`, `embedded_under*`; `meta_target:`, `index_conflict:`, `no_predicate_unit`; oblique `UNRESOLVED`; any future prefix) | — | OTHER_EXPLICIT_UNRESOLVED |

Deduplication (deterministic, not loss): `semantic_closure.reasons` entries prefixed `frame:` restate
frame fields already read above and are skipped; every other reason is read.

Entry status: a `SENS_FRAME` entry with status `OPEN` but no marker yields one
OTHER_EXPLICIT_UNRESOLVED request with problem_ref `status:OPEN`. A non-SENS entry with status
`UNKNOWN` yields one OTHER_EXPLICIT_UNRESOLVED request. An `ERROR` entry is an operational failure,
not a cognitive problem: no request; it stays visible as B6 unknown state.

Per-family sources:

| UnresolvedKind | current mechanical source |
|---|---|
| COREFERENCE | M1, M2, M3 |
| SOURCE_SCOPE | M4 |
| CONDITIONAL_ATTACHMENT | M5 |
| TEMPORAL_REFERENCE | M6 |
| DEIXIS | NO_CURRENT_MECHANICAL_SOURCE (`deixis` lists anchors, not an unresolved state) |
| ENTITY_IDENTITY | NO_CURRENT_MECHANICAL_SOURCE |
| CONTRADICTION | M7, M8 |
| UNKNOWN_TERM_OR_PREDICATE | M9 |
| DOMAIN_SPECIFIC_AMBIGUITY | NO_CURRENT_MECHANICAL_SOURCE |
| WORLD_OR_PHYSICAL_REFERENCE | NO_CURRENT_MECHANICAL_SOURCE |
| OTHER_EXPLICIT_UNRESOLVED | M10 + status fallbacks |

Categories without a current source stay valid in the ontology for future producers; the initial
detector cannot emit them. Ambiguous markers whose meaning spans several families (e.g.
`subject_unresolved`, `coordination_attachment_ambiguous`, `missing …:conditional_protasis`) are
deliberately OTHER (fail closed) rather than guessed.

Consequence recorded for the spec's normative example (§16 of the spec): "Le script que Paul lance,
il échoue." currently carries only `missing …:root` (D3), so the detector emits
OTHER_EXPLICIT_UNRESOLVED (characterization only, never ACCEPT). A COREFERENCE request for it
requires a future explicit producer; the detector must not guess it. Live COREFERENCE example today:
"Lance-le." (`unresolved_references: ["u1:le"]`).

## 6. Fallback and multiplicity laws

- EXPLICIT_UNRESOLVED + NO_SPECIFIC_MAPPING = OTHER_EXPLICIT_UNRESOLVED → CHARACTERIZATION_ONLY →
  NEVER ACCEPT_AS_STRUCTURED_CONTEXT until a type-specific validator exists. Never ignored, dropped
  or guessed.
- One explicit marker → one `CognitiveResolutionRequest` (`problem_refs` = that single marker).
  Several markers → several requests, ordered deterministically by (field order of §4, marker
  string); none silently lost. `request_id` is derived from (`origin_state_digest`, field, marker),
  so the same state always yields the same requests.

## 7. Temporal distinction

LINGUISTIC_TEMPORAL_REFERENCE != PHYSICAL_CHRONOLOGY. Resolving "hier", "demain", "à ce moment-là"
may produce a contextual linguistic candidate (TEMPORAL_REFERENCE_INTERPRETATION). It must not
establish physical event truth, sensor timestamps, world chronology or causal chronology without
separate admissible world / domain evidence (`ESTABLISH_PHYSICAL_CHRONOLOGY` forbidden, §3).

## 8. Brody: role eligibility != implemented capability

| ROLE | BRODY_ELIGIBLE | BRODY_IMPLEMENTED_NOW (as a B7 role) | EVIDENCE |
|---|---|---|---|
| UNDERSTANDER | YES | NO | understanding / response exists (True Voice, `brody_semantic_plan`, `pre_reasoning_calibrator`) but no B7 role interface over StateEntry |
| INVESTIGATOR | YES | NO | Native Memory readonly retrieval exists (`brody_obsidia_native_memory`), no B7 request-driven interface |
| RESOLVER | YES | NO | no linguistic resolution runtime; only code repair (`brody_repair_reasoning`, UNRESOLVED_NAME), out of scope |
| CRITIC | YES | NO | divergence / mismatch signals exist (C273, `brody_anti_mismatch_signal`), not a candidate critic |
| TRANSLATOR | YES | NO | no B7 candidate translator |
| COMPARATOR | NO (not assigned to Brody by the spec) | NO | — |
| BUILDER_PROPOSER | NO (Obsidure precedent) | NO | — |

No generic B7 linguistic resolution runtime exists yet.

## 9. Runtime RED test manifest (source for the next ticket)

T1 request derived mechanically from an explicit unresolved StateEntry · T2 no SENS reinterpretation
during request creation · T3 router chooses eligible roles only · T4 router cannot choose truth or
action · T5 candidate with authority flags → REJECT · T6 candidate losing unresolved content →
REJECT · T7 candidate hiding a contradiction → REJECT · T8 inventing a participant → REJECT ·
T9 inventing a relation → REJECT · T10 inventing a time or source → REJECT · T11 accepted candidate
→ new working StateEntry · T12 original state unchanged · T13 multiple candidates → no automatic
winner · T14 confidence ≠ truth · T15 no B7 durable-memory write · T16 no ACT / no decision
authority · T17 arbitrary dict never becomes trusted B7 / B6 state · T18 B6-10 hardening path
validated · T19 request_id mismatch → REJECT · T20 origin_state_id mismatch → REJECT ·
T21 original_state_digest mismatch → REJECT · T22 ineligible role → REJECT · T23 ineligible provider
→ REJECT · T24 OTHER_EXPLICIT_UNRESOLVED → never ACCEPT · T25 quoted "ALLOW/HOLD/BLOCK" content ≠
authority · T26 non-strict-JSON candidate → REJECT · T27 oversized candidate → REJECT · T28 invalid
TRANSLATOR output → REJECT · T29 duplicate / double ACCEPT derived state id → fail closed ·
T30 marker mapping deterministic (table §5) · T31 unknown explicit marker → OTHER_EXPLICIT_UNRESOLVED ·
T32 multiple unresolved markers conserved, none silently lost · T33 linguistic temporal resolution ≠
physical chronology.

Determinism-contract additions (same manifest): T34 candidate with `candidate_status=PROPOSED` at the
gate → REJECT · T35 candidate kind ≠ request `required_candidate_kind` → REJECT ·
T36 unknown enum value (status / kind / operation / UnresolvedKind) → REJECT · T37 `ERROR` entry →
no request, entry still visible · T38 `deixis` / `constraints` / `evidence_needs` alone → no request ·
T39 `frame:`-prefixed closure reasons not double-counted · T40 WORLD_REFERENCE_HYPOTHESIS without
admissible evidence → STILL_UNRESOLVED.

## 10. Internal consistency

candidate_status ≠ validation verdict · required_candidate_kind is the explicit 1:1 image of
UnresolvedKind · forbidden_operations ≠ KX108 verdict · classification ≠ resolution ≠ truth ·
OTHER_EXPLICIT_UNRESOLVED cannot reach ACCEPT · no free-text value controls routing or authority ·
memory_write=False, emits_act=False, kernel_mutation=False, decision_authority=KX108_ONLY.
