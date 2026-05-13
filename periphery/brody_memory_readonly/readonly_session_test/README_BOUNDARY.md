# BRODY READONLY SESSION TEST V1

## Purpose

Validate that a Brody session can reopen from readonly memory artifacts without querying or writing Graphiti.

## Boundary

- File read only: true
- Graphiti query read: false
- Graphiti write: false
- Neo4j write: false
- Memory intake: false
- Memory decision: false
- Emits ACT: false
- Emits verdict: false
- Kernel mutation: false
- X108 runtime binding: false
- X108 merge: false

## Inputs

- Memory scheduler validation
- Session reopen loop validation
- Memory readonly micro smoke validation
- Memory pipeline V2 close report validation

## Next

COMMIT_BRODY_READONLY_SESSION_TEST_V1_THEN_DECIDE_BRODY_AGENT_TEST_OR_SCHEDULER_V2
