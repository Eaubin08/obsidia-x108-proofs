# NATIVE TASKS + CRM V0

Date: 2026-10-07

Branch:
`feat/native-tasks-crm-v0`

Base:
`feat/world-action-gmail-draft-adapter-v0`

Draft PR:
`#67`

Main mutation:
`NO`

## Decision

TASKS and CRM are now owned by the Obsidia stack.

External SaaS products are optional adapters only.

```text
OBSIDIA TASKS = canonical source of truth
OBSIDIA CRM   = canonical source of truth

monday / HubSpot / Asana / Salesforce / etc.
= optional projection + transport
= never decision authority
= never canonical state by default
```

## Common governed mutation chain

Every native mutation follows:

```text
native mutation
→ exact mutation_hash
→ exact expected pre-state hash
→ internal WORLD_ACTION request
→ explicit HumanApproval
→ WORLD_ACTION_PRE_EXECUTION
→ real GuardX108
→ immutable KX108 decision record
→ ALLOW only
→ native apply
→ append-only receipt
→ replay
```

A KX108 HOLD or BLOCK never reaches native apply.

A state change after PRE invalidates the mutation through the pre-state hash.

Decision authority stays:

`KX108_ONLY`

## TASKS_NATIVE_V0

Canonical task fields include:

- task id
- title
- description
- status
- priority
- assignee ref
- due date
- dependency ids
- tags
- created / updated time
- version

States:

```text
TODO
IN_PROGRESS
BLOCKED
DONE
CANCELLED
```

DONE and CANCELLED are terminal in V0.

Operations:

- CREATE_TASK
- UPDATE_TASK
- ASSIGN_TASK
- SET_STATUS
- SET_DUE_AT
- ADD_DEPENDENCY
- REMOVE_DEPENDENCY
- ADD_TAG
- REMOVE_TAG

Dependencies must refer to an existing native task.

Self-dependencies are forbidden.

Every mutation emits a replayable append-only receipt binding:

- mutation hash
- request hash
- KX108 record id/hash
- before-state hash
- after-state hash
- before/after state
- version
- receipt hash

## CRM_NATIVE_V0

Canonical CRM record types:

- PERSON
- ORGANIZATION
- CASE

Additional native entity kinds:

- relationship
- interaction
- followup

### Records

Records support:

- fields
- owner
- lifecycle status
- tags
- versioned state
- receipts/replay

Secret-like fields such as password/token/API-key/private-key credentials are
rejected before KX108.

### Relationships

Relationships bind two existing CRM records.

Dangling relationships are rejected.

### Interactions

Interactions are append-only observations linked to one CRM record.

Types include:

- NOTE
- EMAIL
- CALL
- MEETING
- FORM
- SYSTEM_EVENT

### Follow-ups

Follow-ups can bind directly to a native task:

```text
CRM followup
   └── task_ref
          ↓
TASKS_NATIVE_V0
```

The linked task must exist.

Follow-up states:

- OPEN
- DONE
- CANCELLED

### Timeline

`crm_timeline_v0` reconstructs the record timeline from:

- record mutations
- relationships
- interactions
- follow-ups

## External sync boundary

Provider-neutral read-only projections now exist:

- NATIVE_TASK_EXTERNAL_SYNC_PROJECTION_V0
- NATIVE_CRM_EXTERNAL_SYNC_PROJECTION_V0

A projection binds:

- source native domain
- source entity id
- exact native state hash
- provider-neutral payload

and explicitly carries:

```text
allowed_to_decide = false
allowed_to_act = false
decision_authority = KX108_ONLY
```

Therefore adding an external task/CRM provider later does not change the
canonical native model.

## Runtime fact

The runtime now exposes:

`native_tasks_crm_domains_present=true`

This does not activate any SaaS or external world execution.

## Proof

Initial complete proof:

```text
104 / 104 PASS
run 37608832419
0.66 s
```

Coverage includes:

- real KX108 PRE records
- TASK create/assign/progress/done
- task dependencies
- task terminal immutability
- stale pre-state rejection
- KX108 HOLD/BLOCK no-apply
- CRM record creation
- relationships
- interactions
- follow-ups
- CRM followup → native task link
- CRM timeline
- secret-field rejection
- dangling relation rejection
- replay
- provider-neutral projections
- runtime facts
- prior WORLD_ACTION / Calendar / Gmail regressions

Protected core changes:

`0`

## Verdict

`NATIVE_TASKS_CRM_CANONICAL_V0_PROVEN`

## Next

Do not integrate a SaaS by default.

Next useful step is to expose these native domains to the Obsidia/Monde UI and
to the CSSA domain adapters:

```text
CSSA case
→ native CRM record / interaction
→ native task / follow-up
→ KX108-governed mutation
→ optional Calendar/Gmail external action
```

External TASKS/CRM providers may be added later only as optional adapters.
