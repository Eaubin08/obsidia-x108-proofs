# INTERPRETATION_TO_INTAKE_POLICY_NATIVE_V0

Date: 2026-10-07

Branch:
`feat/interpretation-to-intake-policy-native-v0`

Base:
`feat/source-interpretation-native-v0`

## Purpose

Extract the reusable conversion between non-sovereign
`SourceInterpretationCandidateV0` objects and governed
`NativeCaseTaskIntakePlanV0` proposals.

The E2E runner no longer owns intake conversion semantics.

## Canonical flow

```text
SourceInterpretationCandidateV0
        +
SourceInterpretationCorrelationV0
        ↓
INTERPRETATION_TO_INTAKE_POLICY_NATIVE_V0
        ↓
InterpretationToIntakeInstructionV0
        ↓
NativeCaseTaskIntakePlanV0 (when work/review is proposed)
        ↓
human approval
        ↓
WORLD_ACTION_PRE
        ↓
KX108
        ↓
native CRM/TASK apply
```

## Policy dispositions

- `INFORMATION_ONLY`
- `CONSTRAINT_CONTEXT`
- `CALENDAR_CONTEXT`
- `DUPLICATE_SUPPRESSED`
- `CONTRADICTION_REVIEW`
- `CONTRADICTION_MEMBER_CONTEXT`
- `EVIDENCE_GAP_REVIEW`
- `EVIDENCE_GAP_CONTEXT`
- `ACTION_PLAN`
- `ACTION_REVIEW_REQUIRED`
- `CONTEXT_ONLY`

## Provenance and epistemic boundaries

The policy preserves the interpretation hash and correlation evidence.

Deadline provenance is explicit:

- `CANDIDATE`: the intake policy received the deadline from the interpretation candidate.
- `INTAKE_REVIEW_POLICY`: the intake policy itself created a review deadline.
- `NONE`: no deadline is asserted by this layer.

The V0 deliberately does **not** relabel every candidate deadline as a raw source fact,
because some interpretation candidates may already contain deterministic interpreter
policy derivations.

Owner handling is fail-closed:

- no owner input → `owner_ref=None` + `OWNER_UNASSIGNED`
- explicit policy input → `EXPLICIT_POLICY_INPUT`

The policy never invents an owner.

## Duplicate / contradiction / evidence-gap behavior

- duplicate correlation → no second plan
- contradiction → one review plan binds all member interpretation hashes and correlation evidence
- contradiction is passed to KX108 as explicit contradiction input; it is not silently resolved
- evidence gap with unknowns → review plan + unknowns passed to KX108
- evidence gap without actionable unknowns → context only
- actionable interpretation without a deadline → review-required disposition, no fabricated due date

## Authority

```ini
allowed_to_decide = false
allowed_to_act = false
decision_authority = KX108_ONLY
```

The policy module does not import or call:

- `execute_native_case_task_intake_v0`
- `apply_crm_mutation_v0`
- `apply_task_mutation_v0`

Execution remains downstream.

## Contract integrity

Every `InterpretationToIntakeInstructionV0` carries:

- candidate id + interpretation hash
- disposition
- group key
- optional plan hash
- gate unknowns / contradictions
- deadline origin
- owner origin
- policy evidence refs
- policy id/version
- deterministic policy hash

The batch is also deterministically hashed and independently verified.

Tampered authority or hashes are rejected.

## Digital Twin proof

The existing 12-source Digital Twin still produces:

```text
12 source observations
12 source packets
12 interpretation candidates
12 intake-policy instructions

3 committed CASE
3 TASKS
12 canonical mutations

1 duplicate suppressed
1 HOLD
1 BLOCK
2 information-only

0 network calls
0 external actions
```

The truth manifest remains test oracle only and is not used for routing.

## Functional proof

Workflow run:
`37627121414`

Result:
`91 passed in 1.60s`

## Protected boundary

No kernel contract or protected core file is required by this component.

`KX108_ONLY` remains unchanged.
