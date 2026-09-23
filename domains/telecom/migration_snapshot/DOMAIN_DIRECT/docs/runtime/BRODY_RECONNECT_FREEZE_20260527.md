# BRODY_RECONNECT_FREEZE_20260527

Status: READY_FOR_SELECTIVE_COMMIT

## Freeze lineage

Previous freeze layer:

- Public repo cleanup / status/doc surface freeze already on main.
- Public docs aligned before Brody reconnect.
- Do not rewrite history.
- Do not reset.
- Do not merge old local repo over target.

Current freeze layer:

- Brody runtime/capability/connectors validation.
- Graphiti V20 readonly proxy from Target 8012 to ObsidiaShell 8011.
- Tests and smoke scripts added.
- Runtime Brody core not patched.
- Graphiti route patched only as readonly proxy/fallback.

## Current validation evidence

Brody capability smoke:

- francais_utf8: PASS
- english_understanding: PASS
- code_debug: PASS
- boundary: PASS
- BRODY_CAPABILITY_SMOKE_OK

Pytest:

- 9 passed

Graphiti V20 proxy smoke:

- GRAPHITI_V20_PROXY_SMOKE_DONE

Graphiti V20 proxy status:

- source = GRAPHITI_V20_HTTP
- graphiti_status = FROZEN_READONLY
- entity_count = 167
- relation_count = 477
- indexed_episodes = 20
- failed_episodes = 0
- live_neo4j_dependency = false
- x108_merge_status = NOT_MERGED
- commit_status = LOCAL_ONLY
- proxy_source = GRAPHITI_V20_HTTP

## Preserved Brody surface

This freeze preserves:

- French UTF-8 response
- English understanding
- Code/debug answer path
- Terminal client path
- Brody route registration
- Memory connector routes
- Graphiti V20 readonly connector
- UI launch helper
- X108 readonly boundary
- KX108_ONLY authority
- No ACT / no verdict / no mutation

## Boundary invariants

- readonly = true
- advisory_only = true
- emits_act = false
- emits_verdict = false
- decision_authority = KX108_ONLY
- memory_write = false
- kernel_mutation = false
- x108_mutation = false
- graphiti_write = false
- neo4j_write = false
- real_action = false

## Important limitation

Graphiti query:

- /api/graphiti/context?q=Brody&limit=5

returns count = 0 because the frozen V20 corpus does not currently contain Brody entity/relation material.

This is not a proxy failure.

Known useful Graphiti V20 query coverage exists for:

- X-108
- CANON
- Kernel
- Proof
- Freeze

## Safe files included in this freeze

See manifest:

- docs/runtime/BRODY_RECONNECT_FREEZE_20260527_MANIFEST_SHA256.txt

## Explicitly excluded from commit

- _BRODY_RECONNECT_WORK/
- raw smoke outputs
- raw audit CSVs
- backup files
- node_modules/
- .venv/
- venv/
- records/
- SESSION_LEDGER raw bulk
- SESSION_INDEX raw bulk
- real .env files
- secrets/tokens/API keys

## Decision

This freeze is accepted as the Brody reconnect freeze candidate.

Commit must be selective.

No git add .
