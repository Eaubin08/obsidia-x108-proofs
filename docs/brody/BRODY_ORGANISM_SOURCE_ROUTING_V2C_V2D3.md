# Brody Organism Source Routing — V2C / V2D3

Status: VALIDATED_RUNTIME_PASS

## Scope

This commit stabilizes Brody source-pack routing and voice synthesis for organism-style source families.

## Validated layers

### V2C — Organ routing

- gencoin -> GENCOIN_ORGAN
- arbres cognitifs -> COGNITIVE_TREES_ORGAN
- paquets manquants -> GAP_READINESS_ORGAN
- preuves disponibles -> PROOF_OS3_LEAN_ORGAN

### V2D3 — Organ voice cleanup

Obsolete V1 fallback phrases were removed from the active multiline angle branches.

Validated removals:

- no generic COGNITIVE_REINTEGRATION fallback for Gencoin
- no OS_TRAD_REVERSE_OS placeholder fallback for cognitive trees
- no missing gap/readiness matrix fallback
- no generic receipts-only fallback for proofs

## Runtime markers

- http_ok=true
- organism_active=true
- starts_synthesis=true
- has_obsolete_phrase=false
- has_organ_voice=true
- readonly=true
- emits_act=false
- memory_write=false
- pass=true

## Boundary

- decision_authority=KX108_ONLY
- readonly=true
- advisory_only=true
- emits_act=false
- emits_verdict=false
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- kernel_mutation=false
- x108_mutation=false
- no UI patch

## Interpretation

Brody now answers through functional organs instead of flat generic source families.

Hierarchy preserved:

1. X108 decides.
2. OS3 / Proof proves.
3. Graphiti / Memory exposes readonly context.
4. Source-pack hydrates source material.
5. Brody synthesizes in readonly.
6. Peripheral organs remain consultative and non-sovereign.

## Known excluded state

- V2D route-final cleanup was invalid and must not be used.
- V2D2 was diagnostic but not runtime-valid.
