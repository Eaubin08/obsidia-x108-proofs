# BRODY_PHASE9B1_OS_TRAD_IR_REVERSE_ROUTE_CONTRACT_20260527

Status: CONTRACT_ONLY_NO_PATCH

## Scope

Define the backend route contract for OS Trad / IR Candidate / OS Reverse before implementation.

This follows Phase 9B0, which validated terminal, UI, API, periphery, 34-tree, memory-world, Brody routing, diffusion, context, and Graphiti readonly surfaces.

## Current validated surfaces

Terminal:
- tools/brody_chat.py
- scripts/run_brody_terminal.ps1
- scripts/smoke_brody_capabilities.ps1

UI / Workbench:
- osTradPipeline.ts
- irCandidateBuilder.ts
- osReverseProjection.ts
- brodyResponseComposer.ts
- obsidiaClient.ts
- App.tsx

API / Backend:
- /api/brody/chat
- /api/translation/trace
- /api/memory/status
- /api/graphiti/status

Periphery / Context:
- /api/periphery/cognitive/trees
- /api/periphery/cognitive/trees/{tree_id}
- /api/periphery/cognitive/trees/domain/{domain}
- /api/periphery/cognitive/memory-world-map
- /api/periphery/context/build
- /api/periphery/context/ingress
- /api/periphery/brody/language-route
- /api/periphery/brody/context-query
- /api/periphery/brody/double-brain-route
- /api/periphery/brody/diffusion-mix
- /api/periphery/graphiti/context-adapt

## Missing dedicated backend routes

- POST /api/os-trad/translate
- POST /api/ir/candidate
- POST /api/os-reverse/project

## Route 1 — POST /api/os-trad/translate

Purpose: translate user input into a readonly structural language packet.

Required input:
- text
- language = auto/fr/en
- session_id optional
- include_context optional
- include_tree_context optional
- include_graphiti_context optional

Required output:
- readonly=true
- advisory_only=true
- emits_act=false
- emits_verdict=false
- decision_authority=KX108_ONLY
- memory_write=false
- graphiti_write=false
- kernel_mutation=false
- x108_mutation=false
- real_action=false
- source=REAL_BACKEND
- detected_language
- alphabet_units
- constraints
- risk_flags
- tree_context optional
- graphiti_context optional
- trace

Binding sources:
- periphery/language/language_router.py
- Workbench symbolicAlphabet.ts behavior
- /api/periphery/brody/language-route
- optional /api/periphery/cognitive/trees
- optional /api/periphery/graphiti/context-adapt

## Route 2 — POST /api/ir/candidate

Purpose: build a non-sovereign IR candidate from text, alphabet units, and optional context.

Required input:
- text
- language = auto/fr/en
- alphabet_units optional
- tree_context optional
- memory_context optional
- graphiti_context optional
- session_id optional

Required output:
- readonly=true
- advisory_only=true
- allowed_to_decide=false
- allowed_to_act=false
- emits_act=false
- emits_verdict=false
- decision_authority=KX108_ONLY
- memory_write=false
- graphiti_write=false
- kernel_mutation=false
- x108_mutation=false
- real_action=false
- source=REAL_BACKEND
- ir_candidate.intent
- ir_candidate.risk_flags
- ir_candidate.contradictions
- ir_candidate.constraints
- ir_candidate.tree_refs
- ir_candidate.memory_refs
- ir_candidate.graphiti_refs
- trace

Binding sources:
- Workbench irCandidateBuilder.ts behavior
- periphery/obsidia_ir.py to be completed or wrapped
- /api/periphery/context/build
- /api/periphery/context/validate
- /api/periphery/brody/context-query
- optional /api/periphery/cognitive/memory-world-map

## Route 3 — POST /api/os-reverse/project

Purpose: project an IR candidate back into a readonly response/projection packet.

Required input:
- text
- language = auto/fr/en
- ir_candidate
- audience = general/technical/business/operator
- format = short/structured/terminal/ui
- tree_context optional
- memory_context optional
- graphiti_context optional
- session_id optional

Required output:
- readonly=true
- advisory_only=true
- allowed_to_decide=false
- allowed_to_act=false
- emits_act=false
- emits_verdict=false
- decision_authority=KX108_ONLY
- memory_write=false
- graphiti_write=false
- kernel_mutation=false
- x108_mutation=false
- real_action=false
- source=REAL_BACKEND
- projection.language
- projection.response_mode=readonly_projection
- projection.summary
- projection.next_safe_step
- projection.boundary_notice=KX108_ONLY
- audience_projection
- format_projection
- tree_refs
- memory_refs
- graphiti_refs
- trace

Binding sources:
- Workbench osReverseProjection.ts behavior
- periphery/reverse_os/action_projection_readonly.py
- periphery/reverse_os/audience_projection.py
- periphery/reverse_os/format_projection.py
- /api/periphery/brody/double-brain-route
- /api/periphery/brody/diffusion-mix

## Integration rule

The new routes must not replace /api/brody/chat.

They must become supporting backend surfaces.

Canonical flow:

Terminal/UI
-> /api/brody/chat
-> optional /api/os-trad/translate
-> optional /api/ir/candidate
-> optional /api/os-reverse/project
-> periphery/context + tree34 + Graphiti readonly
-> KX108_ONLY boundary

## Non-negotiable invariants

Every route must return:

- readonly=true
- advisory_only=true
- emits_act=false
- emits_verdict=false
- allowed_to_decide=false where applicable
- allowed_to_act=false where applicable
- decision_authority=KX108_ONLY
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- kernel_mutation=false
- x108_mutation=false
- real_action=false
- source=REAL_BACKEND

## No direct imports yet

Do not import engine-candidate zip2 directly in Phase 9B-2.

Do not bind 34-tree package directly unless through already-live periphery endpoints.

Use live periphery surfaces first.

## Validation required after implementation

- OpenAPI contains all three routes.
- Each route returns HTTP 200 with minimal payload.
- Each route preserves KX108_ONLY invariants.
- Existing Brody capability smoke still passes.
- Existing Graphiti readonly proxy tests still pass.
- Existing Workbench build still passes.
- Terminal tools still target /api/brody/chat and remain valid.
- UI fallback remains intact.

## Boundary

- Contract only.
- No patch.
- No runtime mutation.
- No kernel mutation.
- No X108 mutation.
- No memory write.
- No Graphiti write.
- KX108_ONLY remains sole decision authority.
