# BRODY API BRIDGE BUILD EPOCH OPEN READONLY V1

## Purpose

Proof-side marker opening a mutable candidate build epoch after a clean X108 proof freeze.

This does not activate runtime.
This does not enable external access.
This does not call network.
This does not call APIs.
This does not scrape.
This does not print secrets.
This does not write Graphiti.
This does not ingest memory.
This does not bind X108 runtime.
This does not merge X108.

## Current state

- build_epoch_open: true
- mutable_candidate_build_allowed: true
- proof_freeze_remains_valid: true
- rerun_live_drift_guard_before_claim: true
- runtime_enabled: false
- external_access_enabled: false
- decision_authority: KX108_ONLY

## Boundary

- MEMORY_DECISION=false
- ALLOWED_TO_DECIDE=false
- EMITS_ACT=false
- EMITS_VERDICT=false
- DECISION_AUTHORITY=KX108_ONLY
- KERNEL_MUTATION=false
- X108_RUNTIME_BINDING=false
- X108_MERGE=false

## Rule

Candidate build can continue.

Before any new claim, freeze, proof promotion, or X108 rapatriement, rerun the live drift guard.
