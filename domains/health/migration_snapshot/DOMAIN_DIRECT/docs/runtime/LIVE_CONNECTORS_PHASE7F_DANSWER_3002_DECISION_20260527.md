# LIVE_CONNECTORS_PHASE7F_DANSWER_3002_DECISION_20260527

Status: OUT_OF_SCOPE_FOR_CURRENT_BRODY_FLOW

## Scope

Close Danswer/Onyx/3002 decision for the current Brody live connector sequence.

## Evidence

- Port 3002 is down.
- http://127.0.0.1:3002/health is down.
- No active Docker service exposes port 3002.
- Current validated critical flow does not use Danswer/Onyx.
- Existing 3002 references are historical docs, prior diagnostics, local audit records, or false-positive numeric/hash matches.

## Decision

Danswer/Onyx on port 3002 is not required for the validated Brody live path.

Current critical flow remains:

Workbench 5173 -> Brody API 8012 -> Graphiti V20 readonly proxy -> ObsidiaShell 8011.

## Preserved capabilities

The current Brody live stack preserves:

- Brody French UTF-8 responses
- English understanding
- code/debug path
- terminal path
- Workbench UI path
- Graphiti V20 readonly context
- Memory status/sources
- KX108_ONLY boundary

## Position

Danswer/Onyx may remain a future optional knowledge connector.

It receives no decision authority and is not required for the current live freeze.

## Not changed

- No service started.
- No Docker mutation.
- No runtime patch.
- No kernel mutation.
- No X108 mutation.
- No Graphiti write.
- No Neo4j write.
- No secrets.

## Boundary

KX108_ONLY remains sole decision authority.

Danswer/Onyx receives no decision authority.