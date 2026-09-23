# BRODY_PHASE_4_VALIDATION_REPORT

Status: PASS_WITH_GRAPHITI_STUB_PENDING

## Scope

This phase validates that the stabilized repo preserves Brody capabilities and connectors without patching runtime application code.

## Results

### Routes

PASS.

Validated routes include:

- /api/brody/chat
- /api/context/from-message
- /api/memory
- /api/memory/status
- /api/memory/sources
- /api/memory/candidates
- /api/memory/candidate/from-message
- /api/memory/candidate-ledger
- /api/memory/promotion-policy
- /api/graphiti/status
- /api/graphiti/context
- /api/graphiti/search
- /api/graphiti/metrics
- /api/graphiti/readiness
- /api/periphery/brody/context-query
- /api/periphery/brody/language-route
- /api/periphery/brody/double-brain-route
- /api/periphery/brody/diffusion-mix

### Capabilities

PASS.

Validated cases:

- francais_utf8
- english_understanding
- code_debug
- boundary

Result:

BRODY_CAPABILITY_SMOKE_OK

### Pytest

PASS.

Result:

6 passed.

### UTF-8

PASS.

Diagnosis:

- curl.exe raw UTF-8 decoding: OK
- python requests raw UTF-8 decoding: OK
- Invoke-WebRequest / Invoke-RestMethod: false positive mojibake

Decision:

No Brody runtime UTF-8 patch required.

The smoke script was adjusted to use curl.exe + raw UTF-8 decoding.

### Boundary

PASS.

Required invariants preserved:

- readonly = true
- advisory_only = true
- emits_act = false
- emits_verdict = false
- decision_authority = KX108_ONLY
- memory_write = false
- kernel_mutation = false
- graphiti_write = false

### Connectors

PARTIAL PASS.

Memory connector:

- /api/memory/status = REAL_BACKEND
- readonly candidate mode active
- auto promotion disabled
- human review required

Graphiti connector:

- /api/graphiti/status = BACKEND_STUB
- graphiti_status = FROZEN_READONLY
- ready = false
- missing = graphiti_v20_db, graphiti_http

Decision:

Graphiti live reconnect remains pending.

## Files created in this phase

Scripts:

- scripts/run_brody_api_local.ps1
- scripts/smoke_brody_routes.ps1
- scripts/smoke_brody_capabilities.ps1
- scripts/run_brody_terminal.ps1
- scripts/run_obsidia_workbench_local.ps1
- scripts/smoke_brody_connectors_status.ps1

Tests:

- tests/api/test_brody_routes_registered.py
- tests/api/test_brody_capabilities_preserved.py
- tests/api/test_brody_boundary_readonly.py

Docs:

- docs/runtime/BRODY_RECONNECT_MAP.md
- docs/runtime/BRODY_CAPABILITY_CONNECTOR_PRESERVATION.md
- docs/runtime/SHELL_GRAPHITI_V20_REFERENCE.md
- docs/runtime/BRODY_PHASE_4_VALIDATION_REPORT.md

## Not committed

- _BRODY_RECONNECT_WORK/
- raw smoke outputs
- backup files
- raw audit CSVs
- node_modules
- .venv
- records
- secrets

## Next phase

PHASE 5 — Graphiti V20 / ObsidiaShell 8011 readonly reconnect.

Goal:

- keep Brody runtime unchanged
- reconnect Graphiti V20 readonly context if available
- keep Graphiti as context provider only
- no Graphiti decision
- no kernel mutation
- no X108 mutation
