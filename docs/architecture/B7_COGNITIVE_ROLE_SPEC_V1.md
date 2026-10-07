# B7 — Cognitive Role Spec + Resolution Funnel (V1)

```
STATUS=B7_SPEC_V1 / FROZEN_ARCHITECTURE / NO_RUNTIME_IMPLEMENTATION
FROZEN_ON=2026-10-07
BASE_HEAD=19925074 (SENS CLOSED at 093c90ac, B6 CLOSED at 19925074)
FORENSIC_BASIS=B7-A audit (READY_FOR_B7_SPEC)
DECISION_AUTHORITY=KX108_ONLY
```

B7 defines **who may cognitively do what** with explicit working state, and the mandatory funnel
for explicitly unresolved state. B7 does **not** define who may authorize action.

## 1. Constitutional laws

- COGNITION != AUTHORITY
- PROPOSAL != DECISION
- RESOLUTION_CANDIDATE != TRUTH
- CAPABILITY != PERMISSION; PERMISSION != AUTHORITY
- LLM_OUTPUT != CANONICAL_STATE
- UNRESOLVED → ESCALATE, NEVER GUESS
- ROLE != PROVIDER
- KX108_ONLY: every B7 element is compatible with `memory_write=False`, `emits_act=False`,
  `kernel_mutation=False`, `allowed_to_decide=False`, `allowed_to_act=False`.

## 2. Position in the stack

```
INPUT → SENS → B6 State-Explicit Harness → B7 Cognitive Role / Resolution → (B8 Knowledge Promotion) → (B9 Cognitive Path History)
```

- SENS parses and represents (closed; never rewritten by B7).
- B6 transports explicit working state (`app/harness/state_explicit`, closed).
- B7 investigates explicitly unresolved state and produces candidates; only its validation gate
  may derive new working context.
- B8 governs promotion into durable knowledge. B9 records reasoning / path history.
- B7 MUST NOT absorb B8 or B9.

## 3. Relation to the six existing role systems

| # | Existing system | Relation to B7 | Rule |
|---|---|---|---|
| 1 | CG9 provider governance (`docs/CG9_*`, `scripts/kernel/kx108_proof_agent_*`) | ADJACENT / REUSE | CG9 governs provider identity, execution, receipts, capability/authority boundary; B7 governs role semantics. A role is fulfilled by an eligible provider governed by CG9. |
| 2 | `periphery/agent_registry.py` (`AGENT_REGISTRY`; `periphery/modules_agents/agent_registry.py` is an identical duplicate, do not use) | OUTSIDE B7 ROUTING | These agents evaluate ActionCandidate / domain concerns; never a B7 role registry. |
| 3 | `periphery/agents/v4_roles/*` | LEGACY / DOC REFERENCE ONLY | Authority-adjacent roles (e.g. Sentinelle "recommends HOLD/BLOCK") are not imported. |
| 4 | `docs/freeze/BRODY_COGNITIVE_MODULE_RESOLUTION_TABLE.json` | MAPPABLE PROVIDER-INTERNAL CAPABILITIES | May inform which Brody capabilities satisfy a role; not the B7 role ontology. |
| 5 | `periphery/agents/obsidure_reasoning_provider.py` registry | DOMAIN BUILDER/PROPOSER PRECEDENT | Request → Diagnosis → Proposal → Validation pattern reused conceptually; repair-domain types not reused. |
| 6 | `apps/obsidia_api/brody_rights_authority_matrix.py` | REUSE AS PROVIDER CAPABILITY SOURCE | Capability truth is not duplicated. |

Also reused: `runtime_contracts/cognitive_advisory_spec` (F07) as safety boundary precedent
(§22); `review_join_v1` for JOIN != RESOLVE (§17); B6 `StateEntry` / `canonical_json` /
`BOUNDARY` for state, strict JSON and digests.

Name rule: B7 never defines a type named `ResolutionStatus` (already defined in
`app/semantic/resolution_status.py` and `app/semantic/lattice/event_coreference.py`).

## 4. Canonical roles

All roles: MAY_WRITE_DURABLE_MEMORY=NO, MAY_DECIDE=NO, MAY_ACT=NO, AUTHORITY=NONE,
MAY_WRITE_WORKING_STATE=NO.

- **UNDERSTANDER** — interprets / contextualizes an explicit working state. Reads ContextPacket and
  StateEntry; produces non-canonical interpretation notes. Never resolves as truth. → RESOLVER / INVESTIGATOR.
- **INVESTIGATOR** — collects bounded evidence / context for a request. Reads working context,
  Native Memory READ_ONLY, allowed domain evidence READ_ONLY; produces evidence / context refs and
  findings. Never chooses truth. → RESOLVER.
- **RESOLVER** — produces one or more `CognitiveResolutionCandidate`. Interprets evidence, proposes.
  Never declares canonical truth, never writes the source SENS frame. → VALIDATION_GATE.
- **CRITIC** — attempts falsification; produces objections, contradictions, remaining unknowns.
  Never selects a winner. → VALIDATION_GATE / COMPARATOR.
- **TRANSLATOR** — turns raw provider output into the typed candidate contract (syntax / schema,
  normalization). Never invents semantics, resolves ambiguity or grants authority. Invalid → REJECT.
- **COMPARATOR** — juxtaposes surviving candidates, evidence and contradictions (JOIN != RESOLVE).
  Never selects by model confidence; no deterministic basis → STILL_UNRESOLVED.
- **BUILDER_PROPOSER** — constructs domain / code / artifact candidates (current precedent:
  Obsidure). Domain-specific; never the default linguistic resolver. Proposes, never decides.

The **Validation / Retranslation Gate** (§15) is not a role: it is a non-sovereign deterministic
check and the only element allowed to emit a NEW validated working StateEntry.

## 5. Role matrix (frozen)

| ROLE_ID | PURPOSE | INPUT | OUTPUT | READ_CONTEXT | READ_MEMORY | QUERY_DOMAIN | PROPOSE_RESOLUTION | WRITE_WORKING_STATE | WRITE_DURABLE_MEMORY | DECIDE | ACT | AUTHORITY | NEXT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UNDERSTANDER | interpret | StateEntry, ContextPacket | interpretation note | YES | NO | NO | NO | NO | NO | NO | NO | NONE | RESOLVER / INVESTIGATOR |
| INVESTIGATOR | gather evidence | CognitiveResolutionRequest | evidence / context refs | YES | READ_ONLY | READ_ONLY | NO | NO | NO | NO | NO | NONE | RESOLVER |
| RESOLVER | propose | request + evidence | candidate(s) | YES | READ_ONLY | READ_ONLY | YES | NO | NO | NO | NO | NONE | VALIDATION_GATE |
| CRITIC | falsify | candidates + evidence | objections, contradictions | YES | READ_ONLY | READ_ONLY | NO | NO | NO | NO | NO | NONE | VALIDATION_GATE / COMPARATOR |
| TRANSLATOR | typed conversion | raw provider output | typed candidate or REJECT | NO | NO | NO | NO | NO | NO | NO | NO | NONE | VALIDATION_GATE |
| COMPARATOR | juxtapose | candidate set | joined view | YES | NO | NO | NO | NO | NO | NO | NO | NONE | STILL_UNRESOLVED / gate |
| BUILDER_PROPOSER | domain construction | domain request | domain proposal | YES | NO | READ_ONLY | YES (domain) | NO | NO | NO | NO | NONE | VALIDATION_GATE |
| *VALIDATION_GATE (not a role)* | check candidate | candidate + request + origin | verdict; NEW working StateEntry on ACCEPT | NO | NO | NO | NO | NEW ENTRY ONLY | NO | NO | NO | NONE | working state / unresolved |

## 6. Canonical resolution funnel

```
SENS
 → B6 StateEntry
 → mechanical unresolved detector
 → CognitiveResolutionRequest
 → Cognitive Role Router (unresolved_kind → eligible role ids)
 → eligible cognitive provider(s), governed by CG9
 → CognitiveResolutionCandidate(s)
 → Cognitive Validation / Retranslation Gate
 → ACCEPT_AS_STRUCTURED_CONTEXT → NEW B6-compatible working StateEntry
   | REJECT
   | STILL_UNRESOLVED
 → (B8 only through a separately justified future knowledge-promotion process)
```

Funnel invariants:

- ORIGINAL_UNRESOLVED_STATE_IS_IMMUTABLE
- RESOLUTION_CANDIDATE != ORIGINAL_STATE; RESOLUTION_CANDIDATE != TRUTH
- ACCEPTED_CONTEXT != DURABLE_KNOWLEDGE
- CONFIDENCE != TRUTH; RECOMMENDATION != PERMISSION; COGNITIVE_PROVIDER != AUTHORITY
- NO COGNITIVE OUTPUT ENTERS TRUSTED WORKING STATE WITHOUT TYPED VALIDATION

## 7. Mechanical unresolved detector

Derives a resolution need only from explicit B6 / SENS state: `StateStatus.OPEN` / `UNKNOWN`,
`ambiguities`, `missing`, `unresolved_references`, `contradictions`, semantic-closure reasons,
frozen deferred markers (D1–D5) and other explicit canonical unresolved fields of
`payload.semantic_frame`. No LLM, no guessing, no reparsing. Output: nothing, or one typed
`CognitiveResolutionRequest` per explicit problem.

## 8. CognitiveResolutionRequest (minimum fields)

`request_id`, `origin_state_id`, `origin_state_type`, `unresolved_kind`, `problem_refs` (the exact
marker strings / field paths that triggered it), `source_refs`, `provenance_refs`, `context_refs`,
`allowed_role_ids`, `forbidden_operations`, `required_candidate_kind`, `uncertainty`,
`why_resolution_needed`, `original_state_digest` (B6 `content_digest`).

Mechanically derivable from a B6 StateEntry; no semantic reinterpretation at creation. Strict JSON,
bounded, immutable.

## 9. UnresolvedKind (closed V1 vocabulary)

`COREFERENCE`, `SOURCE_SCOPE`, `CONDITIONAL_ATTACHMENT`, `TEMPORAL_REFERENCE`, `DEIXIS`,
`ENTITY_IDENTITY`, `CONTRADICTION`, `UNKNOWN_TERM_OR_PREDICATE`, `DOMAIN_SPECIFIC_AMBIGUITY`,
`WORLD_OR_PHYSICAL_REFERENCE`, `OTHER_EXPLICIT_UNRESOLVED`.

`OTHER_EXPLICIT_UNRESOLVED` is fail-closed: no automatic routing beyond UNDERSTANDER + CRITIC and
no ACCEPT without an explicit kind-specific check. Free text never acquires routing authority.

## 10. CognitiveResolutionCandidate (minimum fields)

`candidate_id`, `request_id`, `origin_state_id`, `proposer_role`, `provider_ref`,
`proposed_resolution`, `evidence_refs`, `context_refs`, `provenance_refs`, `confidence_class`,
`remaining_unknowns`, `contradictions`, `assumptions`, `candidate_status`, `candidate_digest`.

Immutable, non-sovereign, strict JSON, bounded. Forbidden authority fields: `emits_act`,
`memory_write`, `kernel_mutation`, `allowed_to_act`, `allowed_to_decide`, `decision_authority`.
No provider-supplied value can override this constitution.

## 11. Confidence

`confidence_class ∈ {LOW, MEDIUM, HIGH, UNKNOWN}` — descriptive only.
CONFIDENCE IS ADVISORY ONLY; HIGH != TRUE; LOW != FALSE. Multiple candidates are never resolved by
choosing the highest confidence. Calibration belongs to a later block.

## 12. Role router (B7 V1 role eligibility, not provider binding)

The router maps `unresolved_kind → eligible ROLE ids`, never to truth, action or a sovereign
provider. Provider selection / execution remains constrained by CG9 and capability policy.

| unresolved_kind | eligible roles |
|---|---|
| COREFERENCE | UNDERSTANDER, RESOLVER, CRITIC |
| SOURCE_SCOPE | UNDERSTANDER, RESOLVER, CRITIC |
| CONDITIONAL_ATTACHMENT | UNDERSTANDER, RESOLVER, CRITIC |
| TEMPORAL_REFERENCE | UNDERSTANDER, RESOLVER, CRITIC |
| DEIXIS | UNDERSTANDER, INVESTIGATOR, RESOLVER |
| ENTITY_IDENTITY | INVESTIGATOR, RESOLVER, CRITIC |
| CONTRADICTION | CRITIC, COMPARATOR |
| UNKNOWN_TERM_OR_PREDICATE | UNDERSTANDER, INVESTIGATOR, RESOLVER |
| DOMAIN_SPECIFIC_AMBIGUITY | INVESTIGATOR, BUILDER_PROPOSER, CRITIC |
| WORLD_OR_PHYSICAL_REFERENCE | INVESTIGATOR (domain / world evidence) — stays unresolved unless admissible evidence exists |
| OTHER_EXPLICIT_UNRESOLVED | UNDERSTANDER, CRITIC (fail-closed) |

TRANSLATOR applies to every provider output before the gate; COMPARATOR applies whenever more than
one candidate survives.

## 13. Validation / Retranslation Gate (non-sovereign)

Verdicts: `ACCEPT_AS_STRUCTURED_CONTEXT`, `REJECT`, `STILL_UNRESOLVED`.
Forbidden verdicts: ALLOW, HOLD, BLOCK, ACT, EXECUTE, DECIDE.

Minimum checks (any failure → REJECT, or STILL_UNRESOLVED when the candidate is valid but not
sufficient):

1. `request_id` matches the active request; `origin_state_id` matches; `original_state_digest` matches.
2. Candidate schema valid; strict JSON; bounded; serializable.
3. `proposer_role` eligible for the `unresolved_kind`; provider eligible for that role (CG9 / capability).
4. Source / provenance refs conserved.
5. No unresolved item silently erased; `remaining_unknowns` explicit.
6. No contradiction hidden.
7. No unsupported participant, relation, time or source invented.
8. No authority field accepted (§20).

## 14. Accepted candidate output

ACCEPT creates a NEW working StateEntry (never a mutation of the origin), linking:
`derived_from_state_id`, `resolution_request_id`, `resolution_candidate_id`, `provider_ref`,
`role_ref`, evidence / provenance refs, validation result, remaining uncertainty. Its status stays
bounded (not KNOWN by default when unknowns remain). Accepted structured context is NOT semantic
truth, observation, world truth, durable memory, knowledge or authority.

## 15. Multiple candidates

Surviving candidates are joined, never ranked into a winner (JOIN != RESOLVE, ReviewJoin
principle). Without a deterministic basis the result is STILL_UNRESOLVED and the candidate set
stays explicit. Future calibration may assist later; B7 V1 does not invent it.

## 16. Normative example — coreference (D3)

Utterance: "Le script que Paul lance, il échoue." — SENS / B6 keep the coreference unresolved
(SENS-D3, FROZEN_DEFERRED).

- Request: `unresolved_kind=COREFERENCE`; problem = referent of "il"; `origin_state_id` = the
  B6 SENS_FRAME entry; `original_state_digest` = its content digest; allowed roles UNDERSTANDER,
  RESOLVER, CRITIC.
- Candidate: "il" → "le script"; `proposer_role=RESOLVER`; `provider_ref` = the CG9-governed
  provider; evidence refs (relative-clause antecedent position, agreement); `confidence_class`;
  `remaining_unknowns` (e.g. "Paul" not formally excluded); assumptions listed.
- Gate: checks the candidate answers the original question, no source meaning disappears, no
  authority is introduced, the original SENS frame is unchanged.
- ACCEPT → one new derived working StateEntry only. The candidate is not truth and cannot authorize.

## 17. Resolution family boundaries

- COREFERENCE, SOURCE_SCOPE, CONDITIONAL_ATTACHMENT, DEIXIS, TEMPORAL_REFERENCE → linguistic /
  context cognition.
- ENTITY_IDENTITY → context + Native Memory READ_ONLY where available.
- CONTRADICTION → CRITIC + COMPARATOR / ReviewJoin; no automatic winner.
- UNKNOWN_TERM_OR_PREDICATE → linguistic / context investigation; lexicon mutation is NOT B7.
- DOMAIN_SPECIFIC_AMBIGUITY → eligible domain translator / builder.
- WORLD_OR_PHYSICAL_REFERENCE → domain / world evidence path; B7 cannot manufacture physical truth.

## 18. Providers

- **Brody** — PROVIDER: COGNITIVE_ADVISORY. Eligible roles: UNDERSTANDER, INVESTIGATOR, RESOLVER,
  CRITIC, TRANSLATOR, subject to actual capability availability. May understand, contextualize,
  inspect readonly context, propose, critique. Never canonical truth writer, never durable-memory
  promoter, never authorizes, never ACTs, never changes KX108, never silently rewrites SENS.
- **Obsidure** — provider / BUILDER_PROPOSER for domain construction. Its repair flow (Request →
  Diagnosis → Proposal → Validation) is architectural precedent; its repair-domain contracts are
  not imported into generic B7. Not a linguistic resolver by default.

## 19. F07 cognitive advisory

REUSE AS SAFETY BOUNDARY / PRECEDENT: F07 already routes cognitive output to bounded candidate
context with forbidden action / authority uses and fail-closed handling. B7 extends that principle
to explicit unresolved-state resolution without duplicating F07 restrictions.

## 20. Security invariants

A candidate carrying any of `emits_act=True`, `memory_write=True`, `kernel_mutation=True`,
`decision_authority≠KX108_ONLY` (e.g. `SELF`), `allowed_to_act=True`, `allowed_to_decide=True` is
REJECTED. A candidate cannot grant itself authority. Provider text such as "ALLOW", "HOLD",
"BLOCK", "ACT" may exist only as quoted / descriptive content and never becomes gate authority.

## 21. B6-10

B6-10 remains FROZEN_DEFERRED. B7 closes the DESIGN gap (typed candidate + typed gate). Runtime
closure requires a later small change: `run_brody_real_response_pipeline` must stop accepting an
arbitrary mapping as `state_context_packet` before any consumer interprets it semantically.
Law: ARBITRARY_DICT != TRUSTED_CONTEXT — only a validated B6 / B7 typed packet may enter trusted
state. B6 is not modified by this spec.

## 22. B7 vs B8 / B9

- B7 output = candidates and validated working context. B8 = knowledge promotion state machine.
  B7 never writes durable memory, marks knowledge durable, promotes belief to knowledge, bypasses
  a human validation that B8 may require, or uses memory-promotion guards
  (`brody_memory_promotion_guard`, `brody_memory_human_validation_gate`, …) as decision authority.
- B7 carries only minimal trace refs: `request_id`, `candidate_id`, `proposer_role`,
  `provider_ref`. No CognitivePath, FailedPath or PathHistory (B9).

## 23. Primitives

B7-native V1: `CognitiveResolutionRequest`, `CognitiveResolutionCandidate`, `CognitiveRoleRef`,
`UnresolvedKind`, `CognitiveValidationVerdict`.
Deferred to Common Cognitive Primitives / later blocks: generalized `EvidenceRef`, `ContextRef`,
`ConfidenceScale`, `PathRef`, history. V1 reuses B6 `source_ref` / provenance identifiers.

## 24. Non-goals

Runtime cognitive execution, full provider selection, memory promotion, durable memory, world model,
calibration, model ranking, learning, self-build, CognitivePath / FailedPath / PathHistory, action
governance, KX108 changes, SENS changes, B6 changes.

## 25. Required future test contracts

- T1 request derived mechanically from an explicit unresolved StateEntry.
- T2 no SENS reinterpretation during request creation.
- T3 router chooses eligible roles only.
- T4 router cannot choose truth or action.
- T5 candidate with authority flags → REJECT.
- T6 candidate losing unresolved content → REJECT.
- T7 candidate hiding a contradiction → REJECT.
- T8 candidate inventing a participant → REJECT.
- T9 candidate inventing a relation → REJECT.
- T10 candidate inventing a time or source → REJECT.
- T11 accepted candidate → new working StateEntry.
- T12 original state unchanged.
- T13 multiple candidates → no automatic winner.
- T14 confidence ≠ truth.
- T15 no B7 durable-memory write.
- T16 no ACT, no decision authority.
- T17 arbitrary dict never becomes trusted B7 / B6 state.
- T18 B6-10 hardening path validated.

## 26. Decisions

- DECISION_B7_01: B7 defines cognitive roles, not providers.
- DECISION_B7_02: CG9 remains provider governance.
- DECISION_B7_03: the Resolution Funnel is canonical.
- DECISION_B7_04: unresolved state escalates; B7 never guesses silently.
- DECISION_B7_05: candidates are non-canonical until validation.
- DECISION_B7_06: validation produces structured working context, not truth.
- DECISION_B7_07: original SENS / B6 state is immutable.
- DECISION_B7_08: multiple surviving candidates remain unresolved.
- DECISION_B7_09: B8 owns durable knowledge promotion.
- DECISION_B7_10: KX108 remains the only decision authority.

## 27. Freeze self-audit

No role with DECIDE=YES; no role with ACT=YES; no durable-memory write anywhere; no direct SENS
rewrite (ACCEPT creates a new entry); no trust of an arbitrary B6 mapping (§21); no B8 promotion
rule; no B9 history. Only the non-sovereign gate may emit a new working StateEntry.
