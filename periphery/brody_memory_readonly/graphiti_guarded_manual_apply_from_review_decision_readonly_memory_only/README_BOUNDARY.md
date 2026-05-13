# BRODY GRAPHITI GUARDED MANUAL APPLY FROM REVIEW DECISION READONLY MEMORY ONLY V1

## Purpose

Take approved Graphiti import candidates after human review decision apply.

Prepare a guarded manual apply layer.

## Modes

### Dry-run

Default mode.

- Builds manual apply plan
- Writes local audit files
- Does not write Neo4j
- Does not write Graphiti
- Does not mutate X108

### Apply

Only with explicit human token:

BRODY_GRAPHITI_MANUAL_APPLY_REVIEW_DECISION_MEMORY_ONLY

Apply writes memory-only `Document` nodes to Neo4j/Graphiti surface.

## Boundary

- Memory only: true
- Manual token required: true
- Kernel mutation: false
- X108 runtime binding: false
- X108 merge: false
- Emits ACT: false
- Emits verdict: false
- Decision authority: KX108_ONLY
