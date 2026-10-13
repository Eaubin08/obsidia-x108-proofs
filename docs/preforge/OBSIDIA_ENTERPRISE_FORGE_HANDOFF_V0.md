# OBSIDIA ENTERPRISE — FORGE HANDOFF V0

Date: 2026-10-07

Working branch:
`feat/preforge-enterprise-stack-freeze-v0`

Base:
`feat/autonomous-office-e2e-v0`

Merge to main:
`NO`

## 1. Frozen architecture before Forge

```text
Provider / local source
        ↓
Native source connector
        ↓
SOURCE_RUNTIME_NATIVE_V0
        ↓
NativeSourceContextPacketV0
        ↓
[ NEXT FORGE: SOURCE_INTERPRETATION_NATIVE_V0 ]
        ↓
NativeCaseTaskIntakePlanV0
        ↓
HumanApproval
        ↓
WORLD_ACTION_PRE_EXECUTION
        ↓
KX108_ONLY
        ↓
CRM_NATIVE_V0 + TASKS_NATIVE_V0
        ↓
append-only receipts / replay
        ↓
optional WORLD_ACTION provider action
```

Monde Obsidia is a READ_ONLY projection of these canonical objects. It must
never become a second state store or authority.

## 2. Already built and proven

### Native operational state

- TASKS_NATIVE_V0
- CRM_NATIVE_V0
- CRM follow-up -> native task
- exact pre-state binding
- KX108 PRE gate
- append-only receipts
- deterministic replay

Reference proof:
`104/104 PASS`

### Native source runtime

- MAILBOX
- DOCUMENT_REPOSITORY
- CALENDAR
- FORM_INBOX
- API_READONLY
- immutable registration
- append-only revocation
- two-key source onboarding
- privacy-safe observations
- provenance-complete source packets

Reference proof:
`103/103 PASS`

### Native local connectors

- MAIL_NATIVE_CONNECTOR_V0
- DOCUMENT_NATIVE_CONNECTOR_V0
- CALENDAR_NATIVE_CONNECTOR_V0

Local deterministic providers only.

Reference proof:
`93/93 PASS`

### Enterprise digital twin

Synthetic office with:

- information-only mail
- action + deadline
- incident
- contradictory instructions
- duplicate reminder
- missing-evidence request
- contract deadline
- supplier constraint
- reference-only document
- deadline calendar event
- routine calendar event

Status:
`SIMULATED_NOT_OBSERVED`

Reference proof:
`65/65 PASS`

### Autonomous office E2E

Observed result:

- 12 native source observations
- 12 source packets
- 3 canonical cases
- 3 canonical tasks
- 12 canonical native mutations
- 1 duplicate suppressed
- 1 HOLD
- 1 BLOCK
- 2 information-only items
- 0 network calls
- 0 external actions

Reference proof:
`71/71 PASS`

Important:

`SANDBOX_ONLY_NOT_PRODUCTION_INTERPRETER`

The semantic route currently comes from the synthetic truth manifest.

## 3. CSSA role after extraction

CSSA remains a métier reference and conformance domain.

Do not build generic source infrastructure inside CSSA again.

Mapping:

```text
CSSA F3H-D → generic native intake bundle + CRM/TASKS
CSSA F3H-F → native source registry
CSSA F3H-G → native source onboarding
CSSA F3H-E → métier routing reference
```

F3H-E is NOT yet the generic production interpreter.

## 4. Exact next Forge scope

Build:

`SOURCE_INTERPRETATION_NATIVE_V0`

Purpose:

Convert a provenance-complete source packet plus ephemeral connector material
into structured, non-sovereign interpretation candidates.

### Input

Required:

- NativeSourceContextPacketV0
- exact registration/source provenance
- ephemeral material supplied by connector
- provider-neutral metadata

The canonical source runtime still must not persist raw source material.

### Output

Create a contract such as:

`SourceInterpretationCandidateV0`

It should bind at minimum:

- source packet id/hash
- source kind
- interpretation kind
- actionability signal
- information-only signal
- deadline candidate
- incident candidate
- duplicate identity candidate
- contradiction candidates
- missing-evidence / unknown signals
- entity references
- proposed case type
- proposed priority
- provenance references
- interpreter identity/version
- interpretation hash
- KX108_ONLY
- allowed_to_decide=false
- allowed_to_act=false

### Required semantics

The interpreter proposes structure only.

It MUST NOT:

- decide ALLOW/HOLD/BLOCK
- create CRM state directly
- create tasks directly
- send mail
- create calendar events
- mutate files
- call payment/trading/device actions
- mutate KX108/kernel
- silently invent missing facts

### Unknowns

Unknown/ambiguous source material must become explicit unknown/evidence-gap
signals.

Never guess an actionable task merely because a message mentions work.

### Duplicates

Multiple messages/documents referring to the same operational obligation must
be able to converge to one proposed work identity.

Deduplication must remain evidence-bound and reversible before canonical apply.

### Contradictions

Conflicting source material must surface as structured contradictions before
KX108.

Do not resolve contradictions inside the interpreter.

## 5. Forge acceptance tests

Forge is DONE only if all are true:

1. Digital Twin no longer needs truth-manifest routing to choose the
   information/action/deadline/incident/duplicate/HOLD/BLOCK paths.

2. The truth manifest remains only the test oracle used to compare expected
   vs interpreted results.

3. Expected sandbox outcomes stay:

   - 3 committed cases
   - 12 canonical mutations
   - 1 duplicate suppressed
   - 1 HOLD
   - 1 BLOCK
   - 2 information-only
   - 0 external action

4. Source interpretation candidates are deterministic/replayable for the same
   inputs.

5. Raw mail/document/calendar material is not persisted by the canonical
   source runtime.

6. The interpreter cannot call native apply directly.

7. KX108 remains the only decision authority.

8. Existing source runtime, connectors, TASKS/CRM, WORLD_ACTION and replay
   regressions remain green.

9. No protected core file changes.

10. Windows path portability remains green.

## 6. Protected core — do not modify

- sigma/guard.py
- sigma/contracts.py
- sigma/protocols.py
- sigma/aggregation.py
- proofs/lean/
- formal/tla/
- merkle_seal.json

If the Forge thinks one of these must change, stop and produce a BLOCKED
analysis instead of editing it.

## 7. Open-source adoption rule

Open source is allowed for non-differentiating implementation layers.

Required sequence:

```text
license audit
→ security/scope audit
→ adapter to Obsidia contract
→ conformance tests
→ optional component
```

An OSS project must not replace these contracts:

- KX108_ONLY
- WORLD_ACTION
- SOURCE_RUNTIME_NATIVE_V0
- TASKS_NATIVE_V0
- CRM_NATIVE_V0

## 8. Explicitly out of scope for next Forge

- real CSSA mailbox
- real CSSA Drive
- production provider credentials
- real mail send
- payments
- real trading
- physical-device actuation
- main merge

## 9. Expected output from next Forge

The Forge should return:

1. implementation branch only;
2. manifest of files added/changed;
3. exact interpretation contracts;
4. deterministic fixture corpus;
5. conformance matrix across mail/document/calendar;
6. E2E results against Enterprise Source Sandbox;
7. HOLD/BLOCK/duplicate/unknown evidence;
8. proof that raw material is not canonically persisted;
9. protected-file diff = 0;
10. final receipt and next unresolved boundary.

## 10. Stop condition

Do not expand scope after SOURCE_INTERPRETATION_NATIVE_V0 passes.

Freeze, document, and return the next unresolved boundary.
