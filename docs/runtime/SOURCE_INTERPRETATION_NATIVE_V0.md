# SOURCE_INTERPRETATION_NATIVE_V0

Date: 2026-10-07

Branch:
`feat/source-interpretation-native-v0`

Draft PR:
`#76`

Base:
`feat/preforge-enterprise-stack-freeze-v0`

Main merge:
`NO`

## Purpose

Replace the Enterprise Source Sandbox truth manifest as the routing mechanism.

The truth manifest remains a test oracle only.

Canonical flow now proven:

```text
native MAIL / DOCUMENT / CALENDAR connector
→ SOURCE_RUNTIME_NATIVE_V0
→ NativeSourceContextPacketV0
→ SOURCE_INTERPRETATION_NATIVE_V0
→ SourceInterpretationCandidateV0
→ correlation
→ sandbox intake policy
→ NativeCaseTaskIntakePlanV0
→ HumanApproval
→ WORLD_ACTION_PRE_EXECUTION
→ KX108_ONLY
→ CRM_NATIVE_V0 / TASKS_NATIVE_V0
→ receipts / replay
```

## Interpretation contract

Input:

- exact NativeSourceContextPacketV0
- exact NativeSourceRegistrationV0
- ephemeral connector material

The ephemeral raw material is used in memory only.

Output:

`SourceInterpretationCandidateV0`

The candidate binds:

- source packet id/hash
- source id/kind/provider
- registration hash
- material fingerprint
- interpretation kind
- actionability signal
- information-only signal
- deadline candidate
- incident signal
- work identity candidate
- contradiction subject
- directive polarity
- duplicate identity candidate
- unknowns
- evidence gaps
- entity references
- proposed case type
- proposed priority
- proposed title/summary
- occurred_at
- provenance references
- interpreter id/version
- interpretation hash

Authority is fixed:

```text
allowed_to_decide = false
allowed_to_act = false
decision_authority = KX108_ONLY
```

## Supported V0 semantic families

- INFORMATION_ONLY
- ACTION_REQUEST
- ACTION_WITH_DEADLINE
- INCIDENT
- CONSTRAINT
- CALENDAR_CONTEXT
- EVIDENCE_GAP

Unknown material remains explicit unknown/evidence-gap structure.

The interpreter does not silently convert unknown content into executable work.

## Duplicate correlation

Multiple actionable candidates may emit the same
`duplicate_identity_candidate`.

The correlation layer can bind a later candidate to an earlier primary.

In the Enterprise Sandbox:

```text
mail-action-001
mail-action-001-duplicate
→ one work identity
→ second candidate suppressed before canonical apply
```

The interpreter itself does not delete or mutate anything.

## Contradiction correlation

Candidates may emit:

- contradiction_subject
- REQUIRE / FORBID polarity

The correlation layer surfaces a contradiction group when opposing directives
exist for the same subject.

In the Enterprise Sandbox:

```text
approve supplier order SO-77
+
do not approve supplier order SO-77
→ structured contradiction group
→ passed downstream as contradictions
→ KX108 BLOCK
→ 0 canonical mutations
```

The interpreter does not resolve the contradiction.

## Evidence gaps

The incomplete request fixture becomes:

```text
interpretation_kind = EVIDENCE_GAP
unknowns =
  REQUEST_SCOPE_UNKNOWN
  REQUEST_AUTHORITY_UNKNOWN
evidence_gap =
  REFERENCED_PRIOR_CONTEXT_MISSING
```

The sandbox intake runner applies an explicit review-policy due date only for
the proposed clarification workflow. That date is tagged as policy-derived,
not as a source fact.

KX108 receives the unknowns and returns HOLD.

## Truth-oracle-free E2E

The new interpreted runner:

`enterprise_office_interpreted_e2e_v0.py`

does not import or read the sandbox truth manifest.

Observed interpreted result:

- source observations: 12
- source packets: 12
- interpretation candidates: 12
- committed cases: 3
- canonical mutations: 12
- duplicate suppressed: 1
- HOLD: 1
- BLOCK: 1
- information-only: 2
- network calls: 0
- external actions: 0

The test reads the truth manifest only after the run to compare expected and
observed outcomes.

## Raw-material boundary

The canonical source runtime still persists only hashes/provenance.

Interpretation candidates contain structured proposals and fingerprints, not
the raw mail/document/calendar bodies.

The source interpretation module has no dependency on:

- periphery.native_ops
- apply_crm_mutation_v0
- apply_task_mutation_v0
- execute_native_case_task_intake_v0

Therefore the interpreter cannot directly mutate CRM/TASK state.

## Runtime fact

`native_source_interpretation_present=true`

Authority fact:

`source_interpretation_authority=NON_SOVEREIGN_CANDIDATE_ONLY`

This does not change:

- world_action_runtime_activated=false
- runtime_allowed_now=false
- execution_authority=false
- emits_act=false

## Proof

Run:

`37624949649`

Result:

`83 passed in 1.84s`

Coverage includes:

- interpretation contract
- mail/document/calendar semantics
- deterministic candidate hashes
- duplicate correlation
- contradiction correlation
- evidence-gap/unknown behavior
- no native apply dependency
- no raw-material candidate persistence
- interpreted E2E without truth-manifest routing
- old autonomous-office E2E regression
- Enterprise Source Sandbox
- native source connectors
- SOURCE_RUNTIME_NATIVE_V0
- TASKS/CRM native
- WORLD_ACTION PRE

Protected core changes:

`0`

## Verdict

`SOURCE_INTERPRETATION_NATIVE_V0_PROVEN`

## Next unresolved boundary

Do not extend SOURCE_INTERPRETATION_NATIVE_V0 further.

The next missing canonical layer is:

`INTERPRETATION_TO_INTAKE_POLICY_NATIVE_V0`

Why:

The conversion from a non-sovereign interpretation candidate/correlation into
a NativeCaseTaskIntakePlanV0 is currently implemented only inside the
interpreted sandbox E2E runner.

The next layer should extract this conversion into a reusable, non-executing
policy contract, with domain adapters able to calibrate:

- case type
- priority
- owner
- policy-derived review due dates
- information-only routing
- duplicate handling
- contradiction routing
- evidence-gap review routing

It must still not execute the plan and must not replace KX108 authority.
