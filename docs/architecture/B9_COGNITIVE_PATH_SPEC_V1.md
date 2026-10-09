# B9 COGNITIVE PATH SPECIFICATION V1

## 0. PURPOSE
B9 represents HOW cognition travelled through a problem. It does NOT represent:
- truth
- knowledge promotion
- world state
- durable memory
- decision authority
- action authorization

Freeze:
COGNITIVE_PATH != TRUTH
COGNITIVE_PATH != DECISION
COGNITIVE_PATH != ACTION_AUTHORITY
FAILED_PATH != FALSE
FAILED_PATH != FORBIDDEN_FOREVER
PAST_SUCCESS != CURRENT_AUTHORITY

## 1. COGNITIVE PATH & IDENTITY
A `CognitivePath` is an ordered, bounded cognitive route.
Identity is deterministic and explicitly commits to:
- problem / subject
- goal / scope
- ordered canonical steps
- canonical step content

Identity must reuse canonical serialization/hash primitives conceptually. 
Freeze:
- NO random UUID as semantic identity.
- NO wall-clock timestamp as semantic identity.
- NO serialization order masquerading as causal meaning.
- PATH_STEP_ORDER_IS_SEMANTIC = YES (A → B → C is NOT A → C → B).

## 2. FAILED PATH
A `FailedPath` indicates that a specific sequence of steps did not reach a valid or true conclusion under a specific context.
- Failure is contextual to the exact route, not a permanent prohibition.
- Reason semantics must reuse B8 reason codes where possible.
- logical contradiction, missing evidence, temporal indeterminacy, verification failure, runtime/tool failure, authority refusal, budget/timebox stop, unknown/unresolved are distinguished conceptually.

## 3. PATH HISTORY
`PathHistory` is an append-only collection/history of path outcomes.
- COMPLETED_PATH_MUTATION = FORBIDDEN.
- Corrections/supersession must produce new objects/relations rather than historical mutation.

## 4. RETRYABILITY
Retryability is defined separately from path status using a minimal classification:
- `RETRYABLE`: known change in inputs/context/prerequisites may justify another attempt.
- `NON_RETRYABLE_UNDER_CURRENT_CONTRACT`: current contract/context gives no valid retry route.
- `UNKNOWN`: insufficient information to classify retryability.

Freeze:
- `NON_RETRYABLE_UNDER_CURRENT_CONTRACT != NEVER_RETRY`
- `FAILED_PATH != PERMANENT_PROHIBITION`
No retry classification creates authority or automatic scheduling.

## 5. FAILURE / RETRY INTERACTION
FailedPath preserves:
- exact context
- exact terminal reason
- retryability classification if known
- relevant dependency/evidence refs
but must not reinterpret failure globally.

Examples:
- MISSING_EVIDENCE → may be RETRYABLE
- TEMPORAL_INDETERMINACY → may become RETRYABLE when comparability changes
- AUTHORITY_REFUSAL → cannot be bypassed merely because an older path succeeded
- TOOL_OR_RUNTIME_FAILURE → route failure, not semantic falsehood
- UNKNOWN_OR_UNRESOLVED → UNKNOWN preserved

Do not introduce B8 truth semantics.

## 6. STATUS MODEL
B9 requires clear distinction between the semantics of:
- `IN_PROGRESS`
- `SUCCEEDED`
- `FAILED`
- `HELD`
- `ABORTED`

Freeze:
- HELD != FAILED
- FAILED != FALSE
- SUCCEEDED != TRUE
- UNKNOWN != FAILED
- UNKNOWN != FALSE

## 7. REPLAY
Replay reconstructs/inspects a path.
- `REPLAY_PATH != AUTHORIZE_PATH`
- No automatic ACT or tools execution during replay.

## 8. BOUNDARIES
### B7 BOUNDARY
B7 owns cognitive role definitions. B9 merely records sequences/routes involving those roles.
B9 MUST NOT redefine UNDERSTANDER, INVESTIGATOR, RESOLVER, CRITIC, TRANSLATOR, COMPARATOR, BUILDER_PROPOSER.

### B8 BOUNDARY
B9 cannot promote knowledge, verify truth, change KnowledgeRecord state, reinterpret B8 promotion, or mutate B8 history.
PATH_SUCCESS != KNOWLEDGE_PROMOTION
PATH_FAILURE != KNOWLEDGE_REJECTION

### B10 BOUNDARY
B9 MUST NOT write to persistent cross-session memory (B10).
B9_DURABLE_MEMORY_WRITE = NO
B9_NATIVE_MEMORY_WRITE = NO
B9_GRAPHITI_WRITE = NO

### AUTHORITY BOUNDARY
B9_AUTHORITY = NONE.
No KERNEL_MUTATION, MEMORY_WRITE, BINDER_MUTATION, or KX108_MUTATION. EMITS_ACT = NO.

## 9. EXPLICIT FUTURE RED CONTRACT
B9 V1 — FUTURE RED CONTRACT
Define all cases explicitly.

- **B9-R1**: deterministic exact identity. Given the same problem/subject, goal/scope, ordered canonical steps, then path_id is identical.
- **B9-R2**: order participates in identity. Same steps with different order (A→B→C vs A→C→B) must produce different path identities.
- **B9-R3**: completed path immutable. After terminal status (SUCCEEDED, FAILED, HELD, ABORTED), canonical path content cannot be mutated in place.
- **B9-R4**: failed path preserves reason/context.
- **B9-R5**: failed path not permanent prohibition.
- **B9-R6**: successful path grants no authority.
- **B9-R7**: PathHistory append-only.
- **B9-R8**: successful + failed alternatives coexist.
- **B9-R9**: UNKNOWN not collapsed to FAILED/FALSE.
- **B9-R10**: B7 role refs preserved.
- **B9-R11**: B8 state not mutated.
- **B9-R12**: no durable memory writes.
- **B9-R13**: replay does not ACT.
- **B9-R14**: path order participates in identity.
- **B9-R15**: same inputs but different cognitive route → distinct path.
