# BRODY_PHASE12E4_B_DOMAIN_RACCORD_READONLY_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Add readonly domain raccords for Brody semantic adaptation after Phase 12E4-A2/A3.

## Problem

Phase 12E4-A3 proved:

- domains_total=9
- domains_present_and_active=6
- domains_repo_present_but_not_active=3
- domains_repo_present_but_not_live_visible=7

Repo-present but not active:

- THERMODYNAMICS
- ENERGY_SIGMA
- ANTI_MISMATCH

Repo-present but not live-visible:

- FRICTION
- THERMODYNAMICS
- COHERENCE
- ENERGY_SIGMA
- ANTI_MISMATCH
- MEMORY_WRITE_CANON_FREEZE
- NEGATION_GUARD

## Patched

- apps/obsidia_api/brody_domain_raccord_adapter.py
- apps/obsidia_api/brody_machination_composer.py
- apps/obsidia_api/brody_true_voice_adapter.py

## Added

- readonly domain raccord adapter
- friction recognition
- thermodynamics recognition
- energy/sigma recognition
- anti-mismatch recognition
- regime recognition
- memory write / canon / Graphiti write boundary
- negation guard for "sans remplacer X108" / "sans modifier kernel"
- true voice domain_raccord_snapshot
- machination support_summary domain_raccord_snapshot

## Preserved

- readonly=true
- advisory_only=true
- context_signal_only=true
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- emits_act=false
- emits_verdict=false
- kernel_mutation=false
- x108_mutation=false
- decision_authority=KX108_ONLY

## Validation

- BOM=false
- py_compile passed
- targeted pytest passed
- live domain raccord check passed
- terminal checks passed

## Decision

Patch connects already-present Obsidia domains to Brody voice/machination without giving them decision authority.
