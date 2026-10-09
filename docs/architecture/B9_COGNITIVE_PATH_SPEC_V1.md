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

## 1. COGNITIVE PATH
A `CognitivePath` is an ordered record of a cognitive route.
- Identity depends on semantic order (unlike B8 C1 unordered refs).

## 2. FAILED PATH
A `FailedPath` indicates that a specific sequence of steps did not reach a valid or true conclusion.
- Failure is contextual to the exact route, not a permanent prohibition against the steps themselves.
- Reason semantics MUST reuse B8 reason codes where possible.
- An UNKNOWN outcome is distinct from FALSE or FAILED. A route ending in UNKNOWN is preserved as UNKNOWN.

## 3. PATH HISTORY
`PathHistory` is an append-only collection of outcomes.
- It does NOT automatically choose paths.
- It does NOT grant execution authority.

## 4. BOUNDARIES
- B9 MUST NOT write to durable memory (B10).
- B9 MUST NOT promote or verify claims (B8).
- B9 MUST NOT redefine cognitive roles (B7).
- B9 MUST NOT emit actions (KX108).
