# NATIVE_WORK_TO_ACTION_PROJECTION_V0

Date: 2026-10-07

Branch:
`feat/native-work-to-action-projection-v0`

Base:
`feat/interpretation-to-intake-policy-native-v0`

## Purpose

Connect canonical native work state to the existing universal action-governance
rail without creating a second action model.

The contract reads bound native CRM/TASK/FOLLOW-UP state and produces either:

- the existing `periphery.common.ActionCandidate`, or
- explicit `NO_ACTION`.

It may then bind an existing `ActionCandidate` to the canonical
`UNIVERSAL_WORLD_ACTION_REQUEST_V0` shape when explicit target/infrastructure
binding is supplied.

It never approves, decides, executes, or emits ACT.

## Flow

```text
CRM CASE
+ TASK
+ FOLLOW-UP
        ↓
NATIVE_WORK_TO_ACTION_PROJECTION_V0
        ↓
ACTION_CANDIDATE
or
NO_ACTION
        ↓
explicit target binding
        ↓
UNIVERSAL_WORLD_ACTION_REQUEST_V0
        ↓
HumanApproval
        ↓
WORLD_ACTION_PRE
        ↓
KX108
```

Execution is out of scope for this Forge.

## Native binding

A projection requires all three canonical objects:

- CASE
- TASK
- FOLLOW-UP

The FOLLOW-UP must bind exactly:

```text
followup.record_id == case_id
followup.task_ref   == task_id
followup.due_at     == task.due_at
```

The projection binds the SHA-256 state hashes of all three objects.

## V0 policy

### Calendar candidates

The following proven work classes may produce a calendar action candidate when
a due date exists:

- `ACTION_WITH_DEADLINE`
- `CONTRACT_DEADLINE`

The existing `ActionCandidate` contract is reused.

Projected action:

```text
action_type = CALENDAR_CREATE_EVENT
surface_id  = CALENDAR
operation   = CREATE_EVENT
irreversible = false
```

### Incident

`INCIDENT` produces:

```text
NO_ACTION
reason = EXTERNAL_ACTION_SURFACE_NOT_PROVEN
```

The existence of a case/task does not prove that email, calendar, device, or
another external surface should be called.

### Mail

No MAIL draft/send action is produced in V0 because native work currently does
not carry a structurally proven recipient + message body.

No recipient or body is invented.

## ActionCandidate → WORLD_ACTION

`build_world_action_request_from_action_candidate_v0` binds the existing
ActionCandidate to the canonical WORLD_ACTION request only when the caller
supplies explicit:

- connector id/action
- connector args
- target ref
- exact target prestate hash
- required scope
- effect class
- world-call class
- risk class / autonomy level

The adapter is verified with
`verify_world_action_request_mapping`.

## Authority

```ini
allowed_to_decide = false
allowed_to_act = false
emits_act = false
decision_authority = KX108_ONLY
```

The module does not import or call:

- native CRM/TASK apply
- LiveSovereignTicket
- bounded connector executor

## Digital Twin proof

The upstream interpreted office still produces:

```text
12 source observations
12 source packets
12 interpretation candidates
12 intake-policy instructions
3 committed CASE
3 TASKS
12 canonical mutations
```

Those 3 committed work bundles project as:

```text
mail-action-001
→ ACTION_CANDIDATE / CALENDAR_CREATE_EVENT

contract-renewal.md
→ ACTION_CANDIDATE / CALENDAR_CREATE_EVENT

mail-incident-001
→ NO_ACTION / EXTERNAL_ACTION_SURFACE_NOT_PROVEN
```

No MAIL action is fabricated.

## WORLD_ACTION_PRE proof

The two calendar ActionCandidates are bound to explicit deterministic sandbox
targets and passed through the real universal PRE rail:

```text
ActionCandidate
→ WorldActionRequest
→ exact HumanApproval
→ WORLD_ACTION_PRE
→ KX108 ALLOW
```

For both:

```text
egress_allowed=false
world_action_runtime_activated=false
decision_authority=KX108_ONLY
```

No connector executor is invoked.

## Functional proof

Workflow:
`37631556953`

Result:
`79 passed in 2.20s`

## Next unresolved boundary

`ENTERPRISE_OFFICE_FULL_LOOP_E2E_V0`

Next scope:

```text
projected ActionCandidate
→ explicit sandbox target
→ WorldActionRequest
→ HumanApproval
→ KX108
→ activation policy
→ LiveSovereignTicket
→ bounded sandbox executor
→ receipt
→ replay
```

No real external provider is required for that next proof.
