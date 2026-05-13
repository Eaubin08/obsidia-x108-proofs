# BRODY GRAPHITI IMPORT DRY RUN FROM POST HUMAN PREP READONLY V1

## Purpose

Prepare a dry-run import plan from the 29 post-human Graphiti candidates.

Input:

- BRODY_GRAPHITI_CANDIDATES_FROM_POST_HUMAN_TRIAGE_READONLY.jsonl

Output:

- BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_PLAN.jsonl

## Boundary

- Graphiti import dry-run: true
- Dry run: true
- Manual apply required: true
- Graphiti write: false
- Neo4j write executed: false
- Memory intake: false
- Memory decision: false
- Emits ACT: false
- Emits verdict: false
- Kernel mutation: false
- X108 runtime binding: false
- X108 merge: false

## Meaning

This plans what could be imported.
It does not import.
It does not write Graphiti.
It does not canonize memory.
