# BRODY GRAPHITI CANDIDATE PREP FROM POST HUMAN TRIAGE READONLY V1

## Purpose

Prepare Graphiti candidates from post-human KEEP records.

Input:

- BRODY_POST_HUMAN_MEMORY_CANDIDATES_READONLY.jsonl

Output:

- BRODY_GRAPHITI_CANDIDATES_FROM_POST_HUMAN_TRIAGE_READONLY.jsonl

## Boundary

- Graphiti candidate prep: true
- Post-human KEEP only: true
- Graphiti write: false
- Memory intake: false
- Memory decision: false
- Emits ACT: false
- Emits verdict: false
- Kernel mutation: false
- X108 runtime binding: false
- X108 merge: false

## Meaning

This prepares candidates.
It does not import them.
It does not write Graphiti.
It does not canonize memory.
