# BRODY API MEMORY OPERATOR REPLAY API FIX V2 READONLY V1

## Purpose

Fix-forward after 2fa2f37.

The previous API fix artifact was committed but invalid as API evidence because endpoint capture was zero.

This V2 captures real readonly endpoint JSON from the live ObsidiaShell gateway on port 8011.

## Validated

- API gateway 8011 live.
- 10 readonly GET endpoints captured.
- Frozen Graphiti status captured.
- Memory/context endpoints captured.
- Search endpoints captured.
- No Graphiti decision.
- No kernel decision.
- No live Neo4j dependency accepted.
- erify_all.py remains PASS.
- X108 repo remains clean before commit.

## Boundary

- Brody did not execute API calls.
- Operator script executed readonly GET calls.
- Brody did not authorize.
- Brody did not decide.
- Brody did not emit ACT.
- Brody did not emit verdict.
- Brody did not write Graphiti.
- Brody did not write Neo4j.
- Brody did not ingest memory.
- Brody did not mutate kernel.
- Brody did not bind X108 runtime.
- Brody did not merge X108.

## Status

BRODY_API_MEMORY_OPERATOR_REPLAY_API_FIX_V2_READONLY_V1_PASS
