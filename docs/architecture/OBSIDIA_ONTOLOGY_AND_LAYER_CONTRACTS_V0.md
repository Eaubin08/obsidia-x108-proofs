# OBSIDIA_ONTOLOGY_AND_LAYER_CONTRACTS_V0

Status: DOCTRINE CHECKPOINT
Date: 2026-10-02
Scope: ontology, layer boundaries, information status, future contracts
Implementation status: doctrine only unless explicitly marked already enforced

## Constitutional invariants

1. Each layer speaks its own language.
2. Translation between layers is explicit; layers are not fused by default.
3. Information that cannot be translated must not silently disappear.
4. Every information object preserves its status.
5. DATA != EXPERIENCE != LEARNING != KNOWLEDGE != MEMORY.
6. MEMORY != COGNITION.
7. COGNITION != DATA.
8. INTELLIGENCE != AUTHORITY.
9. CAPABILITY != PERMISSION.
10. KERNEL remains domain/world agnostic.
11. WORLD_STATE != MEMORY.
12. OBSERVATION != TRUTH.
13. EXPERIENCE != GENERAL TRUTH.
14. PROPOSAL != DECISION.
15. DECISION != ACTION.
16. Authorized ACTION must remain linked to PROOF.

## Canonical role boundaries

DATA
- incoming or available informational material
- does not become truth merely by existing

EXPERIENCE
- what occurred in an interaction with a domain, environment, tool, or world
- does not automatically become knowledge

LEARNING
- extraction from experience after processing, confrontation, audit, or validation
- may result in rejection, uncertainty, or a knowledge candidate

KNOWLEDGE
- sufficiently established material that may be exploited as knowledge
- promotion must be explicit; never automatic from raw experience

MEMORY
- continuity, context, recall
- re-injects relevant past context
- never becomes decision authority

COGNITION
- mechanisms that process, relate, infer, select, solve, explore, and propose
- may increase in effective capability without acquiring more authority

WORLD_STATE(t)
- representation of what is considered present/relevant in the world at time t
- distinct from memory and from general knowledge

KERNEL / KX108
- evaluates canonical structure
- remains agnostic to domain/world semantics
- decision authority remains KX108_ONLY

## Functional model V0

WORLD
-> DATA / OBSERVATIONS
-> INTERFACES / TRANSLATIONS
-> LAYER-SPECIFIC REPRESENTATIONS
-> MECHANISMS
-> EXPERIENCE
-> AUDIT / CONFRONTATION / VALIDATION
-> VALIDATED LEARNING
-> EXPLOITABLE KNOWLEDGE

MEMORY is transversal context, not a mandatory serial stage.

This is a functional model, not a claim that every object must traverse every stage.

## Translation doctrine

Future inter-layer contracts should preserve, at minimum:
- provenance
- explicit unknowns
- ambiguity
- required distinctions
- conservation status
- translation success/failure status

Candidate future fields such as source_language, target_language, preserved_fields,
lost_fields, confidence, and translation_status are proposals, not yet constitutional schema.

## Views are projections, not ownership boundaries

OBSIDIA MONDE
- where Obsidia lives / spatial-existential representation

WORKSPACE
- where the human works / operational projection

POKEMON VIEW
- where agents live/work visually / social-agent projection

CLI
- transversal control/access surface

These views may reference the same underlying objects. They must not absorb or redefine
the ownership semantics of memory, knowledge, agents, proofs, repositories, or WorldState.

## World / physical doctrine

- GPS != physical understanding.
- GPS/Defense contributes provenance, localization, Reality Gate inputs, and partial world state.
- WorldState(t) is a future important object, not a G5 requirement.
- Principle: model the determinable to isolate the indeterminable.
- Do not inject a general world model into KX108.

## Learning doctrine

Accepted:
- experiential learning does not require, by default, mutation of the core mechanism
- stable mechanisms + growing validated experience can yield growing effective capability
- experience -> knowledge requires explicit promotion and validation

Not accepted as universal law:
- that every Obsidia mechanism must remain permanently immutable

## R&D / HOLD

Not current runtime contracts:
- One Birth / single continuous identity
- World Foundry as school + workshop
- general physical world model
- image/video as world observations
- complete Brody identity continuity across engine migration
- advanced VTerritory ontology
- general experience-to-knowledge promotion engine

## SENS boundary

This doctrine does NOT reopen or expand the current SENS M8 scope.

Current SENS obligation remains bounded:
- preserve semantic information inside its scope
- represent unanalyzed required content explicitly
- fail closed on silent semantic loss

The general law "each layer speaks its language" explains the direction of SENS but
does not require SENS to implement the entire ontology.

## G5 boundary

G5 remains strictly:
APPLY_PATCH -> proof -> governed rollback -> drift guard -> human confirmation -> exact restore -> receipt

No WorldState, education, World Foundry, Brody identity, Pokemon View, VTerritory,
new memory system, or new cognition engine is to be added to G5.

## Status matrix

NOW / CONSTITUTION
- language-per-layer
- no silent translation loss
- information status preservation
- data/experience/learning/knowledge/memory separation
- memory/cognition separation
- cognition/data separation
- intelligence/authority separation
- capability/permission separation
- kernel world/domain agnosticism
- WorldState/memory separation
- observation/truth separation
- experience/general-truth separation
- proposal/decision/action separation
- action/proof linkage

LATER / CONTRACTS
- inter-layer translation contracts
- explicit information status types
- experience -> knowledge promotion
- WorldState(t)
- validated experiential learning
- Monde / Workspace / Pokemon interfaces

R&D / HOLD
- One Birth
- World Foundry / education
- general physical world model
- image/video world observation
- full Brody continuity
- advanced VTerritory

## Final rule

Do not ask one layer to guarantee what another layer can guarantee more cleanly.
